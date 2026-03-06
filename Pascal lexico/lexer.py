import ply.lex as lex
import sys

# Analizacor léxico para un subconjunto de Pascal

tokens = (
    
    # 35 palabras reservadas de la documentación básica de pascal basic syntax

    'AND', 'ARRAY', 'BEGIN', 'CASE', 'CONST',
    'DIV', 'DO', 'DOWNTO', 'ELSE', 'END',
    'FILE', 'FOR', 'FUNCTION', 'GOTO', 'IF',
    'IN', 'LABEL', 'MOD', 'NIL', 'NOT',
    'OF', 'OR', 'PACKED', 'PROCEDURE', 'PROGRAM',
    'RECORD', 'REPEAT', 'SET', 'THEN', 'TO',
    'TYPE', 'UNTIL', 'VAR', 'WHILE', 'WITH',

    # Tipos de dato 
    
    'INTEGER', 'REAL', 'BOOLEAN', 'CHAR', 'STRING',

    # Literales 

    'NUMBER',       # Enteros y reales: 123, 3.14, 2e10
    'CHARCONST',    # String entre comillas simples o dobles: 'a'  "hello"

    #  Identificador 
    
    'ID',

    #  Operadores y símbolos 

    'PLUS',         # +
    'MINUS',        # -
    'TIMES',        # *
    'DIVISION',     # /
    'EQ',           # =
    'NE',           # <>
    'LT',           # <
    'GT',           # >
    'LE',           # <=
    'GE',           # >=
    'ASSIGN',       # :=
    'RANGE',        # ..
    'DOT',          # .
    'COMMA',        # ,
    'SEMICOLON',    # ;
    'COLON',        # :
    'LPAR',         # (
    'RPAR',         # )
    'LBR',          # [
    'RBR',          # ]
)

# Ignorados y comentarios

t_ignore = ' \t\r'

def t_COMMENT(t):
    r'\(\*(.|\n)*?\*\)|{[^}]*}'
    t.lexer.lineno += t.value.count('\n')
    # No retorna: el token se descarta

# Palabras reservadas: una función por cada keyword, con el mismo nombre que el token

def t_PROGRAM(t):
    r'program'
    return t

def t_PROCEDURE(t):
    r'procedure'
    return t

def t_FUNCTION(t):
    r'function'
    return t

def t_DOWNTO(t):
    r'downto'
    return t

def t_DO(t):
    r'do'
    return t

def t_FOR(t):
    r'for'
    return t

def t_ARRAY(t):
    r'array'
    return t

def t_AND(t):
    r'and'
    return t

def t_BEGIN(t):
    r'begin'
    return t

def t_CASE(t):
    r'case'
    return t

def t_CONST(t):
    r'const'
    return t

def t_DIV(t):
    r'div'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_END(t):
    r'end'
    return t

def t_FILE(t):
    r'file'
    return t

def t_GOTO(t):
    r'goto'
    return t

def t_IF(t):
    r'if'
    return t

def t_IN(t):
    r'in'
    return t

def t_LABEL(t):
    r'label'
    return t

def t_MOD(t):
    r'mod'
    return t

def t_NIL(t):
    r'nil'
    return t

def t_NOT(t):
    r'not'
    return t

def t_OF(t):
    r'of'
    return t

def t_OR(t):
    r'or'
    return t

def t_PACKED(t):
    r'packed'
    return t

def t_RECORD(t):
    r'record'
    return t

def t_REPEAT(t):
    r'repeat'
    return t

def t_SET(t):
    r'set'
    return t

def t_THEN(t):
    r'then'
    return t

def t_TO(t):
    r'to'
    return t

def t_TYPE(t):
    r'type'
    return t

def t_UNTIL(t):
    r'until'
    return t

def t_VAR(t):
    r'var'
    return t

def t_WHILE(t):
    r'while'
    return t

def t_WITH(t):
    r'with'
    return t

# Tipos de dato 

def t_INTEGER(t):
    r'integer'
    return t

def t_REAL(t):
    r'real'
    return t

def t_BOOLEAN(t):
    r'boolean'
    return t

def t_STRING(t):
    r'string'
    return t

def t_CHAR(t):
    r'char'
    return t

# Literals: números y strings entre comillas

def t_CHARCONST(t):
    r'\'[^\']*\'|"[^"]*"'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?([eE][+-]?\d+)?'
    if '.' in t.value or 'e' in t.value.lower():
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

# Identificador: letra o guion bajo seguido de letras, dígitos o guiones bajos

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

# Nueva línea: actualiza el número de línea

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Operadores y símbolos

t_ASSIGN    = r':='
t_NE        = r'<>'
t_LE        = r'<='
t_GE        = r'>='
t_RANGE     = r'\.\.'

t_PLUS      = r'\+'
t_MINUS     = r'\-'
t_TIMES     = r'\*'
t_DIVISION  = r'/'
t_EQ        = r'='
t_LT        = r'<'
t_GT        = r'>'
t_LPAR      = r'\('
t_RPAR      = r'\)'
t_LBR       = r'\['
t_RBR       = r'\]'
t_DOT       = r'\.'
t_COMMA     = r','
t_SEMICOLON = r';'
t_COLON     = r':'

# Error léxico: muestra el carácter ilegal y continúa

def t_error(t):
    print(f"[ERROR LÉXICO] Línea {t.lexer.lineno}: carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Construye el lexer

lexer = lex.lex()
# main 

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'input.pas'
    with open(filename, 'r') as f:
        data = f.read()
    lexer.input(data)
    for tok in lexer:
        print(tok)