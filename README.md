# Pyton-Lua-Parser
Module to evaluate most lua expressions in python.

##Limitations
The following Lua expressions can be evaluated:

	exp ::= prefixexp
	exp ::= nil | false | true
	exp ::= Numeral
	exp ::= LiteralString
	exp ::= tableconstructor
	exp ::= unop exp
	prefixexp ::= ‘(’ exp ‘)’

The following limitations apply:

* Numerals cannot be hexadecimal constants with fractional part or binary exponent
* unop can only be ‘-’ or ‘not’

##Usage
To check if a string is a valid expression use:
```
lua.is_valid(string)
```
returns True if the string is valid False otherwise.

To evaluate a string as a lua expression use:
```
lua.evaluate(string)
```
Lua tables are converted to lists of (key, value) pairs, nil evaluates to None, everything else evaluates as expected.
