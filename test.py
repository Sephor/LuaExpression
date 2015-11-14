import unittest

from . import expressions

class MyTestCase(unittest.TestCase):

	def assertYields(self, function, input_values, expected_outputs, msg=None):
		for i in range(len(input_values)):
			result = function(*input_values[i])
			if result != expected_outputs[i]:
				msg = self._formatMessage(msg,
					'at index {}: {} of {} did not yield "{}" but "{}"'.format(
						i, function.__name__, input_values[i],
						expected_outputs[i], result))
				raise self.failureException(msg)


class TestBasicExpressions(unittest.TestCase):

	def test_is_valid(self):
		valid = ['false', 'true', 'nil']
		invalid = ['False', '1', '']
		for s in valid:
			with self.subTest(expression=s):
				exp = expressions.BasicExpression(s)
				self.assertTrue(exp.is_valid())
		for s in invalid:
			with self.subTest(expression=s):
				exp = expressions.BasicExpression(s)
				self.assertFalse(exp.is_valid())

	def test_evaluate_valid(self):
		values = [('false', False), ('true', True)]
		for s, value in values:
			with self.subTest(expression=s, value=value):
				exp = expressions.BasicExpression(s)
				self.assertEqual(exp.evaluate_valid(), value)
		exp = expressions.BasicExpression('nil')
		self.assertIsNone(exp.evaluate_valid())


class TestNumeralExpression(MyTestCase):

	def is_valid(self, *s):
		s = ''.join(s)
		exp = expressions.NumeralExpression(s)
		return exp.is_valid()

	def test_is_valid(self):
		valid = ['3', '345', '0xff', '0xBEBADA', '3.0', '3.1416', '314.16e-2',
			'0.31416E1', '34e1', '.1']
		invalid = ['', '3_', '11.45.2', 'abf']
		self.assertYields(self.is_valid, valid, [True] * len(valid))
		self.assertYields(self.is_valid, invalid, [False] * len(invalid))

	def evaluate_valid(self, *s):
		s = ''.join(s)
		exp = expressions.NumeralExpression(s)
		return exp.evaluate_valid()

	def test_evaluate_valid(self):
		input_values = ['3', '345', '0xff', '0xBEBADA', '3.0', '3.1416',
			'314.16e-2', '0.31416E1', '34e1', '.1']
		expected_outputs = [3, 345, 255, 12499674, 3.0, 3.1416, 3.1416, 3.1416,
			340.0, 0.1]
		self.assertYields(self.evaluate_valid, input_values, expected_outputs)


class TestLiteralStringExpression(MyTestCase):

	def is_valid(self, *s):
		s = ''.join(s)
		exp = expressions.LiteralStringExpression(s)
		return exp.is_valid()

	def test_is_valid(self):
		valid = ['""', "''", r"""'alo\n123"'""", r'"alo\n123\""',
			r"""'\97lo\10\04923"'""", '[[alo\n123"]]', '[==[\nalo\n123"]==]']
		invalid = ['"\'', "'''", '[=[foo]==]', '[=[bar]]', r'"\"']
		self.assertYields(self.is_valid, valid, [True] * len(valid))
		self.assertYields(self.is_valid, invalid, [False] * len(invalid))

	def evaluate_valid(self, *s):
		s = ''.join(s)
		exp = expressions.LiteralStringExpression(s)
		return exp.evaluate_valid()

	def test_evaluate_valid(self):
		input_values = ['""', "''", r"""'alo\n123"'""", r'"alo\n123\""',
			r"""'\97lo\10\04923"'""", '[[alo\n123"]]', '[==[\nalo\n123"]==]']
		expected_outputs = ['', '',] + ['alo\n123"'] * 5
		self.assertYields(self.evaluate_valid, input_values, expected_outputs)

class TestGenericExpression(MyTestCase):

	def is_valid(self, *s):
		s = ''.join(s)
		exp = expressions.GenericExpression(s)
		return exp.is_valid()

	def test_is_valid(self):
		valid = ['"foo"', '234', 'false']
		invalid = ['', '1.1.1', 'abc']
		self.assertYields(self.is_valid, valid, [True] * len(valid))
		self.assertYields(self.is_valid, invalid, [False] * len(invalid))

	def evaluate(self, *s):
		s = ''.join(s)
		exp = expressions.GenericExpression(s)
		return exp.evaluate()

	def test_evaluate(self):
		input_values = ['"foo"', '234', 'false']
		expected_outputs = ['foo', 234, False]
		self.assertYields(self.evaluate, input_values, expected_outputs)


class TestTableConstructorExpression(MyTestCase):

	def is_valid(self, *s):
		s = ''.join(s)
		exp = expressions.TableConstructorExpression(s)
		return exp.is_valid()

	def test_is_valid(self):
		valid = ['{}', '{1,2,3}', '{ 1\t;2,\n3}', "{['a'] = 1.1}", '{{},{}}',
			'{\n{foo = \n"bar",\n\t bar = "foo"}}']
		invalid = ['{{}', '{1 1 2}', '[]']
		self.assertYields(self.is_valid, valid, [True] * len(valid))
		self.assertYields(self.is_valid, invalid, [False] * len(invalid))

	def evaluate(self, *s):
		s = ''.join(s)
		exp = expressions.TableConstructorExpression(s)
		return exp.evaluate()

	def test_evaluate(self):
		input_values = ['{}', '{1,2,3}', '{ 1\t;2,\n3}', "{['a'] = 1.1}"
			, '{{}}']
		expected_outputs = [[], [(1, 1), (2, 2), (3, 3)]
			, [(1, 1), (2, 2), (3, 3)], [('a', 1.1)], [(1, [])]]
		self.assertYields(self.evaluate, input_values, expected_outputs)


class TestPrefixExpression(MyTestCase):

	def is_valid(self, *s):
		s = ''.join(s)
		exp = expressions.PrefixExpression(s)
		return exp.is_valid()

	def test_is_valid(self):
		valid = ['("hello")', '(123)', '(nil)']
		invalid = ['()', '((123)', '']
		self.assertYields(self.is_valid, valid, [True] * len(valid))
		self.assertYields(self.is_valid, invalid, [False] * len(invalid))

	def evaluate(self, *s):
		s = ''.join(s)
		exp = expressions.PrefixExpression(s)
		return exp.evaluate()

	def test_evaluate(self):
		input_values = ['("hello")', '(123)', '(nil)']
		expected_outputs = ['hello', 123, None]
		self.assertYields(self.evaluate, input_values, expected_outputs)

class TestUnaryOperatorExpression(MyTestCase):

	def is_valid(self, *s):
		s = ''.join(s)
		exp = expressions.UnaryOperatorExpression(s)
		return exp.is_valid()

	def test_is_valid(self):
		valid = ['-1', '-1.234', 'not true', 'not nil']
		invalid = ['-"hello"', '-nil', '123']
		self.assertYields(self.is_valid, valid, [True] * len(valid))
		self.assertYields(self.is_valid, invalid, [False] * len(invalid))

	def evaluate(self, *s):
		s = ''.join(s)
		exp = expressions.UnaryOperatorExpression(s)
		return exp.evaluate()

	def test_evaluate(self):
		input_values = ['-1', '-1.234', 'not true', 'not nil']
		expected_outputs = [-1, -1.234, False, True]
		self.assertYields(self.evaluate, input_values, expected_outputs)
