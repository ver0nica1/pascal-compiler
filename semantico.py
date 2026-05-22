import sys

T_INTEGER = 'integer'
T_REAL    = 'real'
T_BOOLEAN = 'boolean'
T_CHAR    = 'char'
T_STRING  = 'string'
T_VOID    = 'void'
T_UNKNOWN = 'unknown'

NUMERICOS = {T_INTEGER, T_REAL}

BUILTINS_IO = frozenset({'writeln', 'readln', 'write', 'read'})


class Nodo:
    pass


class NodoNull(Nodo):
    pass


class NodoNumero(Nodo):
    def __init__(self, valor):
        self.valor = valor


class NodoCharConst(Nodo):
    def __init__(self, valor):
        self.valor = valor


class NodoNil(Nodo):
    pass


class NodoPrograma(Nodo):
    def __init__(self, nombre, bloque):
        self.nombre = nombre
        self.bloque = bloque


class NodoBloque(Nodo):
    def __init__(self, sec_const, sec_type, sec_var, sec_subprog, cuerpo):
        self.sec_const   = sec_const
        self.sec_type    = sec_type
        self.sec_var     = sec_var
        self.sec_subprog = sec_subprog
        self.cuerpo      = cuerpo


class NodoSubBloque(Nodo):
    def __init__(self, sec_var, cuerpo):
        self.sec_var = sec_var
        self.cuerpo  = cuerpo


class NodoSeccion(Nodo):
    def __init__(self, items):
        self.items = items


class NodoSecSubprog(Nodo):
    def __init__(self, sps):
        self.subprogramas = sps


class NodoConstDef(Nodo):
    def __init__(self, nombre, valor, linea=0):
        self.nombre = nombre
        self.valor  = valor
        self.linea  = linea


class NodoTypeDef(Nodo):
    def __init__(self, nombre, tipo_str, linea=0):
        self.nombre   = nombre
        self.tipo_str = tipo_str
        self.linea    = linea


class NodoVarDecl(Nodo):
    def __init__(self, nombres, tipo_str, linea=0):
        self.nombres  = nombres
        self.tipo_str = tipo_str
        self.linea    = linea


class NodoFuncion(Nodo):
    def __init__(self, nombre, params, tipo_retorno, subbloque, linea=0):
        self.nombre       = nombre
        self.params       = params
        self.tipo_retorno = tipo_retorno
        self.subbloque    = subbloque
        self.linea        = linea


class NodoProcedimiento(Nodo):
    def __init__(self, nombre, params, subbloque, linea=0):
        self.nombre    = nombre
        self.params    = params
        self.subbloque = subbloque
        self.linea     = linea


class NodoCompuesto(Nodo):
    def __init__(self, stmts):
        self.sentencias = stmts


class NodoAsignacion(Nodo):
    def __init__(self, variable, expresion, linea=0):
        self.variable  = variable
        self.expresion = expresion
        self.linea     = linea


class NodoIf(Nodo):
    def __init__(self, condicion, entonces, linea=0):
        self.condicion = condicion
        self.entonces  = entonces
        self.linea     = linea


class NodoIfElse(Nodo):
    def __init__(self, condicion, entonces, sino, linea=0):
        self.condicion = condicion
        self.entonces  = entonces
        self.sino      = sino
        self.linea     = linea


class NodoWhile(Nodo):
    def __init__(self, condicion, cuerpo, linea=0):
        self.condicion = condicion
        self.cuerpo    = cuerpo
        self.linea     = linea


class NodoRepeat(Nodo):
    def __init__(self, cuerpo, condicion, linea=0):
        self.cuerpo    = cuerpo
        self.condicion = condicion
        self.linea     = linea


class NodoFor(Nodo):
    def __init__(self, var_control, inicio, direccion, limite, cuerpo, linea=0):
        self.var_control = var_control
        self.inicio      = inicio
        self.direccion   = direccion
        self.limite      = limite
        self.cuerpo      = cuerpo
        self.linea       = linea


class NodoCase(Nodo):
    def __init__(self, expresion, casos, sino=None, linea=0):
        self.expresion = expresion
        self.casos     = casos
        self.sino      = sino
        self.linea     = linea


class NodoCaseElem(Nodo):
    def __init__(self, etiquetas, sentencia):
        self.etiquetas = etiquetas
        self.sentencia = sentencia


class NodoWith(Nodo):
    def __init__(self, vars_, cuerpo, linea=0):
        self.vars_  = vars_
        self.cuerpo = cuerpo
        self.linea  = linea


class NodoLlamada(Nodo):
    def __init__(self, nombre, args, linea=0):
        self.nombre = nombre
        self.args   = args
        self.linea  = linea


class NodoBinOp(Nodo):
    def __init__(self, operador, izquierdo, derecho, linea=0):
        self.operador  = operador
        self.izquierdo = izquierdo
        self.derecho   = derecho
        self.linea     = linea


class NodoUnOp(Nodo):
    def __init__(self, operador, operando, linea=0):
        self.operador = operador
        self.operando = operando
        self.linea    = linea


class NodoVariable(Nodo):
    def __init__(self, nombre, linea=0):
        self.nombre = nombre
        self.linea  = linea


class NodoIndice(Nodo):
    def __init__(self, nombre, indice, linea=0):
        self.nombre = nombre
        self.indice = indice
        self.linea  = linea


class NodoCampo(Nodo):
    def __init__(self, registro, campo, linea=0):
        self.registro = registro
        self.campo    = campo
        self.linea    = linea


class Simbolo:
    def __init__(self, nombre, categoria, tipo, linea=0, ambito='global',
                 params=None, tipo_retorno=None):
        self.nombre       = nombre
        self.categoria    = categoria
        self.tipo         = tipo
        self.linea        = linea
        self.ambito       = ambito
        self.params       = params or []
        self.tipo_retorno = tipo_retorno


class TablaSimbolos:
    def __init__(self):
        self._ambitos = [{}]
        self._nombres = ['global']
        self._todos_simbolos = []

    def abrir_ambito(self, nombre='local'):
        self._ambitos.append({})
        self._nombres.append(nombre)

    def cerrar_ambito(self):
        if len(self._ambitos) > 1:
            self._ambitos.pop()
            self._nombres.pop()

    def declarar(self, simbolo):
        simbolo.ambito = self._nombres[-1]
        ambito = self._ambitos[-1]
        clave = simbolo.nombre.lower()
        if clave in ambito:
            return False
        ambito[clave] = simbolo
        self._todos_simbolos.append(simbolo)
        return True

    def buscar(self, nombre):
        clave = nombre.lower()
        for ambito in reversed(self._ambitos):
            if clave in ambito:
                return ambito[clave]
        return None

    def imprimir_tabla(self):
        print()
        print("=" * 84)
        print(f"{'TABLA DE SÍMBOLOS':^84}")
        print("=" * 84)
        print(f"  {'NOMBRE':<18} {'TIPO':<20} {'CATEGORÍA':<12} {'ÁMBITO':<16} {'LÍNEA':>5}")
        print("  " + "-" * 80)

        ambitos_vistos = []
        por_ambito = {}
        for s in self._todos_simbolos:
            if s.ambito not in por_ambito:
                por_ambito[s.ambito] = []
                ambitos_vistos.append(s.ambito)
            por_ambito[s.ambito].append(s)

        for ambito in ambitos_vistos:
            print(f"\n  Ámbito: {ambito}")
            print("  " + "-" * 80)
            for s in por_ambito[ambito]:
                extra = ""
                if s.categoria == 'function' and s.tipo_retorno:
                    extra = f" -> {s.tipo_retorno}"
                elif s.params:
                    ps = ", ".join(f"{n}:{t}" for n, t in s.params)
                    extra = f"({ps})"
                tipo_str = (str(s.tipo) + extra)[:19]
                print(f"  {s.nombre:<18} {tipo_str:<20} {s.categoria:<12} {s.ambito:<16} {s.linea:>5}")

        print("=" * 84)


class AnalizadorSemantico:
    def __init__(self):
        self.tabla   = TablaSimbolos()
        self.errores = []

    def _error(self, mensaje, linea=None):
        prefijo = "ERROR SEMÁNTICO"
        if linea:
            prefijo += f" (línea {linea})"
        self.errores.append(f"{prefijo}: {mensaje}")

    @staticmethod
    def _compatible(tipo_destino, tipo_origen):
        if T_UNKNOWN in (tipo_destino, tipo_origen):
            return True
        if tipo_destino == tipo_origen:
            return True
        if tipo_destino == T_REAL and tipo_origen == T_INTEGER:
            return True
        if tipo_destino == T_STRING and tipo_origen == T_CHAR:
            return True
        return False

    def _visitar_lista(self, nodos):
        for n in nodos or []:
            self._visitar(n)

    def _chequear_booleano(self, tipo, contexto, linea):
        if tipo not in (T_BOOLEAN, T_UNKNOWN):
            self._error(f"La condición del {contexto} debe ser boolean, pero es '{tipo}'", linea)

    @staticmethod
    def _aplanar_params(params):
        resultado = []
        for (nombres, tipo) in params:
            for nm in nombres:
                resultado.append((nm, tipo))
        return resultado

    def _es_concat_string(self, izq, der):
        if izq == T_STRING and der == T_STRING:
            return True
        if izq == T_STRING and der == T_CHAR:
            return True
        if izq == T_CHAR and der == T_STRING:
            return True
        return False

    def _evaluar_binop(self, op, izq, der, linea):
        if T_UNKNOWN in (izq, der):
            return T_UNKNOWN

        op = str(op).lower()
        aritmeticos = ('+', '-', '*', '/', 'div', 'mod')
        logicos = ('and', 'or')
        relacionales = ('=', '<>', '<', '>', '<=', '>=', 'in')

        if op in aritmeticos:
            if op == '+' and self._es_concat_string(izq, der):
                return T_STRING
            if izq in NUMERICOS and der in NUMERICOS:
                if op in ('div', 'mod'):
                    if izq == T_INTEGER and der == T_INTEGER:
                        return T_INTEGER
                    self._error(
                        f"Operación '{op}' requiere operandos integer, "
                        f"pero se tienen '{izq}' y '{der}'",
                        linea
                    )
                    return T_UNKNOWN
                if op == '/':
                    return T_REAL
                return T_REAL if T_REAL in (izq, der) else T_INTEGER
            self._error(
                f"Operación aritmética '{op}' requiere operandos numéricos, "
                f"pero se tienen '{izq}' y '{der}'",
                linea
            )
            return T_UNKNOWN

        if op in logicos:
            if izq == T_BOOLEAN and der == T_BOOLEAN:
                return T_BOOLEAN
            self._error(
                f"Operación lógica '{op}' requiere booleanos, "
                f"pero se tienen '{izq}' y '{der}'",
                linea
            )
            return T_UNKNOWN

        if op in relacionales:
            if (izq in NUMERICOS and der in NUMERICOS) or izq == der:
                return T_BOOLEAN
            if izq == T_UNKNOWN or der == T_UNKNOWN:
                return T_UNKNOWN
            self._error(
                f"Comparación '{op}' entre tipos incompatibles: '{izq}' y '{der}'",
                linea
            )
            return T_UNKNOWN

        return T_UNKNOWN

    def _declarar_subprograma(self, n, es_funcion):
        params = self._aplanar_params(n.params)
        if es_funcion:
            sim = Simbolo(n.nombre, 'function', n.tipo_retorno, n.linea,
                          params=params, tipo_retorno=n.tipo_retorno)
            if not self.tabla.declarar(sim):
                self._error(f"Función '{n.nombre}' ya está declarada", n.linea)
            kind = 'función'
        else:
            sim = Simbolo(n.nombre, 'procedure', T_VOID, n.linea, params=params)
            if not self.tabla.declarar(sim):
                self._error(f"Procedimiento '{n.nombre}' ya está declarado", n.linea)
            kind = 'procedimiento'

        self.tabla.abrir_ambito(n.nombre)
        for (nm, tipo) in params:
            if not self.tabla.declarar(Simbolo(nm, 'var', tipo, n.linea)):
                self._error(f"Parámetro duplicado '{nm}' en {kind} '{n.nombre}'", n.linea)

        self._visitar(n.subbloque)
        self.tabla.cerrar_ambito()

    def analizar(self, ast):
        if ast is not None:
            self._visitar(ast)
        return self.errores

    def _visitar(self, nodo):
        if nodo is None:
            return T_UNKNOWN
        metodo = getattr(self, f'_v_{type(nodo).__name__}', None)
        if metodo is None:
            return T_UNKNOWN
        return metodo(nodo)

    def _v_NodoPrograma(self, n):
        self._visitar(n.bloque)

    def _v_NodoBloque(self, n):
        self._visitar(n.sec_const)
        self._visitar(n.sec_type)
        self._visitar(n.sec_var)
        self._visitar(n.sec_subprog)
        self._visitar(n.cuerpo)

    def _v_NodoSubBloque(self, n):
        self._visitar(n.sec_var)
        self._visitar(n.cuerpo)

    def _v_NodoNull(self, n):
        return T_UNKNOWN

    def _v_NodoSeccion(self, n):
        self._visitar_lista(n.items)

    def _v_NodoConstDef(self, n):
        tipo_val = self._visitar(n.valor)
        sim = Simbolo(n.nombre, 'const', tipo_val, n.linea)
        if not self.tabla.declarar(sim):
            self._error(f"'{n.nombre}' ya está declarado en este ámbito", n.linea)

    def _v_NodoTypeDef(self, n):
        sim = Simbolo(n.nombre, 'type', n.tipo_str, n.linea)
        if not self.tabla.declarar(sim):
            self._error(f"Tipo '{n.nombre}' ya está declarado", n.linea)

    def _v_NodoVarDecl(self, n):
        for nombre in n.nombres:
            sim = Simbolo(nombre, 'var', n.tipo_str, n.linea)
            if not self.tabla.declarar(sim):
                self._error(f"Variable '{nombre}' ya está declarada en este ámbito", n.linea)

    def _v_NodoFuncion(self, n):
        self._declarar_subprograma(n, True)

    def _v_NodoProcedimiento(self, n):
        self._declarar_subprograma(n, False)

    def _v_NodoSecSubprog(self, n):
        self._visitar_lista(n.subprogramas)

    def _v_NodoAsignacion(self, n):
        tipo_var  = self._visitar(n.variable)
        tipo_expr = self._visitar(n.expresion)
        if not self._compatible(tipo_var, tipo_expr):
            nombre = getattr(n.variable, 'nombre', None)
            if nombre:
                self._error(
                    f"Incompatibilidad de tipos en asignación: "
                    f"'{nombre}' es '{tipo_var}' pero se asigna '{tipo_expr}'",
                    n.linea
                )
            else:
                self._error(
                    f"Incompatibilidad de tipos en asignación: "
                    f"se esperaba '{tipo_var}' pero se asigna '{tipo_expr}'",
                    n.linea
                )

    def _v_NodoIf(self, n):
        self._chequear_booleano(self._visitar(n.condicion), 'IF', n.linea)
        self._visitar(n.entonces)

    def _v_NodoIfElse(self, n):
        self._chequear_booleano(self._visitar(n.condicion), 'IF', n.linea)
        self._visitar(n.entonces)
        self._visitar(n.sino)

    def _v_NodoWhile(self, n):
        self._chequear_booleano(self._visitar(n.condicion), 'WHILE', n.linea)
        self._visitar(n.cuerpo)

    def _v_NodoRepeat(self, n):
        self._visitar(n.cuerpo)
        self._chequear_booleano(self._visitar(n.condicion), 'REPEAT..UNTIL', n.linea)

    def _v_NodoFor(self, n):
        sim = self.tabla.buscar(n.var_control)
        if sim is None:
            self._error(f"Variable de control '{n.var_control}' no declarada", n.linea)
        elif sim.tipo not in (T_INTEGER, T_CHAR, T_UNKNOWN):
            self._error(
                f"La variable de control del FOR ('{n.var_control}') debe ser "
                f"integer o char, pero es '{sim.tipo}'", n.linea
            )
        for expr in (n.inicio, n.limite):
            t = self._visitar(expr)
            if t not in (T_INTEGER, T_CHAR, T_UNKNOWN):
                self._error(f"Los límites del FOR deben ser integer o char, se encontró '{t}'", n.linea)
        self._visitar(n.cuerpo)

    def _v_NodoCase(self, n):
        self._visitar(n.expresion)
        self._visitar_lista(n.casos)
        if n.sino:
            self._visitar(n.sino)

    def _v_NodoCaseElem(self, n):
        self._visitar(n.sentencia)

    def _v_NodoWith(self, n):
        self._visitar(n.cuerpo)

    def _v_NodoCompuesto(self, n):
        self._visitar_lista(n.sentencias)

    def _v_NodoLlamada(self, n):
        nombre = n.nombre.lower()
        sim = self.tabla.buscar(n.nombre)

        if sim is None:
            if nombre not in BUILTINS_IO:
                self._error(f"Función/Procedimiento '{n.nombre}' no declarado", n.linea)
            self._visitar_lista(n.args)
            return T_UNKNOWN

        if sim.categoria not in ('function', 'procedure'):
            self._error(f"'{n.nombre}' no es una función ni un procedimiento", n.linea)
            self._visitar_lista(n.args)
            return T_UNKNOWN

        if nombre in BUILTINS_IO:
            self._visitar_lista(n.args)
            return sim.tipo_retorno if sim.categoria == 'function' else T_VOID

        if len(n.args) != len(sim.params):
            self._error(
                f"'{n.nombre}' espera {len(sim.params)} argumento(s), "
                f"pero recibió {len(n.args)}", n.linea
            )

        for i, (arg, (pnm, ptipo)) in enumerate(zip(n.args, sim.params), 1):
            tipo_arg = self._visitar(arg)
            if not self._compatible(ptipo, tipo_arg):
                self._error(
                    f"En '{n.nombre}', argumento {i} ('{pnm}'): "
                    f"se esperaba '{ptipo}' pero se recibió '{tipo_arg}'", n.linea
                )

        return sim.tipo_retorno if sim.categoria == 'function' else T_VOID

    def _v_NodoBinOp(self, n):
        return self._evaluar_binop(
            n.operador,
            self._visitar(n.izquierdo),
            self._visitar(n.derecho),
            n.linea
        )

    def _v_NodoUnOp(self, n):
        tipo_op = self._visitar(n.operando)
        op = str(n.operador).lower()
        if op == 'not':
            if tipo_op not in (T_BOOLEAN, T_UNKNOWN):
                self._error(
                    f"Operación lógica 'not' requiere booleano, pero se tiene '{tipo_op}'",
                    n.linea
                )
            return T_BOOLEAN
        if op in ('+', '-'):
            if tipo_op not in NUMERICOS and tipo_op != T_UNKNOWN:
                self._error(
                    f"Operador unario '{n.operador}' requiere operando numérico, "
                    f"pero se tiene '{tipo_op}'",
                    n.linea
                )
            return tipo_op
        return T_UNKNOWN

    def _v_NodoVariable(self, n):
        sim = self.tabla.buscar(n.nombre)
        if sim is None:
            self._error(f"Identificador '{n.nombre}' no declarado", n.linea)
            return T_UNKNOWN
        return sim.tipo

    def _v_NodoIndice(self, n):
        sim = self.tabla.buscar(n.nombre)
        if sim is None:
            self._error(f"Arreglo '{n.nombre}' no declarado", n.linea)
            return T_UNKNOWN
        tipo_idx = self._visitar(n.indice)
        if tipo_idx not in (T_INTEGER, T_UNKNOWN):
            self._error(f"El índice de '{n.nombre}' debe ser integer, pero es '{tipo_idx}'", n.linea)
        if isinstance(sim.tipo, str) and sim.tipo.startswith('array:'):
            return sim.tipo.split(':', 1)[1]
        return T_UNKNOWN

    def _v_NodoCampo(self, n):
        self._visitar(n.registro)
        return T_UNKNOWN

    def _v_NodoNumero(self, n):
        return T_REAL if isinstance(n.valor, float) else T_INTEGER

    def _v_NodoCharConst(self, n):
        interno = n.valor[1:-1]
        return T_CHAR if len(interno) == 1 else T_STRING

    def _v_NodoNil(self, n):
        return T_UNKNOWN


def registrar_builtins(analizador):
    for nombre in BUILTINS_IO:
        sim = Simbolo(nombre, 'procedure', T_VOID, 0, ambito='global')
        analizador.tabla.declarar(sim)


def analizar_archivo(ruta_archivo):
    from parser_sem import parser, errors_list
    import lexer as pascal_lexer

    with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    total_lineas = len(data.splitlines())
    pascal_lexer.lexer_errors = []
    errors_list.clear()

    ast = parser.parse(data, lexer=pascal_lexer.lexer, tracking=True)
    errores_previos = list(pascal_lexer.lexer_errors) + list(errors_list)

    analizador = AnalizadorSemantico()
    registrar_builtins(analizador)

    if ast is not None and len(errores_previos) == 0:
        analizador.analizar(ast)

    todos = errores_previos + analizador.errores
    return analizador, todos, total_lineas, errores_previos


def reporte_semantico(analizador, total_lineas, errores_previos=None):
    print()
    print("=" * 70)
    print(f"{'ANÁLISIS SEMÁNTICO':^70}")
    print("=" * 70)
    print(f"  Líneas analizadas: {total_lineas}")

    if errores_previos:
        print(f"\n  {len(errores_previos)} error(es) léxico/sintáctico(s) — semántica omitida:")
        for e in errores_previos:
            print(f"    {e}")
        analizador.tabla.imprimir_tabla()
        return

    print()
    print("=" * 70)
    print(f"{'ERRORES SEMÁNTICOS':^70}")
    print("=" * 70)
    if analizador.errores:
        print(f"\n  Se encontraron {len(analizador.errores)} error(es):\n")
        for err in analizador.errores:
            print(f"    {err}")
    else:
        print("\n  Sin errores semánticos.")

    analizador.tabla.imprimir_tabla()


if __name__ == '__main__':
    archivo = sys.argv[1] if len(sys.argv) > 1 else 'input.pas'
    print(f"\nArchivo: {archivo}")
    try:
        analizador, todos, lineas, previos = analizar_archivo(archivo)
    except FileNotFoundError:
        print(f"ERROR: no se encontró el archivo '{archivo}'")
        sys.exit(1)

    reporte_semantico(analizador, lineas, previos)
    if todos:
        print(f"\nTotal de errores (todas las fases): {len(todos)}")
    else:
        print("\n[OK] Sin errores léxicos, sintácticos ni semánticos.")
    sys.exit(0)
