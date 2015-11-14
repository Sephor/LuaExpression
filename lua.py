from . import expressions

def is_valid(string):
	exp = expressions.GenericExpression(string)
	return exp.is_valid()

def evaluate(string):
	exp = expressions.GenericExpression(string)
	return exp.evaluate()
