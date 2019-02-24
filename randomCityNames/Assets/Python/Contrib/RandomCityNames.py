#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Random City Name Generator
# By: duckstab (James Conrad Shea)
#
# Markov Name generation based on public-domain code by Peter Corbett
# http://www.pick.ucam.org/~ptc24/mchain.html
###############################################################################

from CvPythonExtensions import *
from Markov import *
from CityNameLists import *
import BugData
import BugUtil

import string

gc = CyGlobalContext()

GENERATORS = {}

def rcnGetDataValue(key):
	counters = BugData.getGameData().getTable("RandomCityNames")
	if (not counters.hasTable(key)):
		result = None
	else:
		counter = counters.getTable(key)
		result = counter["val"]
	BugUtil.info("rcnGetDataValue(%s) => %s" % (key, result))
	return result

def rcnSetDataValue(key, value):
	BugUtil.info("rcnSetDataValue(%s, %s)" % (key, value))
	counters = BugData.getGameData().getTable("RandomCityNames")
	counter = counters.getTable(key)
	counter["val"] = value
	BugData.save()

class Generator(object):

	def __init__(self, civ, trainingSet):
		(self.minlen, self.maxlen) = limits(trainingSet)
		self.markov_chain = MarkovChain(trainingSet, self.maxlen)
		self.random = gc.getASyncRand()
		self.civ = civ
		GENERATORS[self.civ] = self

	def customize(self, result):
		base = result.title()
		res = u""
		for c in base:
			if res == u"'":
				res = res + c.capitalize()
			elif res.endswith(u"'"):
				res = res + c.lower()
			else:
				res = res + c
		return res

	def generate(self, previous_name=""):
		self.activate()
		result = ""
		# loopcount guarantees termination
		loopcount = 0
		while (len(result) < self.minlen or len(result) > self.maxlen) and loopcount < self.minlen:
			result = self.markov_chain.newName(previous_name)
			loopcount = loopcount + 1
		return self.customize(result)

	def activate(self):
		active_generators = rcnGetDataValue("ACTIVE_GENERATORS") or {}
		maxActive = 1 + gc.getGame().countCivPlayersEverAlive()
		if len(active_generators) < maxActive:
			active_generators[self.civ] = True
			rcnSetDataValue("ACTIVE_GENERATORS", active_generators)

	def choice(self, l):
		return l[self.random.get(len(l), "Generator.choice")]

	def force_case(self, name, *strs):
		for str in strs:
			upname = name.upper()
			upstr = str.upper()
			index = upname.find(upstr)
			length = len(str)
			while index >= 0:
				name = name[0:index] + str + name[index+length:]
				upname = upname[0:index] + str + upname[index+length:]
				index = upname.find(str, index + 1)
		return name

	def force_ending(self, result, trigger, choices):
		res = result
		index = result.find(trigger, 0)
		while index >= 0:
			words = result[index+len(trigger):].split()
			if not ends_with(words[0], choices):
				res = res.replace(words[0], words[0] + self.choice(choices))
			index = result.find(trigger, index + 1)
		return res

def ends_with(str, endings):
	for ending in endings:
		if str.endswith(ending):
			return True
	return False

def limits(trainingSet):
	mn = 30
	mx = 0
	for s in trainingSet:
		mn = min(mn, len(s))
		mx = max(mx, len(s))
	return (mn, mx)

def generate(city, previous_name=""):
	iCivilizationType = city.getCivilizationType()
	if (gc.getCivilizationInfo(iCivilizationType) != None):
		strCivilizationType = gc.getCivilizationInfo(iCivilizationType).getType()
		if GENERATORS.has_key(strCivilizationType):
			generator = GENERATORS[strCivilizationType]
			return generator.generate(previous_name)
	return city.getName()

def save_name(city, previous_owner):
	key = get_saved_name_key(city, previous_owner)
	rcnSetDataValue(key, city.getName())

def get_previous_name(city, previous_owner):
	return rcnGetDataValue(get_saved_name_key(city, previous_owner))

def get_saved_name_key(city, owner):
	x = city.getX()
	y = city.getY()
	key = "saved_name_%d_%d_%d" % (x, y, owner)
	return key

def rename(city, previous_owner, new_owner):
	save_name(city, previous_owner)
	name = get_previous_name(city, new_owner)
	if name is not None:
		return name
	else:
		return generate(city, city.getName())

class AmericanGenerator(Generator):

	def __init__(self, civ, trainingSet):
		super(AmericanGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_ending(res, 'Las ', ['as', 'es'])
		res = self.force_ending(res, 'Los ', ['es', 'os'])
		if res.startswith('Mc'):
			return 'Mc' + res[2:].title()
		else:
			return res

class EnglishGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(EnglishGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(res, " of ", " upon ", "-on-", "-under-")
		return res

class FrenchGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(FrenchGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(
			res,
			"-aux-", "-d'", "-de-", "-des-", "du", "-en-", "-et-", "-l'", "-la-", "-le-", "-les-", "-sous-",
			"-sur-", u"-lÃ¨s-"
		)
		res = self.force_ending(res, 'Les ', ['s', 'aux'])
		res = self.force_ending(res, '-aux-', ['s', 'aux'])
		res = self.force_ending(res, '-des-', ['s', 'aux'])
		res = self.force_ending(res, '-les-', ['s', 'aux'])
		return res

class GermanGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(GermanGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(res, " am ", " an ", " der ", " im ", " in ", " vor ")
		return res

class GreekGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(GreekGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_ending(res, u"Agía ", ["a", "i"])
		res = self.force_ending(res, u"Ágioi ", ["oi"])
		res = self.force_ending(res, u"Ágios ", ["is", "os"])
		res = self.force_ending(res, u"Néa ", [u"ós", "a", "i", u"ás"])
		res = self.force_ending(res, u"Néo ", [u"ó"])
		return res

class DutchGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(DutchGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(res, "'s-", " aan ", " bij ", " de ", " den ", " en ", "het ", " op ")
		res = res.replace("Ij", "IJ")
		return res

class PersianGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(PersianGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(res, "-e ", "-ye ", " va ")
		return res

class PortugueseGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(PortugueseGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(res, "-o-", " da ", " de ", " do ")
		return res

class RomanGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(RomanGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(res, "ad ", " apud ", " fluvium ", " super ")
		return res

class RussianGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(RussianGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_case(res, "-na-")
		return res

class SpanishGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(SpanishGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		res = Generator.customize(self, result)
		res = self.force_ending(res, "Las ", ["as", "es"])
		res = self.force_ending(res, "Los ", ["es", "os"])
		res = self.force_ending(res, "Dos ", ["as", "es", "os"])
		res = self.force_case(res, " de ", " del ", " el ", " i ", " la ", " las ", " los ")
		res = res.replace("L'h", "L'H")
		return res

class ZuluGenerator(Generator):
	def __init__(self, civ, trainingSet):
		super(ZuluGenerator, self).__init__(civ, trainingSet)

	def customize(self, result):
		if (result.startswith("Aba")
				or (result.startswith("Kwa") and self.random.get(14, "ZuluGenerator.customize") < 6)
		):
			return result[0:3] + Generator.customize(self, result[3:])
		elif result.startswith("e") or result.startswith("u"):
			return result[0:1] + Generator.customize(self, result[1:])
		else:
			return Generator.customize(self, result)

class BarbarianGenerator(Generator):
	def __init__(self, civ):
		super(BarbarianGenerator, self).__init__(civ, [])

	def generate(self, previous_name=""):
		self.activate()
		civ = self.choose_delegate()
		delegate = GENERATORS[civ]
		return delegate.generate(previous_name)

	def choose_delegate(self):
		active_generators = rcnGetDataValue("ACTIVE_GENERATORS") or {}
		civs = [civ for civ in GENERATORS.keys() if civ not in active_generators.keys()]
		if len(civs) == 0:
			civs = [civ for civ in GENERATORS.keys() if civ != self.civ]
		return self.choice(civs)


AMERICAN_GENERATOR = AmericanGenerator("CIVILIZATION_AMERICA", AMERICAN_CITIES)
ARABIAN_GENERATOR = Generator("CIVILIZATION_ARABIA", ARABIAN_CITIES)
AZTEC_GENERATOR = Generator("CIVILIZATION_AZTEC", AZTEC_CITIES)
BABYLONIAN_GENERATOR = Generator("CIVILIZATION_BABYLON", BABYLONIAN_CITIES)
BYZANTINE_GENERATOR = Generator("CIVILIZATION_BYZANTIUM", BYZANTINE_CITIES)
CARTHAGINIAN_GENERATOR = Generator("CIVILIZATION_CARTHAGE", CARTHAGINIAN_CITIES)
CELTIC_GENERATOR = Generator("CIVILIZATION_CELT", CELTIC_CITIES)
CHINESE_GENERATOR = Generator("CIVILIZATION_CHINA", CHINESE_CITIES)
EGYPTIAN_GENERATOR = Generator("CIVILIZATION_EGYPT", EGYPTIAN_CITIES)
ENGLISH_GENERATOR = EnglishGenerator("CIVILIZATION_ENGLAND", ENGLISH_CITIES)
ETHIOPIAN_GENERATOR = Generator("CIVILIZATION_ETHIOPIA", ETHIOPIAN_CITIES)
FRENCH_GENERATOR = FrenchGenerator("CIVILIZATION_FRANCE", FRENCH_CITIES)
GERMAN_GENERATOR = GermanGenerator("CIVILIZATION_GERMANY", GERMAN_CITIES)
GREEK_GENERATOR = GreekGenerator("CIVILIZATION_GREECE", GREEK_CITIES)
HOLY_ROMAN_GENERATOR = GermanGenerator("CIVILIZATION_HOLY_ROMAN", HOLY_ROMAN_CITIES)
INCA_GENERATOR = Generator("CIVILIZATION_INCA", INCA_CITIES)
INDIAN_GENERATOR = Generator("CIVILIZATION_INDIA", INDIAN_CITIES)
JAPANESE_GENERATOR = Generator("CIVILIZATION_JAPAN", JAPANESE_CITIES)
KHMER_GENERATOR = Generator("CIVILIZATION_KHMER", KHMER_CITIES)
KOREAN_GENERATOR = Generator("CIVILIZATION_KOREA", KOREAN_CITIES)
MALIAN_GENERATOR = Generator("CIVILIZATION_MALI", MALIAN_CITIES)
MAYA_GENERATOR = Generator("CIVILIZATION_MAYA", MAYA_CITIES)
MONGOL_GENERATOR = Generator("CIVILIZATION_MONGOL", MONGOL_CITIES)
NATIVE_AMERICAN_GENERATOR = Generator("CIVILIZATION_NATIVE_AMERICA", NATIVE_AMERICAN_CITIES)
DUTCH_GENERATOR = DutchGenerator("CIVILIZATION_NETHERLANDS", DUTCH_CITIES)
OTTOMAN_GENERATOR = Generator("CIVILIZATION_OTTOMAN", OTTOMAN_CITIES)
PERSIAN_GENERATOR = PersianGenerator("CIVILIZATION_PERSIA", PERSIAN_CITIES)
PORTUGUESE_GENERATOR = PortugueseGenerator("CIVILIZATION_PORTUGAL", PORTUGUESE_CITIES)
ROMAN_GENERATOR = RomanGenerator("CIVILIZATION_ROME", ROMAN_CITIES)
RUSSIAN_GENERATOR = RussianGenerator("CIVILIZATION_RUSSIA", RUSSIAN_CITIES)
SPANISH_GENERATOR = SpanishGenerator("CIVILIZATION_SPAIN", SPANISH_CITIES)
SUMERIAN_GENERATOR = Generator("CIVILIZATION_SUMERIA", SUMERIAN_CITIES)
VIKING_GENERATOR = Generator("CIVILIZATION_VIKING", VIKING_CITIES)
ZULU_GENERATOR = ZuluGenerator("CIVILIZATION_ZULU", ZULU_CITIES)
BARBARIAN_GENERATOR = BarbarianGenerator("CIVILIZATION_BARBARIAN")
