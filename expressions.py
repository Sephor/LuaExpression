import re

class AbstractExpression(object):

	def __init__(self, string):
		self.raw = string.strip()
		self.invalid_exp = self #who's to blame if expression is invalid

	@classmethod
	def accepts(cls, string):
		exp = cls(string)
		return exp.is_valid()

	def invalid_reason(self):
		return 'Invalid {}: {}'.format(
			type(self.invalid_exp).__name__, self.invalid_exp.raw)

	def is_valid(self):
		return False

	def claims_valid(self):
		return self.is_valid()

	def evaluate(self):
		if self.is_valid():
			return self.evaluate_valid()
		raise Exception(self.invalid_reason())

	def evaluate_valid(self):
		return None


#http://www.lua.org/manual/5.3/manual.html#3.4
class BasicExpression(AbstractExpression):
	re_validator = re.compile(r'(false)|(true)|(nil)')

	def is_valid(self):
		return self.re_validator.fullmatch(self.raw) != None

	def evaluate_valid(self):
		if self.raw == 'nil':
			return None
		return self.raw == 'true'


class NumeralExpression(AbstractExpression):
	#Does not accept fractional hex strings (i.e. 0xABC.1Ep-2).
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
	#matches a string in the long bracket form
	re_long_bracket = re.compile(
		r'\[(?P<eq>=*)\[(?P<content>.*?[^\\])\](?P=eq)\]', re.S)
	#matches a string with single or double quotes
	re_quotes = re.compile(r"""(?P<qt>'|")(?P<content>.*?)(?<=[^\\])(?P=qt)"""
		, re.S)
	escape_map = {'n': '\n', 'r': '\r', 't': '\t', 'v': '\v'
		, '\\': '\\', '\"': '\"', '\'': '\''}
	#matches all lua escape sequences except \u{XXX}
	re_escape_sequence = re.compile(r'\\(?:(?P<dec>\d{1,3})|'
		+ '(?P<hex>x[0-9a-fA-F]{2})|(?P<char>[nrtv\\\"\']))')

	def has_quotes(self):
		match = self.re_quotes.match(self.raw)
		if match and match.end() == len(self.raw):
			self.content = match.group('content')
			return True
		return False

	def has_long_brackets(self):
		match = self.re_long_bracket.match(self.raw)
		if match and match.end() == len(self.raw):
			self.content = match.group('content')
			return True
		return False

	def is_valid(self):
		return self.has_quotes() or self.has_long_brackets()

	def find_content_and_type(self):
		self.has_quotes()
		is_raw = self.has_long_brackets()
		return (self.content, is_raw)

	def interpret_raw(self, content):
		if len(content) > 0 and content[0] == '\n':
			return content[1:]
		return content

	def escape_sequence(self, match):
		groups = match.groupdict()
		if groups['dec']:
			return chr(int(match.group('dec')))
		if groups['hex']:
			hex_number = match.group('hex')[1:]
			return chr(int(hex_number))
		if groups['char']:
			character = match.group('char')
			return self.escape_map[character]

	def interpret(self):
		temp = self.re_escape_sequence.sub(self.escape_sequence, self.content)
		return temp

	def evaluate_valid(self):
		content, is_raw = self.find_content_and_type()
		if is_raw:
			return self.interpret_raw(content)
		return self.interpret()


class PrefixExpression(AbstractExpression):
	#only supports prefixexp ::= ‘(’ exp ‘)’

	def is_valid(self):
		self.internal_exp = GenericExpression(self.raw[1:-1])
		return self.claims_valid() and self.internal_exp.is_valid()

	def claims_valid(self):
		return len(self.raw) >= 2 and self.raw[0] == '(' and self.raw[-1] == ')'

	def evaluate_valid(self):
		return self.internal_exp.evaluate()


class UnaryOperatorExpression(AbstractExpression):
	#only supports unary operators ‘-’ and ‘not’
	re_unop = re.compile(r'-|(not)')

	def is_valid(self):
		match = self.re_unop.match(self.raw)
		if match:
			self.unop = match.group(0)
			if self.unop == '-':
				self.expression = NumeralExpression(self.raw[1:])
				return self.expression.is_valid()
			if self.unop == 'not':
				self.expression = BasicExpression(self.raw[3:])
				return self.expression.is_valid()
		return False

	def evaluate_valid(self):
		if self.unop == '-':
			return - self.expression.evaluate()
		if self.unop == 'not':
			return not self.expression.evaluate()


class GenericExpression(AbstractExpression):
	known_expressions = [BasicExpression, NumeralExpression,
		LiteralStringExpression, TableConstructorExpression, PrefixExpression,
		UnaryOperatorExpression]

	def is_valid(self):
		for expression_type in self.known_expressions:
			exp = expression_type(self.raw)
			if exp.claims_valid():
				self.expression = exp
				self.invalid_exp = exp
				return self.expression.is_valid()
		return False

	def evaluate_valid(self):
		return self.expression.evaluate()
