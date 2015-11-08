import unittest

import expressions

class MyTestCase(unittest.TestCase):

	def assertYields(self, function, input_values, expected_outputs):
		for i in range(len(input_values)):
			with self.subTest(i=i):
				self.assertEqual(function(*input_values[i]),
					expected_outputs[i])

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

	def test_is_valid(self):
		valid = ['3', '345', '0xff', '0xBEBADA', '3.0', '3.1416', '314.16e-2',
			'0.31416E1', '34e1', '.1']
		invalid = ['', '3 ', '11.45.2', 'abf']
		for s in valid:
			with self.subTest(expression=s):
				exp = expressions.NumeralExpression(s)
				self.assertTrue(exp.is_valid())
		for s in invalid:
			with self.subTest(expression=s):
				exp = expressions.NumeralExpression(s)
				self.assertFalse(exp.is_valid())

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
