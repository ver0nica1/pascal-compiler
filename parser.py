import ply.yacc as yacc
from lexer import tokens
import lexer as pascal_lexer
import sys

VERBOSE = 1

# ==============================================================
#   PROGRAMA
# ==============================================================

def p_program(p):
    'program : PROGRAM ID SEMICOLON block DOT'
    pass

# ==============================================================
#   BLOQUE PRINCIPAL
#   Un bloque puede tener (en orden): label, const, type, var,
#   declaraciones de subprogramas, y el cuerpo (begin...end)
# ==============================================================

def p_block(p):
    'block : label_part const_part type_part var_part subprogram_declarations compound_stmt'
    pass

# ==============================================================
#   SECCIÓN LABEL  (puede estar vacía)
#   label 1, 2, 3;
# ==============================================================

def p_label_part_1(p):
    'label_part : LABEL label_list SEMICOLON'
    pass

def p_label_part_2(p):
    'label_part : empty'
    pass

def p_label_list_1(p):
    'label_list : label_list COMMA NUMBER'
    pass

def p_label_list_2(p):
    'label_list : NUMBER'
    pass

# ==============================================================
#   SECCIÓN CONST  (puede estar vacía)
# ==============================================================

def p_const_part_1(p):
    'const_part : CONST const_list'
    pass

def p_const_part_2(p):
    'const_part : empty'
    pass

def p_const_list_1(p):
    'const_list : const_list const_def'
    pass

def p_const_list_2(p):
    'const_list : const_def'
    pass

def p_const_def(p):
    'const_def : ID EQ literal SEMICOLON'
    pass

# ==============================================================
#   SECCIÓN TYPE  (puede estar vacía)
# ==============================================================

def p_type_part_1(p):
    'type_part : TYPE type_list'
    pass

def p_type_part_2(p):
    'type_part : empty'
    pass

def p_type_list_1(p):
    'type_list : type_list type_def'
    pass

def p_type_list_2(p):
    'type_list : type_def'
    pass

def p_type_def(p):
    'type_def : ID EQ type_specifier SEMICOLON'
    pass

# ==============================================================
#   SECCIÓN VAR  (puede estar vacía)
# ==============================================================

def p_var_part_1(p):
    'var_part : VAR var_declaration_list'
    pass

def p_var_part_2(p):
    'var_part : empty'
    pass

def p_var_declaration_list_1(p):
    'var_declaration_list : var_declaration_list var_declaration'
    pass

def p_var_declaration_list_2(p):
    'var_declaration_list : var_declaration'
    pass

# Una declaración de variable: x, y, z : integer;
def p_var_declaration(p):
    'var_declaration : id_list COLON type_specifier SEMICOLON'
    pass

# Lista de identificadores separados por comas: a, b, c
def p_id_list_1(p):
    'id_list : id_list COMMA ID'
    pass

def p_id_list_2(p):
    'id_list : ID'
    pass

# ==============================================================
#   TIPOS  (integer, real, boolean, char, string,
#           array, record, set, file, packed)
# ==============================================================

def p_type_specifier_integer(p):
    'type_specifier : INTEGER'
    pass

def p_type_specifier_real(p):
    'type_specifier : REAL'
    pass

def p_type_specifier_boolean(p):
    'type_specifier : BOOLEAN'
    pass

def p_type_specifier_char(p):
    'type_specifier : CHAR'
    pass

def p_type_specifier_string(p):
    'type_specifier : STRING'
    pass

# array [1..10] of integer
def p_type_specifier_array(p):
    'type_specifier : ARRAY LBR NUMBER RANGE NUMBER RBR OF type_specifier'
    pass

# record  field1: type1; field2: type2; ... end
def p_type_specifier_record(p):
    'type_specifier : RECORD field_list END'
    pass

# set of type
def p_type_specifier_set(p):
    'type_specifier : SET OF type_specifier'
    pass

# file of type
def p_type_specifier_file(p):
    'type_specifier : FILE OF type_specifier'
    pass

# file sin tipo (archivo de texto genérico)
def p_type_specifier_file_plain(p):
    'type_specifier : FILE'
    pass

# packed array / packed record / packed set / packed file
def p_type_specifier_packed(p):
    'type_specifier : PACKED type_specifier'
    pass

# Identificador como tipo (tipos definidos por el usuario)
def p_type_specifier_id(p):
    'type_specifier : ID'
    pass

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
#   DECLARACIONES DE SUBPROGRAMAS (FUNCTION y PROCEDURE)
#   Pueden ser cero o muchas, antes del begin principal
# ==============================================================

def p_subprogram_declarations_1(p):
    'subprogram_declarations : subprogram_declarations subprogram_declaration'
    pass

def p_subprogram_declarations_2(p):
    'subprogram_declarations : empty'
    pass

def p_subprogram_declaration_function(p):
    'subprogram_declaration : function_declaration'
    pass

def p_subprogram_declaration_procedure(p):
    'subprogram_declaration : procedure_declaration'
    pass

# --------------------------------------------------------------
#   FUNCTION:  function nombre(params): tipo; var... begin...end;
# --------------------------------------------------------------

def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAR params RPAR COLON type_specifier SEMICOLON subblock SEMICOLON'
    pass

# --------------------------------------------------------------
#   PROCEDURE: procedure nombre(params); var... begin...end;
# --------------------------------------------------------------

def p_procedure_declaration(p):
    'procedure_declaration : PROCEDURE ID LPAR params RPAR SEMICOLON subblock SEMICOLON'
    pass

# Sub-bloque: sección label + var opcionales + cuerpo
def p_subblock(p):
    'subblock : label_part var_part compound_stmt'
    pass

# ==============================================================
#   PARÁMETROS
# ==============================================================

def p_params_1(p):
    'params : param_list'
    pass

def p_params_2(p):
    'params : empty'
    pass

def p_param_list_1(p):
    'param_list : param_list SEMICOLON param'
    pass

def p_param_list_2(p):
    'param_list : param'
    pass

# num: integer
def p_param(p):
    'param : id_list COLON type_specifier'
    pass

# ==============================================================
#   CUERPO:  begin  sentencias  end
# ==============================================================

def p_compound_stmt(p):
    'compound_stmt : BEGIN statement_list END'
    pass

def p_statement_list_1(p):
    'statement_list : statement_list SEMICOLON statement'
    pass

def p_statement_list_2(p):
    'statement_list : statement'
    pass

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
    pass

# --------------------------------------------------------------
#   ASIGNACIÓN:   variable := expresion
# --------------------------------------------------------------

def p_assignment_stmt(p):
    'assignment_stmt : variable ASSIGN expression'
    pass

# --------------------------------------------------------------
#   IF / IF-ELSE
# --------------------------------------------------------------

def p_if_stmt_1(p):
    'if_stmt : IF expression THEN statement'
    pass

def p_if_stmt_2(p):
    'if_stmt : IF expression THEN statement ELSE statement'
    pass

# --------------------------------------------------------------
#   WHILE
# --------------------------------------------------------------

def p_while_stmt(p):
    'while_stmt : WHILE expression DO statement'
    pass

# --------------------------------------------------------------
#   FOR
# --------------------------------------------------------------

def p_for_stmt_1(p):
    'for_stmt : FOR ID ASSIGN expression TO expression DO statement'
    pass

def p_for_stmt_2(p):
    'for_stmt : FOR ID ASSIGN expression DOWNTO expression DO statement'
    pass

# --------------------------------------------------------------
#   REPEAT ... UNTIL
# --------------------------------------------------------------

def p_repeat_stmt(p):
    'repeat_stmt : REPEAT statement_list UNTIL expression'
    pass

# --------------------------------------------------------------
#   CASE
#   case expresion of
#     valor1 : sentencia;
#     valor2 : sentencia;
#     else     sentencia     (rama else opcional)
#   end
# --------------------------------------------------------------

def p_case_stmt_1(p):
    'case_stmt : CASE expression OF case_list END'
    pass

def p_case_stmt_2(p):
    'case_stmt : CASE expression OF case_list ELSE statement END'
    pass

def p_case_list_1(p):
    'case_list : case_list case_element'
    pass

def p_case_list_2(p):
    'case_list : case_element'
    pass

# Un elemento de case: valor (o lista de valores) : sentencia ;
def p_case_element(p):
    'case_element : case_label_list COLON statement SEMICOLON'
    pass

def p_case_label_list_1(p):
    'case_label_list : case_label_list COMMA literal'
    pass

def p_case_label_list_2(p):
    'case_label_list : literal'
    pass

# --------------------------------------------------------------
#   GOTO
#   goto <etiqueta numérica>
# --------------------------------------------------------------

def p_goto_stmt(p):
    'goto_stmt : GOTO NUMBER'
    pass

# --------------------------------------------------------------
#   Sentencia etiquetada:  <número> : sentencia
# --------------------------------------------------------------

def p_labeled_stmt(p):
    'labeled_stmt : NUMBER COLON statement'
    pass

# --------------------------------------------------------------
#   WITH
#   with registro do sentencia
# --------------------------------------------------------------

def p_with_stmt(p):
    'with_stmt : WITH variable_list DO statement'
    pass

def p_variable_list_1(p):
    'variable_list : variable_list COMMA variable'
    pass

def p_variable_list_2(p):
    'variable_list : variable'
    pass

# --------------------------------------------------------------
#   LLAMADA A PROCEDIMIENTO:  nombre(args)  o  nombre  (sin args)
# --------------------------------------------------------------

def p_procedure_call_stmt_1(p):
    'procedure_call_stmt : ID LPAR args RPAR'
    pass

def p_procedure_call_stmt_2(p):
    'procedure_call_stmt : ID'
    pass

# ==============================================================
#   VARIABLE (para el lado izquierdo de asignaciones)
# ==============================================================

def p_variable_simple(p):
    'variable : ID'
    pass

def p_variable_array(p):
    'variable : ID LBR expression RBR'
    pass

# Acceso a campo de record:  registro.campo
def p_variable_field(p):
    'variable : variable DOT ID'
    pass

# ==============================================================
#   EXPRESIONES
# ==============================================================

def p_expression_relop(p):
    'expression : simple_expression relop simple_expression'
    pass

def p_expression_simple(p):
    'expression : simple_expression'
    pass

# Operador IN:  expresion IN set_constructor
def p_expression_in(p):
    'expression : simple_expression IN set_constructor'
    pass

def p_relop(p):
    '''relop : EQ
             | NE
             | LT
             | GT
             | LE
             | GE
    '''
    pass

def p_simple_expression_addop(p):
    'simple_expression : simple_expression addop term'
    pass

def p_simple_expression_term(p):
    'simple_expression : term'
    pass

def p_addop(p):
    '''addop : PLUS
             | MINUS
             | OR
    '''
    pass

def p_term_mulop(p):
    'term : term mulop factor'
    pass

def p_term_factor(p):
    'term : factor'
    pass

def p_mulop(p):
    '''mulop : TIMES
             | DIVISION
             | DIV
             | MOD
             | AND
    '''
    pass

def p_factor_number(p):
    'factor : NUMBER'
    pass

def p_factor_charconst(p):
    'factor : CHARCONST'
    pass

# NIL (puntero nulo)
def p_factor_nil(p):
    'factor : NIL'
    pass

def p_factor_variable(p):
    'factor : variable'
    pass

def p_factor_call(p):
    'factor : ID LPAR args RPAR'
    pass

def p_factor_paren(p):
    'factor : LPAR expression RPAR'
    pass

def p_factor_not(p):
    'factor : NOT factor'
    pass

# Constructor de SET:  [1, 2, 3..5, x]
def p_factor_set(p):
    'factor : set_constructor'
    pass

# ==============================================================
#   CONSTRUCTOR DE SET   [ elem, elem, ... ]
# ==============================================================

def p_set_constructor_1(p):
    'set_constructor : LBR set_element_list RBR'
    pass

def p_set_constructor_2(p):
    'set_constructor : LBR RBR'
    pass

def p_set_element_list_1(p):
    'set_element_list : set_element_list COMMA set_element'
    pass

def p_set_element_list_2(p):
    'set_element_list : set_element'
    pass

# Un elemento puede ser un valor simple o un rango  a..b
def p_set_element_range(p):
    'set_element : expression RANGE expression'
    pass

def p_set_element_single(p):
    'set_element : expression'
    pass

# ==============================================================
#   ARGUMENTOS DE LLAMADA A FUNCIÓN/PROCEDIMIENTO
# ==============================================================

def p_args_1(p):
    'args : args_list'
    pass

def p_args_2(p):
    'args : empty'
    pass

def p_args_list_1(p):
    'args_list : args_list COMMA expression'
    pass

def p_args_list_2(p):
    'args_list : expression'
    pass

# ==============================================================
#   LITERALES  (usados en const y expresiones)
# ==============================================================

def p_literal_number(p):
    'literal : NUMBER'
    pass

def p_literal_charconst(p):
    'literal : CHARCONST'
    pass

# ==============================================================
#   PRODUCCIÓN VACÍA
# ==============================================================

def p_empty(p):
    'empty :'
    pass

# ==============================================================
#   MANEJO DE ERRORES
# ==============================================================

errors_list = []

def p_error(p):
    global errors_list
    if p is not None:
        # Mostramos exactamente cuál fue el token que causó el problema
        msg = f"ERROR SINTÁCTICO en la línea {p.lineno}: no se esperaba el token '{p.value}'"
        
        # Evitar inundar la pantalla con muchos errores en la misma línea
        if not any(f"línea {p.lineno}:" in e for e in errors_list):
            errors_list.append(msg)
            
        # Recuperación modo pánico: buscamos el siguiente ';' o palabra clave importante
        while True:
            tok = parser.token()
            if not tok or tok.type in ['SEMICOLON', 'BEGIN', 'END']:
                break
        parser.errok()
    else:
        # El usuario solicitó omitir el error de fin de archivo inesperado
        pass

# ==============================================================
#   CONSTRUCCIÓN DEL PARSER
# ==============================================================

parser = yacc.yacc()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        fin = sys.argv[1]
    else:
        fin = 'input.pas'

    f = open(fin, 'r', encoding='utf-8', errors='ignore')
    data = f.read()
    total_lines = len(data.splitlines())
    
    pascal_lexer.lexer_errors = []
    
    parser.parse(data, lexer=pascal_lexer.lexer, tracking=True)
    
    all_errors = pascal_lexer.lexer_errors + errors_list
    
    if len(all_errors) == 0:
        print(f"\nSe analizaron {total_lines} líneas correctamente.")
        print("[OK] El parser reconoció correctamente el programa Pascal")
    else:
        print(f"\nSe analizaron {total_lines} líneas.")
        print(f"Se encontraron {len(all_errors)} error(es):")
        for err in all_errors:
            print(f" - {err}")