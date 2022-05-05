class datum:
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return self.name

INITIAL_SCAN = datum('INITIAL_SCAN')
SENTINEL = datum('SENTINEL')
