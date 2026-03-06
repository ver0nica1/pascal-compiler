program prueba_completa;

{ Este es un comentario con llaves }
(* Este es un comentario con parentesis y asterisco *)

const
    MAX = 100;
    PI  = 3.14159;
    MENSAJE = 'Hola Mundo';

type
    rango = array[1..10] of integer;

var
    x, y    : integer;
    z       : real;
    bandera : boolean;
    letra   : char;
    nombre  : string;
    lista   : array[1..MAX] of integer;

{ ------ PROCEDIMIENTO ------ }
procedure sumar(a, b : integer);
var
    resultado : integer;
begin
    resultado := a + b
end;

{ ------ FUNCION ------ }
function multiplicar(a, b : integer) : integer;
begin
    multiplicar := a * b
end;

{ ------ PROGRAMA PRINCIPAL ------ }
begin

    { Asignaciones basicas }
    x := 10;
    y := 3;
    z := 2.5;
    bandera := true;
    letra   := 'A';
    nombre  := 'Pascal';

    { Operadores aritmeticos }
    x := x + y;
    x := x - y;
    x := x * y;
    z := z / 2.0;
    x := x div y;
    x := x mod y;

    { Operadores relacionales }
    if x = y then
        bandera := true
    else
        bandera := false;

    if x <> y then
        x := x + 1;

    if x < y then
        x := 0;

    if x > y then
        x := 1;

    if x <= y then
        x := 2;

    if x >= y then
        x := 3;

    { Operadores logicos }
    if (x > 0) and (y > 0) then
        bandera := true;

    if (x = 0) or (y = 0) then
        bandera := false;

    if not bandera then
        x := 99;

    { Estructura WHILE }
    while x > 0 do
    begin
        x := x - 1
    end;

    { Estructura FOR }
    for x := 1 to 10 do
    begin
        lista[x] := x * 2
    end;

    { FOR con DOWNTO }
    for x := 10 downto 1 do
    begin
        lista[x] := 0
    end;

    { Estructura REPEAT UNTIL }
    repeat
        x := x + 1
    until x = 10;

    { Estructura CASE }
    case x of
        1 : y := 10;
        2 : y := 20;
        3 : y := 30
    end;

    { Llamadas a subprogramas }
    sumar(3, 5);
    y := multiplicar(4, 6);

    { Uso de NIL y punteros basicos }
    if nombre = nil then
        x := 0;

    { Uso de IN y SET }
    if x in [1, 2, 3] then
        y := 1;

    { Uso de WITH y RECORD }
    { (sintaxis referencial, no ejecutable sin definicion de record) }

    { Numeros reales y notacion cientifica }
    z := 1.5e10;
    z := 3.0e-5;

    { GOTO y LABEL }
    label salida;
    goto salida;
    salida:
        x := 0

end.