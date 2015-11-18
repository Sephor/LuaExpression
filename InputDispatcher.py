import re
import expressions


class DefaultReadState(object):
	state_map = {
		'"': 
	}

	@classmethod
	def evaluate(cls, char):
		pass

class InputDispatcher(object):

	def __init__(self, string):
		self.raw = string
		self.expression_stack = []

	def evaluate(self):
		pass
