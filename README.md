# 🔬 Compilador Pascal

Compilador de subconjunto Pascal desarrollado en Python con PLY (Python Lex-Yacc). Implementa las tres fases clásicas de análisis de un compilador: **léxico**, **sintáctico** y **semántico**, con reporte detallado de errores y tabla de símbolos.

---

## 📁 Estructura del proyecto

```
.
├── lexer.py          # Analizador léxico
├── parser.py         # Analizador sintáctico (LALR(1))
├── semantico.py      # Analizador semántico
├── test.py           # Punto de entrada principal
└── input.pas         # Archivo Pascal de prueba (reemplazar con el propio)
```

---

## ⚙️ Requisitos

- Python 3.8 o superior
- PLY (Python Lex-Yacc)

```bash
pip install ply
```

---

## 🚀 Uso

```bash
python test.py <archivo.pas>
```

**Ejemplo:**

```bash
python test.py factorial.pas
```

Si no se pasa un archivo, el compilador busca `input.pas` en el directorio actual por defecto.

---

## 🧩 Fases del compilador

### [ 1 ] Análisis léxico — `lexer.py`

Tokeniza el código fuente y detecta caracteres ilegales. Reconoce:

- **35 palabras reservadas** de Pascal: `program`, `begin`, `end`, `if`, `then`, `else`, `while`, `for`, `repeat`, `until`, `case`, `function`, `procedure`, `var`, `const`, `type`, `array`, `record`, `set`, `file`, `packed`, `goto`, `label`, `with`, `and`, `or`, `not`, `div`, `mod`, `in`, `nil`, `do`, `to`, `downto`, `of`
- **Tipos de dato**: `integer`, `real`, `boolean`, `char`, `string`
- **Literales**: números enteros y reales (`42`, `3.14`, `1e5`), constantes de carácter (`'a'`, `'hola'`)
- **Operadores**: aritméticos, relacionales, lógicos, asignación (`:=`), rango (`..`)
- **Símbolos**: paréntesis, corchetes, punto, coma, dos puntos, punto y coma
- **Comentarios**: estilo `{ ... }` y `(* ... *)` — ignorados silenciosamente

---

### [ 2 ] Análisis sintáctico — `parser.py`

Parser LALR(1) construido con PLY que verifica la estructura gramatical del programa. Soporta:

- Estructura general: `program nombre; bloque.`
- Secciones de declaración: `label`, `const`, `type`, `var`
- Tipos: escalares, `array`, `record`, `set`, `file`, `packed`
- Sentencias: asignación, `if/else`, `while`, `for`, `repeat/until`, `case`, `goto`, `with`
- Subprogramas: `function` y `procedure` con parámetros tipados
- Expresiones: aritméticas, relacionales, lógicas, con precedencia correcta
- Constructores de conjuntos: `[a, b..c, d]`

**Recuperación de errores:** ante un error sintáctico el parser busca el siguiente `;`, `begin` o `end` para continuar el análisis y reportar todos los errores posibles en una sola pasada.

---

### [ 3 ] Análisis semántico — `semantico.py`

Opera en **dos pasadas** sobre la lista de tokens:

**Primera pasada — recolección de declaraciones:**
Recorre el código y construye la tabla de símbolos registrando variables, constantes, tipos, funciones y procedimientos con sus parámetros y tipos de retorno.

**Segunda pasada — verificación de uso:**
Recorre nuevamente el código verificando la corrección semántica.

#### Errores detectados

| Error | Descripción |
|---|---|
| Redeclaración | Variable, función o procedimiento declarado más de una vez |
| Variable sin declarar | Uso de un identificador que no aparece en ninguna sección `var` |
| Incompatibilidad de tipos en asignación | `contador := 'texto'` cuando `contador` es `integer` |
| Argumentos incorrectos | Llamada con distinto número de argumentos del esperado |
| Subprograma no declarado | Llamada a función o procedimiento inexistente |
| Variable de control inválida | Variable de `for` no declarada o de tipo distinto a `integer`/`char` |

#### Advertencias generadas

| Advertencia | Descripción |
|---|---|
| Variable no usada | Declarada en `var` pero nunca referenciada en el cuerpo |
| Función no llamada | Declarada pero nunca invocada |
| Procedimiento no llamado | Declarado pero nunca invocado |

#### Compatibilidad de tipos soportada

| Destino | Orígenes compatibles |
|---|---|
| `integer` | `integer` |
| `real` | `real`, `integer` (promoción implícita) |
| `boolean` | `boolean` |
| `char` | `char` |
| `string` | `string`, `char` |

#### Built-ins reconocidos

El analizador conoce los procedimientos y funciones estándar de Pascal y no los reporta como no declarados:

`writeln`, `write`, `readln`, `read`, `new`, `dispose`, `length`, `copy`, `concat`, `pos`, `chr`, `ord`, `abs`, `sqr`, `sqrt`, `trunc`, `round`, `succ`, `pred`, `odd`, `eof`, `eoln`, `reset`, `rewrite`, `close`, `upcase`, `lowercase`, `str`, `val`

---

## 📋 Ejemplo de salida

```
============================================================
  COMPILADOR PASCAL
  Archivo : factorial.pas
  Tokens  : 87    Líneas: 45
============================================================

           [ 1 ] ANÁLISIS LÉXICO
------------------------------------------------------------
  [OK] Sin errores léxicos.

         [ 2 ] ANÁLISIS SINTÁCTICO
------------------------------------------------------------
  [OK] Sin errores sintácticos.

          [ 3 ] ANÁLISIS SEMÁNTICO
------------------------------------------------------------
  [OK] Sin errores semánticos.

           [ 4 ] TABLA DE SÍMBOLOS
------------------------------------------------------------

  Variables globales: 3
    - n         : integer [✓ usada] (línea 4)
    - resultado : integer [✓ usada] (línea 5)
    - mensaje   : string  [✓ usada] (línea 6)

  Constantes: 0
  Tipos definidos: 0

  Funciones: 1
    - calcfactorial(num: integer) : integer [✓ usada] (línea 9)
        var acum : integer [✓ usada] (línea 11)
        var j    : integer [✓ usada] (línea 12)

  Procedimientos: 0

              [ RESUMEN FINAL ]
------------------------------------------------------------
  Errores léxicos    : 0
  Errores sintácticos: 0
  Errores semánticos : 0
  Advertencias       : 0
------------------------------------------------------------
  [OK] COMPILACIÓN EXITOSA — el código es correcto.
============================================================
```

---

## 🧪 Programa de prueba con errores semánticos

El repositorio incluye `prueba_semantica.pas`, un programa Pascal sintácticamente válido diseñado para disparar todos los tipos de errores y advertencias que detecta el analizador semántico:

```bash
python test.py prueba_semantica.pas
```

Errores que contiene deliberadamente:

1. Variable `x` declarada dos veces
2. Función `duplicada` declarada dos veces
3. Asignación de `string` a variable `integer`
4. Asignación de `real` a variable `boolean`
5. Uso de variable `noExiste` sin declarar
6. Llamada a `sumar` con 3 argumentos (espera 2)
7. Llamada a `funcionFantasma` (no declarada)
8. Variable de control `k` en `for` sin declarar

---

## 📐 Subconjunto de Pascal soportado

Este compilador implementa un subconjunto representativo de Pascal estándar. Lo que **sí** soporta:

- Programas completos con secciones `const`, `type`, `var`
- Funciones y procedimientos con parámetros y variables locales
- Todos los tipos escalares y estructurados básicos (`array`, `record`, `set`, `file`, `packed`)
- Todas las sentencias de control (`if`, `while`, `for`, `repeat`, `case`, `goto`, `with`)
- Expresiones con precedencia correcta, operador `in`, constructores de conjuntos
- Etiquetas numéricas (`label`) y sentencia `goto`

Lo que **no** soporta (fuera del alcance del proyecto):

- Punteros y tipos de acceso (`^`)
- Parámetros por referencia (`var` en parámetros)
- Unidades (`unit`) y módulos
- Generación de código intermedio o ejecutable

---

## 🛠️ Tecnologías

- **Python 3** — lenguaje de implementación
- **PLY 3.x** — librería de construcción de lexers y parsers LALR(1) para Python

---

## 👥 Autores

Proyecto desarrollado como entrega académica para el curso de **Compiladores** — Universidad Tecnológica de Pereira.
