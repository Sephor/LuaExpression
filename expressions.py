
import re

class AbstractExpression(object):

	def __init__(self, string):
		self.raw = string

	def is_valid(self):
		return False

	def evaluate(self):
		if self.is_valid:
			return self.evaluate_valid()

	def evaluate_valid(self):
		return None

#http://www.lua.org/manual/5.3/manual.html#3.4
class BasicExpression(AbstractExpression):
	re_validator = re.compile(r'(false)|(true)|(nil)')

	def is_valid(self):
		return self.re_validator.fullmatch(self.raw)

	def evaluate_valid(self):
		if self.raw == 'nil':
			return None
		return self.raw == 'true'


class NumeralExpression(AbstractExpression):
	#Does not accept fractional hex strings.
	re_int = re.compile(r'(\d+)')
	re_hex_int = re.compile(r'(0(x|X)[0-9a-fA-F]+)')
	re_float = re.compile(r'(\d*)(?P<dot>\.)?\d+' +
		r'(?(dot)((e|E)-?\d+)?|((e|E)-?\d+))')

	def is_int(self):
		return self.re_int.fullmatch(self.raw) != None

	def is_hex_int(self):
		return self.re_hex_int.fullmatch(self.raw) != None

	def is_float(self):
		return self.re_float.fullmatch(self.raw) != None

	def is_valid(self):
		return (self.is_int() or self.is_hex_int() or self.is_float())

	def evaluate_valid(self):
		if self.is_int():
			return int(self.raw)
		if self.is_hex_int():
			return int(self.raw, 0)
		if self.is_float():
			return float(self.raw)


class LiteralStringExpression(AbstractExpression):
	pass
