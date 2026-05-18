import ply.yacc as yacc
from lexer import tokens, lexer, lexer_errors
import sys

# ══════════════════════════════════════════════════════════════════
#  TABLA DE SÍMBOLOS
# ══════════════════════════════════════════════════════════════════

class Symbol:
    def __init__(self, name, kind, typ, scope, line, initialized=False, params=None, return_type=None):
        self.name        = name          # str
        self.kind        = kind          # 'var' | 'const' | 'param' | 'function' | 'procedure' | 'type'
        self.type        = typ           # str  e.g. 'integer', 'real', 'boolean', 'char', 'string', 'array', …
        self.scope       = scope         # str  nombre del ámbito  ('global' o nombre del subprograma)
        self.line        = line          # int
        self.initialized = initialized  # bool
        self.params      = params or []  # lista de tipos de parámetros  (para funciones/procs)
        self.return_type = return_type   # str | None  (sólo para functions)

    def __repr__(self):
        return (f"Symbol({self.name!r}, kind={self.kind!r}, type={self.type!r}, "
                f"scope={self.scope!r}, line={self.line})")


class SymbolTable:
    def __init__(self):
        # Pila de ámbitos: cada entrada es dict  name → Symbol
        self._scopes = [{}]          # índice 0 = global
        self._scope_names = ['global']
        self._all_symbols = []       # registro histórico (para la impresión)

    # ── Gestión de ámbitos ───────────────────────────────────────

    def push_scope(self, name):
        self._scopes.append({})
        self._scope_names.append(name)

    def pop_scope(self):
        self._scopes.pop()
        self._scope_names.pop()

    @property
    def current_scope(self):
        return self._scope_names[-1]

    # ── Inserción ────────────────────────────────────────────────

    def insert(self, symbol: Symbol):
        """Inserta el símbolo en el ámbito actual.
           Devuelve True si es nuevo, False si ya existía (redefinición)."""
        top = self._scopes[-1]
        key = symbol.name.lower()
        if key in top:
            return False           # ya existía → error de redefinición
        top[key] = symbol
        self._all_symbols.append(symbol)
        return True

    # ── Búsqueda ─────────────────────────────────────────────────

    def lookup(self, name) -> Symbol | None:
        """Busca desde el ámbito más interno hacia afuera."""
        key = name.lower()
        for scope in reversed(self._scopes):
            if key in scope:
                return scope[key]
        return None

    def lookup_current(self, name) -> Symbol | None:
        key = name.lower()
        return self._scopes[-1].get(key)

    # ── Marca de inicialización ──────────────────────────────────

    def mark_initialized(self, name):
        key = name.lower()
        for scope in reversed(self._scopes):
            if key in scope:
                scope[key].initialized = True
                return

    # ── Impresión ────────────────────────────────────────────────

    def print_table(self):
        print()
        print("╔" + "═"*80 + "╗")
        print("║{:^80}║".format("TABLA DE SÍMBOLOS"))
        print("╠" + "═"*80 + "╣")
        header = f"  {'NOMBRE':<20} {'TIPO':<14} {'CATEGORÍA':<12} {'ÁMBITO':<16} {'LÍNEA':>5}  {'INIC':>5}"
        print("║" + header + "║")
        print("╠" + "═"*80 + "╣")

        # Agrupa por ámbito para mayor legibilidad
        scopes_seen = []
        by_scope: dict[str, list[Symbol]] = {}
        for s in self._all_symbols:
            if s.scope not in by_scope:
                by_scope[s.scope] = []
                scopes_seen.append(s.scope)
            by_scope[s.scope].append(s)

        for scope in scopes_seen:
            syms = by_scope[scope]
            label = f"  Ámbito: {scope}"
            print("║" + f"  {'─'*76}  " + "║")
            print("║" + f"  {label:<78}" + "║")
            for s in syms:
                init_str = "sí" if s.initialized else ("–" if s.kind in ('function','procedure','const','type') else "no")
                extra = ""
                if s.kind == 'function':
                    extra = f"→{s.return_type}"
                elif s.kind in ('function','procedure') and s.params:
                    extra = f"({','.join(s.params)})"
                tipo_str = (s.type + extra)[:13]
                row = f"  {s.name:<20} {tipo_str:<14} {s.kind:<12} {s.scope:<16} {s.line:>5}  {init_str:>5}"
                print("║" + row + "║")

        print("╚" + "═"*80 + "╝")


# ══════════════════════════════════════════════════════════════════
#  ANALIZADOR SEMÁNTICO
# ══════════════════════════════════════════════════════════════════

class SemanticAnalyzer:

    # Tipos escalares reconocidos
    SCALAR = {'integer', 'real', 'boolean', 'char', 'string'}
    NUMERIC = {'integer', 'real'}

    def __init__(self):
        self.table   = SymbolTable()
        self.errors  = []
        self.warnings = []
        # Para saber el subprograma actual y su tipo de retorno
        self._current_function = None

    # ── Reporte ──────────────────────────────────────────────────

    def error(self, line, msg):
        self.errors.append(f"  ERROR SEMÁNTICO (línea {line}): {msg}")

    def warning(self, line, msg):
        self.warnings.append(f"  ADVERTENCIA (línea {line}): {msg}")

    # ── Compatibilidad de tipos ───────────────────────────────────

    def compatible(self, t1, t2):
        """¿Se puede asignar / operar t2 → t1?"""
        if t1 is None or t2 is None:
            return True        # ya se reportó otro error antes
        t1, t2 = t1.lower(), t2.lower()
        if t1 == t2:
            return True
        # integer ↔ real son compatibles
        if {t1, t2} <= self.NUMERIC:
            return True
        return False

    def numeric_result(self, t1, t2):
        if t1 == 'real' or t2 == 'real':
            return 'real'
        return 'integer'

    # ════════════════════════════════════════════════════════════
    #  VISITA DEL ÁRBOL (el parser.py no construye AST explícito,
    #  así que reescribimos las acciones semánticas en este módulo
    #  redefiniendo las reglas gramaticales)
    # ════════════════════════════════════════════════════════════

    # Las funciones de regla retornan un "valor semántico":
    #   - Para expresiones/factores: el tipo como str  ('integer', 'real', …)
    #   - Para sentencias y partes estructurales: None

    # ── program ──────────────────────────────────────────────────

    def visit_program(self, name, block, line):
        pass   # el nombre del programa no se registra en tabla

    # ── Sección VAR ──────────────────────────────────────────────

    def visit_var_declaration(self, names, typ, line):
        for name in names:
            sym = Symbol(name, 'var', typ, self.table.current_scope, line)
            if not self.table.insert(sym):
                self.error(line, f"'{name}' ya fue declarado en este ámbito")

    # ── Sección CONST ─────────────────────────────────────────────

    def visit_const_def(self, name, typ, line):
        sym = Symbol(name, 'const', typ, self.table.current_scope, line, initialized=True)
        if not self.table.insert(sym):
            self.error(line, f"'{name}' ya fue declarado en este ámbito")

    # ── Declaración de FUNCTION ───────────────────────────────────

    def visit_function_decl_begin(self, name, params, return_type, line):
        """Registra la función en el ámbito padre y abre su propio ámbito."""
        param_types = [p[1] for p in params]  # [(nombre, tipo), ...]
        sym = Symbol(name, 'function', return_type,
                     self.table.current_scope, line,
                     initialized=True,
                     params=param_types,
                     return_type=return_type)
        if not self.table.insert(sym):
            self.error(line, f"'{name}' ya fue declarado en este ámbito")
        # Abre ámbito de la función
        self.table.push_scope(name)
        self._current_function = (name, return_type)
        # Registra parámetros dentro del nuevo ámbito
        for pname, ptype in params:
            psym = Symbol(pname, 'param', ptype, self.table.current_scope, line, initialized=True)
            if not self.table.insert(psym):
                self.error(line, f"Parámetro '{pname}' duplicado en '{name}'")

    def visit_function_decl_end(self):
        self.table.pop_scope()
        self._current_function = None

    # ── Declaración de PROCEDURE ──────────────────────────────────

    def visit_procedure_decl_begin(self, name, params, line):
        param_types = [p[1] for p in params]
        sym = Symbol(name, 'procedure', 'void',
                     self.table.current_scope, line,
                     initialized=True,
                     params=param_types)
        if not self.table.insert(sym):
            self.error(line, f"'{name}' ya fue declarado en este ámbito")
        self.table.push_scope(name)
        self._current_function = None
        for pname, ptype in params:
            psym = Symbol(pname, 'param', ptype, self.table.current_scope, line, initialized=True)
            if not self.table.insert(psym):
                self.error(line, f"Parámetro '{pname}' duplicado en '{name}'")

    def visit_procedure_decl_end(self):
        self.table.pop_scope()

    # ── Asignación ────────────────────────────────────────────────

    def visit_assignment(self, lhs_name, lhs_type, rhs_type, line):
        sym = self.table.lookup(lhs_name)
        if sym is None:
            self.error(line, f"'{lhs_name}' no fue declarado")
            return
        if sym.kind == 'const':
            self.error(line, f"No se puede asignar a la constante '{lhs_name}'")
            return
        if not self.compatible(sym.type, rhs_type):
            self.error(line, f"Incompatibilidad de tipos en asignación: "
                             f"'{lhs_name}' es '{sym.type}' pero se asigna '{rhs_type}'")
        self.table.mark_initialized(lhs_name)

    # ── Llamada a función / procedimiento ────────────────────────

    def visit_call(self, name, arg_types, line):
        """Verifica que el identificador exista y que el nº de args sea correcto."""
        sym = self.table.lookup(name)
        if sym is None:
            self.error(line, f"'{name}' no fue declarado")
            return None
        if sym.kind not in ('function', 'procedure'):
            # Podría ser un procedimiento built-in (writeln, readln, …)
            if name.lower() not in ('writeln', 'write', 'readln', 'read'):
                self.error(line, f"'{name}' no es una función ni un procedimiento")
            return sym.return_type if hasattr(sym, 'return_type') else None
        if len(arg_types) != len(sym.params):
            self.error(line, f"'{name}' espera {len(sym.params)} argumento(s), "
                             f"pero se proporcionaron {len(arg_types)}")
        else:
            for i, (at, pt) in enumerate(zip(arg_types, sym.params)):
                if not self.compatible(pt, at):
                    self.error(line, f"Argumento {i+1} de '{name}': "
                                     f"se esperaba '{pt}' pero se recibió '{at}'")
        return sym.return_type if sym.kind == 'function' else None

    # ── Uso de variable ───────────────────────────────────────────

    def visit_variable(self, name, line):
        sym = self.table.lookup(name)
        if sym is None:
            self.error(line, f"'{name}' no fue declarado")
            return None
        if sym.kind == 'var' and not sym.initialized:
            self.warning(line, f"'{name}' se usa sin haber sido inicializada")
        return sym.type

    # ── Lvalue (lado izquierdo de asignación) ─────────────────────

    def visit_lvalue(self, name, line):
        """Igual que visit_variable pero NO verifica inicialización."""
        sym = self.table.lookup(name)
        if sym is None:
            self.error(line, f"'{name}' no fue declarado")
            return None
        return sym.type

    # ── Operación binaria ─────────────────────────────────────────

    def visit_binop(self, op, t1, t2, line):
        if t1 is None or t2 is None:
            return None
        arith = {'+', '-', '*', '/', 'div', 'mod'}
        logic = {'and', 'or'}
        rel   = {'=', '<>', '<', '>', '<=', '>=', 'in'}

        if op in arith:
            if t1 not in self.NUMERIC or t2 not in self.NUMERIC:
                self.error(line, f"Operación aritmética '{op}' requiere operandos numéricos, "
                                 f"pero se tienen '{t1}' y '{t2}'")
                return None
            return self.numeric_result(t1, t2)

        if op in logic:
            if t1 != 'boolean' or t2 != 'boolean':
                self.error(line, f"Operación lógica '{op}' requiere booleanos, "
                                 f"pero se tienen '{t1}' y '{t2}'")
                return 'boolean'
            return 'boolean'

        if op in rel:
            if not self.compatible(t1, t2):
                self.error(line, f"Comparación '{op}' entre tipos incompatibles: "
                                 f"'{t1}' y '{t2}'")
            return 'boolean'

        return None

    # ── Impresión de resultados ───────────────────────────────────

    def report(self, total_lines):
        print()
        print("╔" + "═"*60 + "╗")
        print("║{:^60}║".format("ANÁLISIS SEMÁNTICO"))
        print("╚" + "═"*60 + "╝")

        if self.warnings:
            print(f"\n⚠  {len(self.warnings)} advertencia(s):")
            for w in self.warnings:
                print(w)

        if self.errors:
            print(f"\n✗  {len(self.errors)} error(es) semántico(s):")
            for e in self.errors:
                print(e)
        else:
            print(f"\n✔  Sin errores semánticos en {total_lines} líneas.")

        self.table.print_table()

# ══════════════════════════════════════════════════════════════════
#  PARSER CON ACCIONES SEMÁNTICAS
# ══════════════════════════════════════════════════════════════════

sem = SemanticAnalyzer()
syntax_errors = []

# ─── Programa ────────────────────────────────────────────────────

def p_program(p):
    'program : PROGRAM ID SEMICOLON block DOT'
    pass

# ─── Bloque ──────────────────────────────────────────────────────

def p_block(p):
    'block : label_part const_part type_part var_part subprogram_declarations compound_stmt'
    pass

# ─── Label (ignoramos semánticamente) ────────────────────────────

def p_label_part_1(p): 'label_part : LABEL label_list SEMICOLON'
def p_label_part_2(p): 'label_part : empty'
def p_label_list_1(p): 'label_list : label_list COMMA NUMBER'
def p_label_list_2(p): 'label_list : NUMBER'

# ─── Const ───────────────────────────────────────────────────────

def p_const_part_1(p): 'const_part : CONST const_list'
def p_const_part_2(p): 'const_part : empty'
def p_const_list_1(p): 'const_list : const_list const_def'
def p_const_list_2(p): 'const_list : const_def'

def p_const_def(p):
    'const_def : ID EQ literal SEMICOLON'
    typ = p[3] if p[3] else 'unknown'
    sem.visit_const_def(p[1], typ, p.lineno(1))

# ─── Type (registramos el alias, no verificamos en profundidad) ──

def p_type_part_1(p): 'type_part : TYPE type_list'
def p_type_part_2(p): 'type_part : empty'
def p_type_list_1(p): 'type_list : type_list type_def'
def p_type_list_2(p): 'type_list : type_def'

def p_type_def(p):
    'type_def : ID EQ type_specifier SEMICOLON'
    sym = Symbol(p[1], 'type', p[3] or 'unknown', sem.table.current_scope, p.lineno(1), initialized=True)
    if not sem.table.insert(sym):
        sem.error(p.lineno(1), f"'{p[1]}' ya fue declarado en este ámbito")

# ─── Var ─────────────────────────────────────────────────────────

def p_var_part_1(p): 'var_part : VAR var_declaration_list'
def p_var_part_2(p): 'var_part : empty'
def p_var_declaration_list_1(p): 'var_declaration_list : var_declaration_list var_declaration'
def p_var_declaration_list_2(p): 'var_declaration_list : var_declaration'

def p_var_declaration(p):
    'var_declaration : id_list COLON type_specifier SEMICOLON'
    names = p[1] if p[1] else []
    typ   = p[3] or 'unknown'
    sem.visit_var_declaration(names, typ, p.lineno(2))

def p_id_list_1(p):
    'id_list : id_list COMMA ID'
    p[0] = p[1] + [p[3]]

def p_id_list_2(p):
    'id_list : ID'
    p[0] = [p[1]]

# ─── Tipos ───────────────────────────────────────────────────────

def p_type_specifier_integer(p):
    'type_specifier : INTEGER'
    p[0] = 'integer'

def p_type_specifier_real(p):
    'type_specifier : REAL'
    p[0] = 'real'

def p_type_specifier_boolean(p):
    'type_specifier : BOOLEAN'
    p[0] = 'boolean'

def p_type_specifier_char(p):
    'type_specifier : CHAR'
    p[0] = 'char'

def p_type_specifier_string(p):
    'type_specifier : STRING'
    p[0] = 'string'

def p_type_specifier_array(p):
    'type_specifier : ARRAY LBR NUMBER RANGE NUMBER RBR OF type_specifier'
    p[0] = f'array[{p[3]}..{p[5]}] of {p[8]}'

def p_type_specifier_record(p):
    'type_specifier : RECORD field_list END'
    p[0] = 'record'

def p_type_specifier_set(p):
    'type_specifier : SET OF type_specifier'
    p[0] = f'set of {p[3]}'

def p_type_specifier_file(p):
    'type_specifier : FILE OF type_specifier'
    p[0] = f'file of {p[3]}'

def p_type_specifier_file_plain(p):
    'type_specifier : FILE'
    p[0] = 'file'

def p_type_specifier_packed(p):
    'type_specifier : PACKED type_specifier'
    p[0] = f'packed {p[2]}'

def p_type_specifier_id(p):
    'type_specifier : ID'
    # Tipo definido por el usuario – verificamos que exista
    sym = sem.table.lookup(p[1])
    if sym is None:
        sem.error(p.lineno(1), f"Tipo '{p[1]}' no declarado")
        p[0] = 'unknown'
    else:
        p[0] = sym.type

# ─── Campos de record ────────────────────────────────────────────

def p_field_list_1(p): 'field_list : field_list SEMICOLON field_declaration'
def p_field_list_2(p): 'field_list : field_declaration'
def p_field_list_3(p): 'field_list : empty'
def p_field_declaration(p): 'field_declaration : id_list COLON type_specifier'

# ─── Subprogramas ────────────────────────────────────────────────

def p_subprogram_declarations_1(p): 'subprogram_declarations : subprogram_declarations subprogram_declaration'
def p_subprogram_declarations_2(p): 'subprogram_declarations : empty'
def p_subprogram_declaration_function(p):  'subprogram_declaration : function_declaration'
def p_subprogram_declaration_procedure(p): 'subprogram_declaration : procedure_declaration'

# Se divide en _head y cuerpo para poder abrir el ámbito a tiempo

def p_function_head(p):
    'function_head : FUNCTION ID LPAR params RPAR COLON type_specifier SEMICOLON'
    params = p[4] or []
    sem.visit_function_decl_begin(p[2], params, p[7], p.lineno(1))
    p[0] = (p[2], p[7])   # (nombre, tipo-retorno)

def p_function_declaration(p):
    'function_declaration : function_head subblock SEMICOLON'
    sem.visit_function_decl_end()

def p_procedure_head(p):
    'procedure_head : PROCEDURE ID LPAR params RPAR SEMICOLON'
    params = p[4] or []
    sem.visit_procedure_decl_begin(p[2], params, p.lineno(1))
    p[0] = p[2]

def p_procedure_declaration(p):
    'procedure_declaration : procedure_head subblock SEMICOLON'
    sem.visit_procedure_decl_end()

def p_subblock(p):
    'subblock : label_part var_part compound_stmt'

# ─── Parámetros ──────────────────────────────────────────────────

def p_params_1(p):
    'params : param_list'
    p[0] = p[1]

def p_params_2(p):
    'params : empty'
    p[0] = []

def p_param_list_1(p):
    'param_list : param_list SEMICOLON param'
    p[0] = p[1] + p[3]

def p_param_list_2(p):
    'param_list : param'
    p[0] = p[1]

def p_param(p):
    'param : id_list COLON type_specifier'
    # Retorna lista de (nombre, tipo)
    p[0] = [(name, p[3]) for name in (p[1] or [])]

# ─── Sentencias ──────────────────────────────────────────────────

def p_compound_stmt(p):
    'compound_stmt : BEGIN statement_list END'

def p_statement_list_1(p):
    'statement_list : statement_list SEMICOLON statement'

def p_statement_list_2(p):
    'statement_list : statement'

def p_statement(p):
    '''statement : assignment_stmt
                 | compound_stmt
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | repeat_stmt
                 | case_stmt
                 | goto_stmt
                 | with_stmt
                 | labeled_stmt
                 | procedure_call_stmt
                 | empty
    '''

# ─── Asignación ──────────────────────────────────────────────────

def p_assignment_stmt(p):
    'assignment_stmt : lvalue ASSIGN expression'
    lhs_name, lhs_type = p[1]   # (nombre, tipo)
    rhs_type = p[3]
    if lhs_name:
        sem.visit_assignment(lhs_name, lhs_type, rhs_type, p.lineno(2))

# ─── Lvalue (lado izquierdo de asignación, no verifica inicialización) ──

def p_lvalue_simple(p):
    'lvalue : ID'
    typ = sem.visit_lvalue(p[1], p.lineno(1))
    p[0] = (p[1], typ)

def p_lvalue_array(p):
    'lvalue : ID LBR expression RBR'
    sym = sem.table.lookup(p[1])
    if sym is None:
        sem.error(p.lineno(1), f"'{p[1]}' no fue declarado")
        p[0] = (p[1], None)
    else:
        base = sym.type
        if 'of' in str(base):
            base = base.split('of')[-1].strip()
        p[0] = (p[1], base)

def p_lvalue_field(p):
    'lvalue : lvalue DOT ID'
    p[0] = (p[3], None)

# ─── if / while / for / repeat / case ────────────────────────────

def p_if_stmt_1(p):
    'if_stmt : IF expression THEN statement ELSE statement'
    if p[2] and p[2] != 'boolean':
        sem.error(p.lineno(1), f"La condición del IF debe ser booleana, se tiene '{p[2]}'")

def p_if_stmt_2(p):
    'if_stmt : IF expression THEN statement'
    if p[2] and p[2] != 'boolean':
        sem.error(p.lineno(1), f"La condición del IF debe ser booleana, se tiene '{p[2]}'")

def p_while_stmt(p):
    'while_stmt : WHILE expression DO statement'
    if p[2] and p[2] != 'boolean':
        sem.error(p.lineno(1), f"La condición del WHILE debe ser booleana, se tiene '{p[2]}'")

def p_for_stmt_1(p):
    'for_stmt : FOR ID ASSIGN expression TO expression DO statement'
    sym = sem.table.lookup(p[2])
    if sym is None:
        sem.error(p.lineno(2), f"'{p[2]}' no fue declarado")
    sem.table.mark_initialized(p[2])

def p_for_stmt_2(p):
    'for_stmt : FOR ID ASSIGN expression DOWNTO expression DO statement'
    sym = sem.table.lookup(p[2])
    if sym is None:
        sem.error(p.lineno(2), f"'{p[2]}' no fue declarado")
    sem.table.mark_initialized(p[2])

def p_repeat_stmt(p):
    'repeat_stmt : REPEAT statement_list UNTIL expression'
    if p[4] and p[4] != 'boolean':
        sem.error(p.lineno(1), f"La condición del REPEAT-UNTIL debe ser booleana, se tiene '{p[4]}'")

def p_case_stmt_1(p):
    'case_stmt : CASE expression OF case_list END'

def p_case_stmt_2(p):
    'case_stmt : CASE expression OF case_list ELSE statement END'

def p_case_list_1(p): 'case_list : case_list case_element'
def p_case_list_2(p): 'case_list : case_element'

def p_case_element(p):
    'case_element : case_label_list COLON statement SEMICOLON'

def p_case_label_list_1(p): 'case_label_list : case_label_list COMMA literal'
def p_case_label_list_2(p): 'case_label_list : literal'

def p_goto_stmt(p):
    'goto_stmt : GOTO NUMBER'

def p_labeled_stmt(p):
    'labeled_stmt : NUMBER COLON statement'

def p_with_stmt(p):
    'with_stmt : WITH variable_list DO statement'

def p_variable_list_1(p): 'variable_list : variable_list COMMA variable'
def p_variable_list_2(p): 'variable_list : variable'

# ─── Llamada a procedimiento (como sentencia) ─────────────────────

def p_procedure_call_stmt_1(p):
    'procedure_call_stmt : ID LPAR args RPAR'
    arg_types = p[3] or []
    sem.visit_call(p[1], arg_types, p.lineno(1))

def p_procedure_call_stmt_2(p):
    'procedure_call_stmt : ID'
    # Si no hay paréntesis podría ser asignación de función (retorno)
    # o llamada a proc sin args – verificamos que exista
    sym = sem.table.lookup(p[1])
    if sym is None and p[1].lower() not in ('writeln','write','readln','read'):
        sem.error(p.lineno(1), f"'{p[1]}' no fue declarado")

# ─── Variable (retorna (nombre, tipo)) ────────────────────────────

def p_variable_simple(p):
    'variable : ID'
    typ = sem.visit_variable(p[1], p.lineno(1))
    p[0] = (p[1], typ)

def p_variable_array(p):
    'variable : ID LBR expression RBR'
    sym = sem.table.lookup(p[1])
    if sym is None:
        sem.error(p.lineno(1), f"'{p[1]}' no fue declarado")
        p[0] = (p[1], None)
    else:
        # El tipo del elemento del array (simplificado)
        base = sym.type
        if 'of' in str(base):
            base = base.split('of')[-1].strip()
        p[0] = (p[1], base)

def p_variable_field(p):
    'variable : variable DOT ID'
    p[0] = (p[3], None)   # acceso a campo de record – tipo no verificado en profundidad

# ─── Expresiones ─────────────────────────────────────────────────

def p_expression_relop(p):
    'expression : simple_expression relop simple_expression'
    p[0] = sem.visit_binop(p[2], p[1], p[3], p.lineno(2))

def p_expression_simple(p):
    'expression : simple_expression'
    p[0] = p[1]

def p_expression_in(p):
    'expression : simple_expression IN set_constructor'
    p[0] = 'boolean'

def p_relop(p):
    '''relop : EQ
             | NE
             | LT
             | GT
             | LE
             | GE'''
    p[0] = p[1]

def p_simple_expression_addop(p):
    'simple_expression : simple_expression addop term'
    p[0] = sem.visit_binop(p[2], p[1], p[3], p.lineno(2))

def p_simple_expression_term(p):
    'simple_expression : term'
    p[0] = p[1]

def p_addop(p):
    '''addop : PLUS
             | MINUS
             | OR'''
    p[0] = p[1]

def p_term_mulop(p):
    'term : term mulop factor'
    p[0] = sem.visit_binop(p[2], p[1], p[3], p.lineno(2))

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_mulop(p):
    '''mulop : TIMES
             | DIVISION
             | DIV
             | MOD
             | AND'''
    p[0] = p[1]

# ─── Factores ────────────────────────────────────────────────────

def p_factor_number(p):
    'factor : NUMBER'
    p[0] = 'real' if isinstance(p[1], float) else 'integer'

def p_factor_charconst(p):
    'factor : CHARCONST'
    val = p[1]
    # 'x' → char,  'texto' con longitud >3 → string
    inner = val[1:-1].replace("''", "'")
    p[0] = 'char' if len(inner) == 1 else 'string'

def p_factor_nil(p):
    'factor : NIL'
    p[0] = 'nil'

def p_factor_variable(p):
    'factor : variable'
    p[0] = p[1][1] if p[1] else None   # tipo

def p_factor_call(p):
    'factor : ID LPAR args RPAR'
    arg_types = p[3] or []
    ret = sem.visit_call(p[1], arg_types, p.lineno(1))
    p[0] = ret

def p_factor_paren(p):
    'factor : LPAR expression RPAR'
    p[0] = p[2]

def p_factor_not(p):
    'factor : NOT factor'
    if p[2] and p[2] != 'boolean':
        sem.error(p.lineno(1), f"NOT requiere operando booleano, se tiene '{p[2]}'")
    p[0] = 'boolean'

def p_factor_set(p):
    'factor : set_constructor'
    p[0] = 'set'

# ─── Set constructor ──────────────────────────────────────────────

def p_set_constructor_1(p):
    'set_constructor : LBR set_element_list RBR'
    p[0] = 'set'

def p_set_constructor_2(p):
    'set_constructor : LBR RBR'
    p[0] = 'set'

def p_set_element_list_1(p): 'set_element_list : set_element_list COMMA set_element'
def p_set_element_list_2(p): 'set_element_list : set_element'

def p_set_element_range(p):
    'set_element : expression RANGE expression'

def p_set_element_single(p):
    'set_element : expression'

# ─── Args ────────────────────────────────────────────────────────

def p_args_1(p):
    'args : args_list'
    p[0] = p[1]

def p_args_2(p):
    'args : empty'
    p[0] = []

def p_args_list_1(p):
    'args_list : args_list COMMA expression'
    p[0] = p[1] + [p[3]]

def p_args_list_2(p):
    'args_list : expression'
    p[0] = [p[1]]

# ─── Literal ─────────────────────────────────────────────────────

def p_literal_number(p):
    'literal : NUMBER'
    p[0] = 'real' if isinstance(p[1], float) else 'integer'

def p_literal_charconst(p):
    'literal : CHARCONST'
    inner = p[1][1:-1].replace("''","'")
    p[0] = 'char' if len(inner) == 1 else 'string'

# ─── Vacío ───────────────────────────────────────────────────────

def p_empty(p):
    'empty :'
    p[0] = None

# ─── Error sintáctico ────────────────────────────────────────────

def p_error(p):
    if p:
        msg = f"ERROR SINTÁCTICO (línea {p.lineno}): token inesperado '{p.value}'"
        if not any(f"línea {p.lineno}" in e for e in syntax_errors):
            syntax_errors.append(msg)
        while True:
            tok = parser.token()
            if not tok or tok.type in ('SEMICOLON','BEGIN','END'):
                break
        parser.errok()

# ══════════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN DEL PARSER
# ══════════════════════════════════════════════════════════════════

parser = yacc.yacc()

# ══════════════════════════════════════════════════════════════════
#  BUILT-INS (writeln, write, readln, read)
# ══════════════════════════════════════════════════════════════════

def register_builtins():
    for name in ('writeln','write','readln','read'):
        sym = Symbol(name, 'procedure', 'void', 'global', 0,
                     initialized=True, params=[])
        sym.params = ['variadic']   # flag especial – no verificamos nº args
        sem.table.insert(sym)

# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    fin = sys.argv[1] if len(sys.argv) > 1 else 'input.pas'

    with open(fin, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    total_lines = len(data.splitlines())

    register_builtins()
    lexer.lineno = 1
    parser.parse(data, lexer=lexer, tracking=True)

    # ── Cabecera ──────────────────────────────────────────────────
    print()
    print("=" * 62)
    print(f"  Archivo analizado : {fin}")
    print(f"  Líneas totales    : {total_lines}")
    print("=" * 62)

    # ── Errores léxicos / sintácticos ────────────────────────────
    all_prior = lexer_errors + syntax_errors
    if all_prior:
        print(f"\n⚠  {len(all_prior)} error(es) léxico/sintáctico(s):")
        for e in all_prior:
            print(f"  {e}")

    # ── Resultado semántico + tabla ───────────────────────────────
    sem.report(total_lines)
