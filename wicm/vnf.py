class Vnf(object):
	""" Creating VNFs as object """
	def __init__(self,name):
		self.name = name
		self.floating = None
		self.vim = None
		self.hostname = None
		self.source = False
		self.target = None
		self.goes = None
		self.by = None

	def print(self):
		print ("name:"+self.name+", vim:"+self.vim+", hostname:"+self.hostname+", floating:"+self.floating)




