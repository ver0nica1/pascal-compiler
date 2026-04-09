PROGRAM Factorial;

Var
  n        : INTEGER;
  resultado: integer;
  mensaje  : STRING;

(* Funcion que calcula el factorial de un numero *)
FUNCTION calcFactorial(num: integer): INTEGER;   
Var
  acum: integer;
  j   : integer;
Begin
  acum := 1;
  j    := 1;
  WHILE j <= num DO
  begin
    acum := acum * j;
    j    := j + 1;
  end;
  calcFactorial := acum; 
EnD;

BEGIN
  n := 5;
  resultado := 1;

  IF n < 0 then
  begin
    mensaje := 'Numero negativo';
  end
  ELSE IF n = 0 then
  Begin
    mensaje := 'Factorial es 1';
  End
  else
  begin
    resultado := calcFactorial(n);
  end;
  
  WriteLn(mensaje);
  IF n >= 0 THEN
    WriteLn('El factorial de ', n, ' es: ', resultado);

eNd.