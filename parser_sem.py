import ply.yacc as yacc
from lexer import tokens
import lexer as pascal_lexer
from semantico import *
import sys

precedence = (
    ('nonassoc', 'LOWER_THAN_ELSE'),
    ('nonassoc', 'ELSE'),
    ('left',  'OR'),
    ('left',  'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'IN'),
    ('left',  'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
    ('left',  'PLUS', 'MINUS'),
    ('left',  'TIMES', 'DIVISION', 'DIV', 'MOD'),
    ('right', 'UMINUS', 'UPLUS'),
)

# ==============================================================
#   PROGRAMA
# ==============================================================

def p_program(p):
    'program : PROGRAM ID SEMICOLON block DOT'
    p[0] = NodoPrograma(p[2], p[4])

# ==============================================================
#   BLOQUE PRINCIPAL
# ==============================================================

def p_block(p):
    'block : label_part const_part type_part var_part subprogram_declarations compound_stmt'
    p[0] = NodoBloque(p[2], p[3], p[4], p[5], p[6])

# ==============================================================
#   SECCIÓN LABEL  (puede estar vacía — no genera nodo semántico)
# ==============================================================

def p_label_part_1(p):
    'label_part : LABEL label_list SEMICOLON'
    p[0] = NodoNull()

def p_label_part_2(p):
    'label_part : empty'
    p[0] = NodoNull()

def p_label_list_1(p):
    'label_list : label_list COMMA NUMBER'
    pass

def p_label_list_2(p):
    'label_list : NUMBER'
    pass

# ==============================================================
#   SECCIÓN CONST
# ==============================================================

def p_const_part_1(p):
    'const_part : CONST const_list'
    p[0] = NodoSeccion(p[2])

def p_const_part_2(p):
    'const_part : empty'
    p[0] = NodoNull()

def p_const_list_1(p):
    'const_list : const_list const_def'
    p[0] = p[1] + [p[2]]

def p_const_list_2(p):
    'const_list : const_def'
    p[0] = [p[1]]

def p_const_def(p):
    'const_def : ID EQ literal SEMICOLON'
    p[0] = NodoConstDef(p[1], p[3], p.lineno(1))

# ==============================================================
#   SECCIÓN TYPE
# ==============================================================

def p_type_part_1(p):
    'type_part : TYPE type_list'
    p[0] = NodoSeccion(p[2])

def p_type_part_2(p):
    'type_part : empty'
    p[0] = NodoNull()

def p_type_list_1(p):
    'type_list : type_list type_def'
    p[0] = p[1] + [p[2]]

def p_type_list_2(p):
    'type_list : type_def'
    p[0] = [p[1]]

def p_type_def(p):
    'type_def : ID EQ type_specifier SEMICOLON'
    p[0] = NodoTypeDef(p[1], p[3], p.lineno(1))

# ==============================================================
#   SECCIÓN VAR
# ==============================================================

def p_var_part_1(p):
    'var_part : VAR var_declaration_list'
    p[0] = NodoSeccion(p[2])

def p_var_part_2(p):
    'var_part : empty'
    p[0] = NodoNull()

def p_var_declaration_list_1(p):
    'var_declaration_list : var_declaration_list var_declaration'
    p[0] = p[1] + [p[2]]

def p_var_declaration_list_2(p):
    'var_declaration_list : var_declaration'
    p[0] = [p[1]]

def p_var_declaration(p):
    'var_declaration : id_list COLON type_specifier SEMICOLON'
    p[0] = NodoVarDecl(p[1], p[3], p.lineno(2))

def p_id_list_1(p):
    'id_list : id_list COMMA ID'
    p[0] = p[1] + [p[3]]

def p_id_list_2(p):
    'id_list : ID'
    p[0] = [p[1]]

# ==============================================================
#   ESPECIFICADORES DE TIPO  (devuelven string)
# ==============================================================

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
    p[0] = f'array:{p[8]}'

def p_type_specifier_record(p):
    'type_specifier : RECORD field_list END'
    p[0] = 'record'

def p_type_specifier_set(p):
    'type_specifier : SET OF type_specifier'
    p[0] = f'set:{p[3]}'

def p_type_specifier_file(p):
    'type_specifier : FILE OF type_specifier'
    p[0] = f'file:{p[3]}'

def p_type_specifier_file_plain(p):
    'type_specifier : FILE'
    p[0] = 'file'

def p_type_specifier_packed(p):
    'type_specifier : PACKED type_specifier'
    p[0] = f'packed:{p[2]}'

def p_type_specifier_id(p):
    'type_specifier : ID'
    p[0] = p[1]

# ==============================================================
#   CAMPOS DE RECORD
# ==============================================================

def p_field_list_1(p):
    'field_list : field_list SEMICOLON field_declaration'
    pass

def p_field_list_2(p):
    'field_list : field_declaration'
    pass

def p_field_list_3(p):
    'field_list : empty'
    pass

def p_field_declaration(p):
    'field_declaration : id_list COLON type_specifier'
    pass

# ==============================================================
#   DECLARACIONES DE SUBPROGRAMAS
# ==============================================================

def p_subprogram_declarations_1(p):
    'subprogram_declarations : subprogram_declarations subprogram_declaration'
    p[0] = NodoSecSubprog(p[1].subprogramas + [p[2]])

def p_subprogram_declarations_2(p):
    'subprogram_declarations : empty'
    p[0] = NodoSecSubprog([])

def p_subprogram_declaration_function(p):
    'subprogram_declaration : function_declaration'
    p[0] = p[1]

def p_subprogram_declaration_procedure(p):
    'subprogram_declaration : procedure_declaration'
    p[0] = p[1]

# ── FUNCTION ──────────────────────────────────────────────────

def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAR params RPAR COLON type_specifier SEMICOLON subblock SEMICOLON'
    p[0] = NodoFuncion(p[2], p[4], p[7], p[9], p.lineno(1))

# ── PROCEDURE ────────────────────────────────────────────────

def p_procedure_declaration(p):
    'procedure_declaration : PROCEDURE ID LPAR params RPAR SEMICOLON subblock SEMICOLON'
    p[0] = NodoProcedimiento(p[2], p[4], p[7], p.lineno(1))

# Sub-bloque (var opcional + cuerpo)
def p_subblock(p):
    'subblock : label_part var_part compound_stmt'
    p[0] = NodoSubBloque(p[2], p[3])

# ==============================================================
#   PARÁMETROS
# ==============================================================

def p_params_1(p):
    'params : param_list'
    p[0] = p[1]

def p_params_2(p):
    'params : empty'
    p[0] = []

def p_param_list_1(p):
    'param_list : param_list SEMICOLON param'
    p[0] = p[1] + [p[3]]

def p_param_list_2(p):
    'param_list : param'
    p[0] = [p[1]]

def p_param(p):
    'param : id_list COLON type_specifier'
    p[0] = (p[1], p[3])   # ([nombres], tipo_str)

# ==============================================================
#   CUERPO: begin  sentencias  end
# ==============================================================

def p_compound_stmt(p):
    'compound_stmt : BEGIN statement_list END'
    p[0] = NodoCompuesto(p[2])

def p_statement_list_1(p):
    'statement_list : statement_list SEMICOLON statement'
    p[0] = p[1] + [p[3]]

def p_statement_list_2(p):
    'statement_list : statement'
    p[0] = [p[1]]

# ==============================================================
#   SENTENCIAS
# ==============================================================

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
    p[0] = p[1] if p[1] is not None else NodoNull()

# ── ASIGNACIÓN ────────────────────────────────────────────────

def p_assignment_stmt(p):
    'assignment_stmt : variable ASSIGN expression'
    p[0] = NodoAsignacion(p[1], p[3], p.lineno(2))

# ── IF ────────────────────────────────────────────────────────

def p_if_stmt_1(p):
    'if_stmt : IF expression THEN statement %prec LOWER_THAN_ELSE'
    p[0] = NodoIf(p[2], p[4], p.lineno(1))

def p_if_stmt_2(p):
    'if_stmt : IF expression THEN statement ELSE statement'
    p[0] = NodoIfElse(p[2], p[4], p[6], p.lineno(1))

# ── WHILE ─────────────────────────────────────────────────────

def p_while_stmt(p):
    'while_stmt : WHILE expression DO statement'
    p[0] = NodoWhile(p[2], p[4], p.lineno(1))

# ── FOR ───────────────────────────────────────────────────────

def p_for_stmt_1(p):
    'for_stmt : FOR ID ASSIGN expression TO expression DO statement'
    p[0] = NodoFor(p[2], p[4], 'to', p[6], p[8], p.lineno(1))

def p_for_stmt_2(p):
    'for_stmt : FOR ID ASSIGN expression DOWNTO expression DO statement'
    p[0] = NodoFor(p[2], p[4], 'downto', p[6], p[8], p.lineno(1))

# ── REPEAT ────────────────────────────────────────────────────

def p_repeat_stmt(p):
    'repeat_stmt : REPEAT statement_list UNTIL expression'
    p[0] = NodoRepeat(NodoCompuesto(p[2]), p[4], p.lineno(1))

# ── CASE ──────────────────────────────────────────────────────

def p_case_stmt_1(p):
    'case_stmt : CASE expression OF case_list END'
    p[0] = NodoCase(p[2], p[4], None, p.lineno(1))

def p_case_stmt_2(p):
    'case_stmt : CASE expression OF case_list ELSE statement END'
    p[0] = NodoCase(p[2], p[4], p[6], p.lineno(1))

def p_case_list_1(p):
    'case_list : case_list case_element'
    p[0] = p[1] + [p[2]]

def p_case_list_2(p):
    'case_list : case_element'
    p[0] = [p[1]]

def p_case_element(p):
    'case_element : case_label_list COLON statement SEMICOLON'
    p[0] = NodoCaseElem(p[1], p[3])

def p_case_label_list_1(p):
    'case_label_list : case_label_list COMMA literal'
    p[0] = p[1] + [p[3]]

def p_case_label_list_2(p):
    'case_label_list : literal'
    p[0] = [p[1]]

# ── GOTO ──────────────────────────────────────────────────────

def p_goto_stmt(p):
    'goto_stmt : GOTO NUMBER'
    p[0] = NodoNull()

# ── ETIQUETA ──────────────────────────────────────────────────

def p_labeled_stmt(p):
    'labeled_stmt : NUMBER COLON statement'
    p[0] = p[3]

# ── WITH ──────────────────────────────────────────────────────

def p_with_stmt(p):
    'with_stmt : WITH variable_list DO statement'
    p[0] = NodoWith(p[2], p[4], p.lineno(1))

def p_variable_list_1(p):
    'variable_list : variable_list COMMA variable'
    p[0] = p[1] + [p[3]]

def p_variable_list_2(p):
    'variable_list : variable'
    p[0] = [p[1]]

# ── LLAMADA A PROCEDIMIENTO ───────────────────────────────────

def p_procedure_call_stmt_1(p):
    'procedure_call_stmt : ID LPAR args RPAR'
    p[0] = NodoLlamada(p[1], p[3], p.lineno(1))

def p_procedure_call_stmt_2(p):
    'procedure_call_stmt : ID'
    p[0] = NodoLlamada(p[1], [], p.lineno(1))

# ==============================================================
#   VARIABLE  (lado izquierdo de asignaciones / acceso)
# ==============================================================

def p_variable_simple(p):
    'variable : ID'
    p[0] = NodoVariable(p[1], p.lineno(1))

def p_variable_array(p):
    'variable : ID LBR expression RBR'
    p[0] = NodoIndice(p[1], p[3], p.lineno(1))

def p_variable_field(p):
    'variable : variable DOT ID'
    p[0] = NodoCampo(p[1], p[3], p.lineno(2))

# ==============================================================
#   EXPRESIONES
# ==============================================================

def p_expression_relop(p):
    'expression : simple_expression relop simple_expression'
    p[0] = NodoBinOp(p[2], p[1], p[3], p.lineno(2))

def p_expression_simple(p):
    'expression : simple_expression'
    p[0] = p[1]

def p_expression_in(p):
    'expression : simple_expression IN set_constructor'
    p[0] = NodoBinOp('in', p[1], p[3], p.lineno(2))

def p_relop(p):
    '''relop : EQ
             | NE
             | LT
             | GT
             | LE
             | GE
    '''
    p[0] = p[1]

def p_simple_expression_addop(p):
    'simple_expression : simple_expression addop term'
    p[0] = NodoBinOp(p[2], p[1], p[3], p.lineno(2))

def p_simple_expression_term(p):
    'simple_expression : term'
    p[0] = p[1]

def p_addop(p):
    '''addop : PLUS
             | MINUS
             | OR
    '''
    p[0] = p[1]

def p_term_mulop(p):
    'term : term mulop factor'
    p[0] = NodoBinOp(p[2], p[1], p[3], p.lineno(2))

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_mulop(p):
    '''mulop : TIMES
             | DIVISION
             | DIV
             | MOD
             | AND
    '''
    p[0] = p[1]

# ── Factores ──────────────────────────────────────────────────

def p_factor_number(p):
    'factor : NUMBER'
    p[0] = NodoNumero(p[1])

def p_factor_charconst(p):
    'factor : CHARCONST'
    p[0] = NodoCharConst(p[1])

def p_factor_nil(p):
    'factor : NIL'
    p[0] = NodoNil()

def p_factor_variable(p):
    'factor : variable'
    p[0] = p[1]

def p_factor_call(p):
    'factor : ID LPAR args RPAR'
    p[0] = NodoLlamada(p[1], p[3], p.lineno(1))

def p_factor_paren(p):
    'factor : LPAR expression RPAR'
    p[0] = p[2]

def p_factor_not(p):
    'factor : NOT factor'
    p[0] = NodoUnOp('not', p[2], p.lineno(1))

def p_factor_uminus(p):
    'factor : MINUS factor %prec UMINUS'
    p[0] = NodoUnOp('-', p[2], p.lineno(1))

def p_factor_uplus(p):
    'factor : PLUS factor %prec UPLUS'
    p[0] = NodoUnOp('+', p[2], p.lineno(1))

def p_factor_set(p):
    'factor : set_constructor'
    p[0] = p[1]

# ==============================================================
#   SET CONSTRUCTOR
# ==============================================================

def p_set_constructor_1(p):
    'set_constructor : LBR set_element_list RBR'
    p[0] = NodoNull()

def p_set_constructor_2(p):
    'set_constructor : LBR RBR'
    p[0] = NodoNull()

def p_set_element_list_1(p):
    'set_element_list : set_element_list COMMA set_element'
    pass

def p_set_element_list_2(p):
    'set_element_list : set_element'
    pass

def p_set_element_range(p):
    'set_element : expression RANGE expression'
    pass

def p_set_element_single(p):
    'set_element : expression'
    pass

# ==============================================================
#   ARGUMENTOS
# ==============================================================

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

# ==============================================================
#   LITERALES
# ==============================================================

def p_literal_number(p):
    'literal : NUMBER'
    p[0] = NodoNumero(p[1])

def p_literal_charconst(p):
    'literal : CHARCONST'
    p[0] = NodoCharConst(p[1])

# ==============================================================
#   PRODUCCIÓN VACÍA
# ==============================================================

def p_empty(p):
    'empty :'
    p[0] = NodoNull()

# ==============================================================
#   MANEJO DE ERRORES SINTÁCTICOS
# ==============================================================

errors_list = []

def p_error(p):
    global errors_list
    if p is not None:
        msg = f"ERROR SINTÁCTICO en la línea {p.lineno}: token inesperado '{p.value}'"
        if not any(f"línea {p.lineno}:" in e for e in errors_list):
            errors_list.append(msg)
        while True:
            tok = parser.token()
            if not tok or tok.type in ('SEMICOLON', 'BEGIN', 'END'):
                break
        parser.errok()
    # EOF inesperado: silencioso

# ==============================================================
#   CONSTRUCCIÓN DEL PARSER
# ==============================================================

parser = yacc.yacc()

# ==============================================================
#   MAIN
# ==============================================================

if __name__ == '__main__':
    from semantico import analizar_archivo, reporte_semantico

    fin = sys.argv[1] if len(sys.argv) > 1 else 'input.pas'
    print(f"\nArchivo: {fin}")

    analizador, todos_errores, total_lineas, errores_previos = analizar_archivo(fin)
    reporte_semantico(analizador, total_lineas, errores_previos)

    if errores_previos:
        print(f"\n{len(errores_previos)} error(es) léxico/sintáctico(s).")
    elif len(todos_errores) == 0:
        print("\n[OK] El programa es léxica, sintáctica y semánticamente correcto.")
    else:
        print(f"\nTotal de errores: {len(todos_errores)}")
    sys.exit(0)