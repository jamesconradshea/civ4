#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Markov chain for name generation
# By: duckstab (James Conrad Shea)
#
# Based on public-domain code by Peter Corbett
# http://www.pick.ucam.org/~ptc24/mchain.html
###############################################################################

from CvPythonExtensions import *

gc = CyGlobalContext()

class MarkovDict:
	def __init__(self):
		self.random = gc.getASyncRand()
		self.d = {}

	def __getitem__(self, key):
		if key in self.d:
			return self.d[key]
		else:
			raise KeyError(key)

	def add_key(self, prefix, suffix):
		key = tuple([c for c in prefix])
		if key in self.d:
			self.d[key].append(suffix)
		else:
			self.d[key] = [suffix]

	def get_suffix(self, prefix):
		key = tuple([c for c in prefix])
		l = self[key]
		return l[self.random.get(len(l), "MarkovDict.choice")]

class MarkovChain:
	"""
	A name from a Markov chain
	"""

	def __init__(self, trainingSet, maxlen, chainlen=2):
		"""
		Building the dictionary
		"""

		self.mcd = MarkovDict()
		#oldnames = []
		self.maxlen = maxlen
		self.chainlen = chainlen

		for l in trainingSet:
			#oldnames.append(l)
			s = unicode("_" * chainlen) + l
			for n in range(0, len(l)):
				self.mcd.add_key(s[n:n + chainlen], s[n + chainlen])
			self.mcd.add_key(s[len(l):len(l) + chainlen], "\n")

	def newName(self, oldname=""):
		"""
		New name from the Markov chain
		"""
		prefix = unicode("_" * self.chainlen)
		name = u""
		basis = oldname
		while True:
			suffix = None
			if len(basis) > 0:
				key = tuple([c for c in prefix])
				if key in self.mcd.d:
					choices = self.mcd.d[key]
					for i in range(0, len(basis)):
						if basis[i] in choices:
							suffix = basis[i]
							basis = basis[i+1:]
							break
			if suffix is None:
			suffix = self.mcd.get_suffix(prefix)
			if suffix == "\n" or len(name) > self.maxlen:
				break
			else:
				name = name + suffix
				prefix = prefix[1:] + suffix
		return name


