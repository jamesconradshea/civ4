#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Random Name Generator
# By: The Lopez
# 
# Refactored by duckstab (James Conrad Shea)
#
# Markov Name generation based on public-domain code by Peter Corbett
# http://www.pick.ucam.org/~ptc24/mchain.html
###############################################################################

from CvPythonExtensions import *

import CvUtil
import sys
import math
import string
import BugData
import BugUtil

from Markov import *

gc = CyGlobalContext()  

def getDataValue(key):
	counters = BugData.getGameData().getTable("RandomNameUtils")
	if (not counters.hasTable(key)):
		counter = counters.getTable(key)
		result = None
	else:
		counter = counters.getTable(key)
		result = counter["val"]
	return result

def setDataValue(key, value):
	BugUtil.debug("setDataValue(%s, %s)" % (key, value))
	counters = BugData.getGameData().getTable("RandomNameUtils")
	counter = counters.getTable(key)
	counter["val"] = value
	BugData.save()

class Generator(object):

	def __init__(self, mFirst, fFirst, mMiddle, fMiddle, last):
		self.random = gc.getASyncRand()
		self.masculineFirstNames = mFirst
		self.feminineFirstNames = fFirst
		self.masculineMiddleNames = mMiddle
		self.feminineMiddleNames = fMiddle
		self.surnames = last

	def choice(self, l):
		return l[self.random.get(len(l), "Generator.choice")]

	def generateInternal(self, firstNames, middleNames, lastNames):
		unitName = ""

		firstName = self.choice(firstNames)
		middleName = self.choice(middleNames)
		lastName = self.choice(lastNames)

		unitName = firstName + " " + lastName

		if (len(unitName) < 14 and firstName != middleName and middleName != lastName):
			unitName = firstName + " " + middleName + " " + lastName

		return unitName

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			return self.generateInternal(self.masculineFirstNames, self.masculineMiddleNames, self.surnames)
		else:
			return self.generateInternal(self.feminineFirstNames, self.feminineMiddleNames, self.surnames)

	def activate(self, civName):
		self.civ = civName
		active_generators = getDataValue("ACTIVE_GENERATORS") or {}
		active_generators[self.civ] = True
		setDataValue("ACTIVE_GENERATORS", active_generators)


class ArabianGenerator(Generator):

	def generateInternal2(self, firstNames, mnPrefix, middleNames, lastNames):
		unitName = ""

		firstName = self.choice(firstNames)
		middleName = mnPrefix + self.choice(middleNames)
		lastName = "al " + self.choice(lastNames)

		unitName = firstName + " " + lastName

		if (len(unitName) < 17 and firstName != middleName and middleName != lastName):
			unitName = firstName + " " + middleName + " " + lastName

		return unitName

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			return self.generateInternal2(self.masculineFirstNames, "ibn ", self.masculineMiddleNames, self.surnames)
		else:
			return self.generateInternal2(self.feminineFirstNames, "bint ", self.feminineMiddleNames, self.surnames)

class AztecGenerator(Generator):

	def __init__(self, mFirst, fFirst, numerals):
		super(AztecGenerator, self).__init__(mFirst, fFirst, [], [], [])
		self.numerals = numerals

	def generateInternal(self, firstNames, middleNames, lastNames):
		unitName = ""

		firstName = self.choice(firstNames)
		lastName = self.choice(firstNames)
		while firstName == lastName:
			lastName = self.choice(firstNames)

		unitName = self.replaceNumeral(firstName) + " " + self.replaceNumeral(lastName)

		return unitName

	def replaceNumeral(self, s):
		numeral = self.choice(self.numerals)
		return string.replace(s, "_N_", numeral)

class SimplifiedGenerator(Generator):

	def __init__(self, mFirst, fFirst):
		super(SimplifiedGenerator, self).__init__(mFirst, fFirst, [], [], [])

	def generateInternal(self, firstNames, middleNames, lastNames):
		unitName = ""

		firstName = self.choice(firstNames)
		lastName = self.choice(firstNames)
		while firstName == lastName:
			lastName = self.choice(firstNames)

		unitName = firstName + " " + lastName

		return unitName


class MarkovGenerator(Generator):

	def __init__(self, mFirst, fFirst, mMiddle, fMiddle, last, minlen, maxlen):
		super(MarkovGenerator, self).__init__(mFirst, fFirst, mMiddle, fMiddle, last)
		self.mcMFirst = MarkovChain(mFirst, maxlen)
		self.mcFFirst = MarkovChain(fFirst, maxlen)
		if mMiddle is None:
			self.mcMMiddle = self.mcMFirst
		else:
			self.mcMMiddle = MarkovChain(mMiddle, maxlen)
		if fMiddle is None:
			self.mcFMiddle = self.mcFFirst
		else:
			self.mcFMiddle = MarkovChain(fMiddle, maxlen)
		self.mcLast = MarkovChain(last, maxlen)
		self.minlen = minlen
		self.maxlen = maxlen

	def generateComponent(self, mc):
		component = ""
		# loopcounter ensures termination
		loopcounter = 0
		while ((len(component) < self.minlen or len(component) > self.maxlen) and loopcounter < self.minlen):
			component = mc.newName().title()
			loopcounter = loopcounter + 1
		return component

	def generateMarkov(self, mcf, mcm, mcl):
		firstName = self.generateComponent(mcf)
		middleName = self.generateComponent(mcm)
		lastName = self.generateComponent(mcl)

		unitName = firstName + " " + lastName

		if (len(unitName) < (self.minlen + self.maxlen) and firstName != middleName and middleName != lastName):
			unitName = firstName + " " + middleName + " " + lastName

		return unitName


	def generate(self, pUnit, pCity, masculine):
		if masculine:
			return self.generateMarkov(self.mcMFirst, self.mcMMiddle, self.mcLast)
		else:
			return self.generateMarkov(self.mcFFirst, self.mcFMiddle, self.mcLast)


M_FIRST_AMERICAN = [
	"Aaron", "Alan", "Albert", "Alexander", "Alfred", "Allen", "Andrew", "Anthony", "Archie", "Arthur", "August", "Benjamin", "Bernard", "Bert", "Billy", "Bobby", "Bradley", "Brian", "Bruce", "Bryan", "Calvin", "Carl", "Charles", "Charley", "Charlie", "Chester", "Christopher", "Clarence", "Claude", "Clyde", "Conrad", "Craig", "Curtis", "Dale", "Daniel", "Danny", "Darrell", "Darren", "David", "Dean", "Dennis", "Donald", "Douglas", "Dylan", "Earl", "Edgar", "Edward", "Edwin", "Elmer", "Eric", "Ernest", "Eugene", "Floyd", "Francis", "Frank", "Frederick", "Gary", "George", "Gerald", "Glenn", "Gregory", "Guy", "Harry", "Harvey", "Henry", "Herbert", "Herman", "Homer", "Horace", "Howard", "Hugh", "Ira", "Isaac", "Jack", "Jacob", "James", "Jason", "Jay", "Jeff", "Jeffrey", "Jerry", "Jesse", "Jessie", "Jim", "Jimmy", "Joe", "Joel", "John", "Johnny", "Jonathan", "Jose", "Joseph", "Julius", "Keith", "Kelly", "Kenneth", "Kevin", "Larry", "Lawrence", "Lee", "Leo", "Leonard", "Lewis", "Louis", "Luther", "Marc", "Marion", "Mark", "Martin", "Matthew", "Michael", "Mike", "Milton", "Oliver", "Oscar", "Otto", "Patrick", "Patrick", "Paul", "Peter", "Philip", "Phillip", "Ralph", "Randall", "Randy", "Raymond", "Richard", "Ricky", "Robert", "Rodney", "Roger", "Ronald", "Roy", "Rufus", "Russell", "Samuel", "Scott", "Sean", "Shawn", "Sidney", "Stephen", "Steven", "Terry", "Theodore", "Thomas", "Timothy", "Todd", "Tom", "Tony", "Troy", "Vincent", "Walter", "Warren", "Wayne", "William", "Willie", "Willis"
	]

F_FIRST_AMERICAN = [
	"Abigail", "Agnes", "Alexa", "Alexandra", "Alexis", "Alice", "Allison", "Alma", "Alyssa", "Amelia", "Andrea", "Angelina", "Ann", "Anna", "Anne", "Annie", "Ariana", "Arianna", "Ashley", "Aubrey", "Audrey", "Autumn", "Ava", "Avery", "Bailey", "Barbara", "Beatrice", "Bernice", "Bertha", "Bessie", "Betty", "Blanche", "Brianna", "Brooke", "Brooklyn", "Caroline", "Catherine", "Charlotte", "Chloe", "Claire", "Clara", "Destiny", "Doris", "Dorothy", "Edith", "Edna", "Eleanor", "Elizabeth", "Ella", "Ellen", "Elsie", "Emily", "Emma", "Esther", "Ethel", "Eva", "Evelyn", "Faith", "Florence", "Frances", "Gabriella", "Gabrielle", "Genevieve", "Geraldine", "Gertrude", "Gianna", "Gladys", "Grace", "Gracie", "Hailey", "Haley", "Hannah", "Hazel", "Helen", "Ida", "Irene", "Isabel", "Isabella", "Isabelle", "Jada", "Jane", "Jasmine", "Jean", "Jennie", "Jennifer", "Jessica", "Jessie", "Jocelyn", "Jordan", "Josephine", "Juanita", "Julia", "June", "Kaitlyn", "Katelyn", "Katherine", "Kathleen", "Kathryn", "Kayla", "Kaylee", "Kimberly", "Kylie", "Laura", "Lauren", "Layla", "Leah", "Lena", "Leona", "Lillian", "Lillian", "Lillie", "Lily", "Lois", "Lorraine", "Louise", "Lucille", "Lucy", "Mabel", "Mackenzie", "Madeline", "Madison", "Mae", "Margaret", "Marguerite", "Maria", "Mariah", "Marian", "Marie", "Marion", "Marjorie", "Martha", "Mary", "Mary", "Mattie", "Maxine", "Maya", "Megan", "Melanie", "Mia", "Michelle", "Mildred", "Minnie", "Molly", "Morgan", "Myrtle", "Nancy", "Natalie", "Nellie", "Nicole", "Norma", "Olivia", "Opal", "Paige", "Pauline", "Pearl", "Phyllis", "Rachel", "Rita", "Rose", "Ruby", "Ruth", "Samantha", "Sara", "Sarah", "Sarah", "Savannah", "Shirley", "Sofia", "Sophia", "Sophie", "Stella", "Stephanie", "Sydney", "Sylvia", "Taylor", "Thelma", "Trinity", "Valeria", "Vanessa", "Vera", "Victoria", "Viola", "Violet", "Virginia", "Vivian", "Wilma", "Zoe"
	]

LAST_AMERICAN = [
	"Abelard","Ackley","Acton","Addison","Afton","Aida","Aidan","Ailen","Aland","Alcott","Alden","Alder","Aldercy","Aldis","Aldrich","Alfred","Allard","Alvin","Amaris","Amberjill","Amherst","Amsden","Ansley","Ashley","Atherol","Atwater","Atwood","Audrey","Avena","Averill","Ballard","Bancroft","Barclay","Barden","Barnett","Baron","Barse","Barton","Baul","Bavol","Baxter","Beacher","Beaman","Beardsley","Beccalynn","Bede","Beldon","Benson","Bentley","Benton","Bersh","Bethshaya","Beval","Beverly","Birch","Bishop","Blade","Blaine","Blake","Blossom","Blythe","Bob","Bolton","Bond","Booker","Booth","Borden","Bowman","Braden","Bradford","Bradley","Bramwell","Brandon","Bray","Brayden","Brenda","Brennan","Brent","Brett","Brewster","Brigham","Brinley","Brishen","Shea","Brock","Broderick","Bromley","Bronson","Brook","Brown","Buck","Buckley","Bud","Bunny","Burdette","Burgess","Burle","Burne","Burt","Burton","Calder","Caldwell","Calhoun","Calvert","Cam","Cameron","Carleton","Carling","Carlisle","Carlton","Carlyle","Carrington","Carter","Carver","Chad","Chal","Channing","Chapman","Charles","Chatwin","Chelsea","Chilton","Claiborne","Clark","Clayton","Clay","Cleveland","Clifford","Clinton","Clive","Clovis","Cody","Colby","Cole","Coleman","Collier","Colton","Columbia","Corin","Corliss","Coty","Courtland","Courtney","Creighton","Crosby","Culver","Currier","Cynric","Dale","Dallin","Dalton","Damon","Dane","Danior","Daralis","Darnell","Darrel","Darren","Darthmouth","Darwin","Dawn","Dayton","Demelza","Dempster","Denley","Denton","Denver","Derwin","Devon","Dickinson","Digby","Dixie","Donald","Dooriya","Dorset","Dory","Dover","Drake","Duane","Dudley","Dugan","Dunstan","Durriken","Durward","Dustin","Dwennon","Dwight","Eartha","Easter","Eaton","Ebony","Edda","Edgardo","Edison","Edlyn","Edmond","Edolie","Edsel","Edward","Edward","Eddie","Egerton","Elden","Eldon","Eldridge","Ella","Elmar","Elton","Ember","Emerson","Emmett","Ena","Erika","Erskine","Esmeralda","Esmond","Ewing","Fairfax","Falkner","Farley","Farrah","Farrah","Fara","Farrell","Fear","Fenton","Fern","Fielding","Finlay","Fleming","Fleta","Fletcher","Floyd","Forbes","Ford","Forrester","Free","Fuller","Fulton","Gage","Gail","Gaines","Garfield","Garrick","Garridan","Gary","Garyson","Geoffrey","Gleda","Goldie","Gordon","Granger","Grayson","Gresham","Grover","Gypsy","Gytha","Hadden","Hale","Hall","Halsey","Halton","Hamilton","Hanley","Harden","Harley","Harman","Harmony","Harold","Harper","Harrison","Hartley","Harva","Harvey","Hayden","Hayes","Haylee","Hazel","Heath","Heather","Hilton","Holbrook","Holly","Holt","Honey","Hope","Houston","Howard","Hugh","Hunter","Huntley","Ida","India","Ives","Jagger","Jal","James","Jimmy","Jamie","Jamison","Jarman","Jarvis","Jillian","Jocelyn","Joyce","Jonesy","Joy","Kaelyn","Keane","Keene","Kell","Kelsey","Kemp","Kenelm","Kenley","Kennard","Kenneth","Kenrich","Kent","Kenton","Ker","Keyon","Kim","Kimberley","King","Kingsley","Kinsey","Kipling","Kipp","Kirsten","Kismet","Knox","Kody","Kyla","Ladd","Lainey","Lander","Landon","Lane","Lang","Langley","Lari","Lark","Latimer","Lawson","Lee","Leigh","Leighton","Leland","Lensar","Leslie","Lew","Liberty","Lincoln","Lind","Lindsay","Linwood","Litton","Llewellyn","Locke","London","Love","Lowell","Luella","Lyman","Lyndon","Lyre","Mac","Macon","Macy","Maida","Maitane","Maitland","Makepeace","Mala","Mander","Manhattan","Manley","Manning","Marden","Marland","Marlow","Marsden","Marshal","Mather","Mavis","Maxwell","Mead","Melor","Melville","Mendel","Mercer","Mercy","Merrick","Merry","Milburn","Millard","Miller","Milton","Missy","Misty","Morley","Morven","Mull","Nara","Nash","Neda","Nelson","Nevin","Newell","Newman","Norman","North","Nyle","Oakes","Oakley","Ogden","Olin","Orman","Orson","Osbert","Osborn","Osmond","Oswald","Oswin","Oxford","Packard","Palma","Palmer","Paris","Parker","Parr","Parry","Paxton","Payton","Pearl","Pebbles","Pell","Penley","Penn","Pepper","Perri","Perry","Pierce","Pierson","Piper","Poppy","Prentice","Prescott","Preston","Putnam","Queen","Queena","Queenie","Quella","Quenna","Radcliff","Radcliffe","Radella","Radford","Rae","Raleigh","Ralph","Ramsey","Ransford","Ransley","Ransom","Raven","Ravinger","Rawlins","Rayburn","Raymond","Read","Redford","Reed","Reeve","Reeves","Reginald","Remington","Rhett","Rhodes","Richard","Richelle","Rider","Ridgley","Ridley","Rigby","Ripley","Rishley","Robert","Roberta","Rochester","Rodman","Rodney","Roldan","Rowan","Rowena","Royce","Rudd","Rudyard","Ruford","Rumer","Russel","Rutherford","Ryesen","Rylan","Sabrina","Brina","Salal","Sanborn","Sanders","Sandon","Sanford","Sawyer","Scarlet","Scarlett","Scott","Seabert","Seaton","Selby","Severin","Seward","Seymour","Shandy","Sharman","Shaw","Shelby","Sheldon","Shelley","Shepherd","Sherlock","Sherman","Sherwood","Shipley","Shirley","Siddel","Simmon","Skeet","Skye","Skyla","Skylar","Slade","Smith","Snowden","Spalding","Sparrow","Spencer","Spike","Spring","Standish","Stanford","Stanislaw","Stanley","Stanley","Stan","Stanway","Sterling","Sterne","Stockard","Stoke","Stokley","Storm","Stroud","Studs","Summer","Sunny","Sutton","Swain","Tab","Tanner","Tate","Tatum","Tawnie","Taylor","Telford","Tem","Tennyson","Terrel","Thane","Thatcher","Thistle","Thorne","Thorpe","Thurlow","Tilden","Tina","Todd","Tomkin","Townsend","Tranter","Tremayne","Trey","Tripp","Trudy","Truman","Tucker","Tuesday","Turner","Twain","Tye","Tyler","Tyne","Udolf","Ulla","Ulrich","Ulrika","Unity","Unwin","Upshaw","Upton","Vala","Vance","Velvet","Verity","Vian","Wade","Wakefield","Walker","Wallace","Walton","Ward","Warren","Washington","Watson","Waverly","Wayland","Waylen","Wayland","Wayne","Webster","Welcome","Wells","Wendy","Wesley","West","Weston","Wetherby","Wheaton","Wheeler","Whit","Whitfield","Whitlaw","Whitney","Wilfred","Willow","Wilmer","Wilona","Winifred","Winslow","Winston","Winter","Winthrop","Wolf","Woodley","Woodrow","Woodward","Wright","Wyatt","Wylie","Wyndam","Wyndham","Yardley","Yates","Yedda","Yeoman","York","Yule","Zane","Zelene","Zinnia","Allen","Austin","Avery","Bryant","Elmer","Emmett","Everett","Garrett","Gary","Jackson","Larkin","Lark","Lamont","Lawrence","Madison","Merle","Merrill","Mitchell","Morris","Nelson","Otis","Pierce","Stacy","Stacey","Willard","Willis","Wilson","Wyatt","Ainsley","Alton","Ashley","Bailey","Barrington","Bentley","Beverly","Bradford","Bradley","Brady","Brent","Brock","Brooke","Byron","Camden","Carlton","Chester","Clay","Clayton","Clifford","Clifton","Clinton","Clive","Colton","Dale","Dalton","Dana","Darby","Denzil","Digby","Drake","Dudley","Easton","Forrest","Glanville","Grover","Hailey","Haley","Hartley","Heath","Holden","Kelsey","Kendall","Kent","Kenton","Kimberly","Landon","Lee","Lester","Milton","Nash","Norris","Odell","Perry","Peyton","Preston","Rodney","Royston","Shelby","Sheldon","Shirley","Stanley","Stanton","Vance","Van","Wade","Wesley","Whitney","Winston","Woodrow","Roscoe","Barrie","Barry","Colby","Courtney","Courtenay","Darcy","Darrell","Darryl","Lacey","Lance","Lane","Leland","Montague","Mortimer","Morton","Neville","Percy","Sacheverell","Troy","Vernon","Warren","Blake","Brady","Brett","Cade","Chance","Cole","Curtis","Dana","Drew","Franklin","Scott","Tate","Todd","Truman","Wendell","Wynne","Bailey","Baron","Booker","Brewster","Carter","Chandler","Chauncey","Chase","Clark","Cooper","Cody","Cordell","Dexter","Earl","Garnet","Hunter","Jagger","Marshall","Mason","Millard","Page","Paige","Parker","Sherman","Tanner","Taylor","Tucker","Tyler","Travis","Spencer","Walker","Wayne","Bruce","Graham","Lyle","Grant","Ross","Wallace","Stuart","Dallas","Gordon","Kirk","Lindsay","Lindsey","Maxwell","Ramsay","Rutherford","Blair","Douglas","Keith","Kyle","Ross","Sterling","Boyd","Cameron","Cambell","Doyle","MacKenzie","McKinley","Irving","Logan","Barry","Cody","Darcy","Desmond","Grady","Kelley","Kelly","Kennedy","Sullivan","Barrington","Barry","Brady","Carroll","Casey","Cassidy","Cody","Donovan","Fallon","Hogan","Keegan","Quinn","Quillian","Sheridan","Corey","Cory","Delaney","Perry","Craig","Kendall","Trevor","Meredith","Vaughan","Wynne"
	]

GENERATOR_AMERICAN = Generator(
	M_FIRST_AMERICAN,
	F_FIRST_AMERICAN,
	M_FIRST_AMERICAN + LAST_AMERICAN,
	F_FIRST_AMERICAN + LAST_AMERICAN,
	LAST_AMERICAN
	)

M_FIRST_ARABIAN = [
	"Abdul Aliyy", "Abdul Aziz", "Abdul Fattah", "Abdul Halim", "Abdul Khabir", "Abdul Muhaimin", "Abdul Muqaddim", "Abdul Qadir", "Abdul Rahman", "Abdul Sattar", "Abdul Wakil", "Abdullah", "Abu Bakr", "Adib", "Ahmed", "Al 'Abbas", "Alhasan", "Alhusain", "Ali", "Alim", "Amid", "Anas", "Asad", "Ata' Allah", "Awwab", "Azim", "Badi", "Bahir", "Bashshar", "Burhan", "Dani", "Diya", "Fadil", "Fakhr al Din", "Fariq", "Fawzan", "Fu'ad", "Ghaith", "Ghiyath", "Hadad", "Hamdan", "Hani", "Hatim", "Houd", "'Id", "Imam", "Ishaq", "Jabbar", "Jamal", "Jawdah", "Junaid", "Kadin", "Karif", "Khalid", "Khoury", "Lablab", "Ma'd", "Mahrus", "Majid", "Marghub", "Nabih", "Na'im", "Nash'ah", "Nasri", "Nawaf", "Nijad", "Nur al Din", "Qais", "Rabah", "Rahman", "Rakin", "Rashid", "Rayyan", "Rushd", "Saad", "Sadad", "Safuh", "Saif al Din", "Saleh", "Salman", "Saud", "Shahin", "Sharaf", "Shumayl", "Suhaib", "Sultan", "Tahir", "Tamir", "Tawhid", "Thamer", "'Ubaidah", "Umayyah", "Waddah", "Wajdi", "Waqar", "Yahya", "Yazid", "Zafar", "Zakariyya", "Ziad"
	]

F_FIRST_ARABIAN = [
	"'Abal", "Aadab", "'Afifah", "Aida", "Alima", "Al Zahra",
	"Ameena", "Aneesa", "Areebah", "Asima", "Atifa", "Azhaar",
	"Baheera", "Baraka", "Baseema", "Bisar", "Buthayna",
	"Daniyah", "Dunya", "Fadwa", "Falak", "Farizah", "Fayha'",
	"Firyal", "Gharam", "Gharam", "Habeeba", "Hafthah",
	"Hameeda", "Hasibah", "Hayaam", "Hidayah", "Hidayah",
	"Hudun", "Husn", "Ibtihaaj", "I'jaz", "Imtithal", "Is'ad",
	"Istilah", "'Izzah", "Jana", "Jawna'", "Juhanah", "Juwan",
	"Kawakib", "Khairiya", "Labibah", "Lateefa", "Lubaaba",
	"Lu'lu'", "Madeeha", "Maymunah", "Malak", "Maraam",
	"Mawaddah", "Maysam", "Mina", "Mufeeda", "Mu'minah",
	"Murshidah", "Nabeeha", "Nadwa", "Na'ima", "Najwa", "Nasiha",
	"Nawar", "Nibras", "Niyaf", "Nunah", "Nuwwarrah", "Qudsiyah",
	"Rafah", "Raghidah", "Ra'ifah", "Raneem", "Rawdha", "Rida",
	"Rubaa", "Ruqayya", "Sabihah", "Safa'", "Sa'idah", "Salma",
	"Sameh", "Saniyah", "Shadhaa", "Shahlah", "Shaymaa",
	"Shukriyah", "Sireen", "Suhaymah", "Sunbu", "Tahiyah",
	"Taqiyah", "Tharwah", "'Ubaab", "Umniyah", "Wafeeqa",
	"Walaa'", "Wi'am", "Wurud", "Yasirah", "Zahirah", "Zanubiya",
	"Zumurrud"
	]

LAST_ARABIAN = [
	"Ali", "Ahmed", "Ahmad", "Haddad", "Mahmood", "Mansoor", "Rahman", "Abdel", "Naser", "Hanna", "Hana", "Qasim", "Sam", "Mansour", "Hadad", "Musa", "Mahmoud", "Nasser", "Hasan", "Malik", "Awad", "Hassan", "Hasan", "Essa", "Turk", "Mousa", "Mazin", "Qasem", "Qasim", "Khaleel", "Khalil", "Khaleel", "Khalil", "Kalil", "Kaleel", "Isa", "Nasser", "Yousif", "Yousef", "Jaber", "Jabir", "Shaheen", "Abba", "Najjar", "Alam", "Salah", "Abdullah", "Abdul", "Abdulah", "Abdellah", "Saleh", "Salih", "Issa", "Aziz", "Bari", "Ababneh", "Hussain", "Hossein", "Khatib", "Mustafa", "Khoury", "Sleiman", "Sulaiman", "Sulayman", "Yaseen", "Ibrahim", "Ibraheem", "Ibrahim", "Qassem", "Abbas", "Abbas", "Hamdan", "Abolhassan", "Amin", "Ameen", "Ismail", "Salman", "Rashid", "Karim", "Saad", "Sad", "Temiz", "Hamid", "Ayasha", "Saleem", "Salim", "Shadi", "Omar", "Omer", "Ommar", "Murat", "Habib", "Shareef", "Sharif", "Mahmad", "Najeeb", "Armanjani", "Shahriar", "Rasheed", "Mohammad"
	]

GENERATOR_ARABIAN = ArabianGenerator(
	M_FIRST_ARABIAN,
	F_FIRST_ARABIAN,
	M_FIRST_ARABIAN,
	M_FIRST_ARABIAN + F_FIRST_ARABIAN,
	LAST_ARABIAN
	)

M_AZTEC = [
	"Yaotl", "Matlalihuitl", "Nochehuatl", "Coatl", "Tototl", "Cuauhtl",
	"Tochtli", "Zolin", "Matlal", "Xochitl", "Mazatl", "Cuetzpalli",
	"Olli", "Itzcuintli", "Tlalli", "Huitzitl", "Ocelotl", "Ozomatli",
	"Cuetlachtli", "Tecolotl", "Miztli", "Cipac", "Ocuil", "Cuixtli",
	"Tapayaxi", "Cozahtli", "Necuametl", "Huitztecol", "Eloxochitl",
	"Xochipepe", "Achcauhtli", "Acolmixtli", "Ahuiliztli", "Amoxtli", "Atl",
	"Camaxtli", "Chicahua", "Chimalli", "Chipahua", "Citlalli", "Coyotl",
	"Cualli", "Cuauhtemoc", "Cuetlachtli", "Etalpalli", "Eztli", "Huemac",
	"Huitzilihuitl", "Huitzilin", "Ichtaca", "Icnoyotl", "Ilhicamina",
	"Ilhuitl", "Ihuicatl", "Itotia", "Itztli", "Ixtli", "Malinalxochitl",
	"Milintica", "Mecatl", "Meztli", "Nahuatl", "Necalli", "Nezahualcoyotl",
	"Nezahualpilli", "Nochtli", "Nopaltzin", "Ohtli", "Patli", "Tenoch",
	"Tezcacoatl", "Tlacaelel", "Tlachinolli", "Tlazopilli", "Toltecatl",
	"Xipil", "Xipilli", "Xiuhcoatl", "Xihuitl", "Yolotli", "Yaotl",
	"Yayauhqui", "_N_ Cipactli", "_N_ Ozomahtli", "_N_ Ocelotl",
	"_N_ Cuetzpalin", "_N_ Mazatl", "_N_ Ollin", "_N_ Xochitl",
	"_N_ Itzcuintli", "_N_ Acatl", "_N_ Calli", "_N_ Miquiztli",
	"_N_ Cozcacuauhtli", "_N_ Quiahuitl", "_N_ Atl", "_N_ Malinalli",
	"_N_ Ehecatl", "_N_ Coatl", "_N_ Cuauhtli"
	]

AZTEC_NUMERALS = [
	"Ce", "Ome", "Yei", "Nahui", "Mahchuilli", "Chicuacen", "Chicome",
	"Chicuei", "Chicunahui", "Mahtlactli"
	]

F_AZTEC = [
	 "Acaxochitl", "Achcauhtli", "Ahuiliztli", "Amoxtli", "Anacaona",
 "Atl", "Atototl", "Atzi",
 "Centehua",  "Chalchiuhticue",
 "Chalchiuitl",  "Chicahua", "Chicomecoatl", "Chimalma", "Chipahua",
 "Cihuaton",  "Citlali",  "Citlalmina",
 "Coaxoch",  "Coszcatl",  "Cozamalotl", "Cualli",
   "Cuicatl",  "Eleuia",
 "Eloxochitl",  "Etalpalli",  "Eztli",
 "Ichtaca",  "Icnoyotl",  "Ihuicatl",
 "Ilhuitl",  "Itotia",  "Itzel", "Iuitl",
 "Ixcatzin",  "Ixchel",  "Ixtli",  "Izel",
 "Mahuizoh",  "Malinalxochitl",
 "Manauia",  "Mazatl", "Mecatl", "Meztli",
 "Miyaoaxochitl",   "Mizquixaual",
 "Momoztli",    "Moyolehuani",
 "Nahuatl",    "Necahual", "Nelli",
 "Nenetl",    "Nochtli",
 "Noxochicoztli",   "Ohtli", "Papan",
 "Patli", "Quetzal",   "Quetzalxochitl",
 "Sacnite",    "Teicuih", "Tenoch",
 "Teoxihuitl",    "Tepin",
 "Teuicui",    "Teyacapan",
 "Tlachinolli",    "Tlaco",
 "Tlacoehua",    "Tlacotl", "Tlalli",
	 "Tlanextli",
 "Tlazohtzin",    "Tlexictli",
 "Tochtli", "Toltecatl",    "Tonalnan",
 "Xihuitl",    "Xiloxoch", "Xipil",
 "Xiuhcoatl",    "Xiuhtonal",
 "Xochicotzin",    "Xochiquetzal",
 "Xochitl",    "Xochiyotl", "Xoco",
 "Xocoyotl",    "Yaotl", "Yaretzi", 
 "Yayauhqui",    "Yolihuani",
 "Yolotli",    "Yoloxochitl",
 "Yoltzin",    "Yolyamanitzin",
 "Zaniyah", "Zeltzin", "Zuma",   "Zyanya"
]

GENERATOR_AZTEC = AztecGenerator(
	M_AZTEC,
	F_AZTEC,
	AZTEC_NUMERALS
	)

M_BABYLONIAN = [
	"Amarsin",
"Appan-Il",
"Apuulluunideeszu",
"Ariistuun",
"Arishaka",
"Ataneedusu",
"Anti'iikusu",
"Aplaa",
"Ar'siuqqa",
"Arshaka",
"Attii'kusu",
"Avil Kush",
"Baassiia",
"Balashi",
"Balathu",
"Bashaa",
"Burnaburiash",
"Dadanum",
"Dakhe",
"Dee'qiteesu",
"Deemeethresu",
"Deemethresi",
"Deemuukratee",
"Demetheriia",
"Dii'duuresu",
"Diimeritia",
"Diipaa'ni",
"Diipatusu",
"Dudu",
"Ea-nasir",
"Ekurzakir",
"Enshunu",
"Enusat",
"Gina",
"Hassimir",
"Hillalum",
"Hunzuu",
"Iaazipaa",
"Ibbi-Adad",
"Ikuppi-Adad",
"Ipqu-Annunitum",
"Ipqu-Aya",
"Ishme-Ea",
"Isiratuu",
"Issaruutunu",
"Kadashman-Enlil",
"Kandalanu",
"Kiipluu'",
"Kinaa",
"Kuri",
"Kurigalzu",
"Labashi",
"Laliya",
"Laqip",
"Ligish",
"Libluth",
"Manishtusu",
"Manuiqapu",
"Mannuiqapi",
"Milik-Harbat",
"Nabuzikiriskun",
"Naram-Sin",
"Nidintu-Bel",
"Nidintulugal",
"Niiqiarqusu",
"Niiqquulamuusu",
"Nikanuur",
"Nikiiarqusu",
"Nigsummu",
"Nigsummulugal",
"Nigsummunu",
"Nutesh",
"Numunia",
"Nur-Ayya",
"Puzur-Ishtar",
"Rabi-Sillashu",
"Rihat",
"Riisvul",
"Rimush",
"Ripaa",
"Samsuiluna",
"Sargon",
"Seluku",
"Shamash-Andulli",
"Shamash-Nasir",
"Sharkalisharri",
"Shu-Turul",
"Sin-Baladan",
"Sin-Nasir",
"Suusaandar",
"Tattannu",
"Timgiratee",
"Ubar",
"Ugurnaszir",
"Uktannu",
"Uppulu",
"Utuaa",
"Yahatti-Il",
"Zamana",
"Zuuthusu"
]

F_BABYLONIAN = [
	"Adeeshuduggaat",
"Ahassunu",
"Ahati-waqrat",
"Ahatsunu",
"Alittum",
"Allatu",
"Amata",
"Anagalmeshshu",
"Anagalshu",
"Anatu",
"Anunit",
"Arahunaa",
"Aralu",
"Aruru",
"Arwia",
"Ashlultum",
"Atanah-Ili",
"Banunu",
"Bau",
"Belatsunat",
"Belessunu",
"Beletsunu",
"Belili",
"Belit",
"Beltis",
"Bilit Taauth",
"Damkina",
"Davcina",
"Davke",
"Ellat-Gula",
"Enheduana",
"Erishti",
"Ettu",
"Gashansunu",
"Gemegishkirihallat",
"Gemekaa",
"Gemeti",
"Gula",
"Humusi",
"Ia",
"Iltani",
"Ishtar",
"Ishtar-gamelat",
"Istar",
"Kalumtum",
"Kishar",
"Kissare",
"Ku-Aya",
"Ku-Baba",
"Kullaa",
"Mot",
"Mummu",
"Munawwirtum",
"Mupallidat-Serua",
"Mushezibitu",
"Mushezibti",
"Mylitta",
"Nana",
"Ni",
"Nidintu",
"Nin-Marki",
"Ninsunu",
"Omarosa",
"Ri",
"Rubati",
"Sabitum",
"Sarpanitum",
"Shala",
"Tabni-Ishtar",
"Tashmitum",
"Tauthe",
"Tiamat",
"Ubalnu",
"Yadidatum",
"Zakiti",
"Zirratbanit",
u"Ǎ"
]

GENERATOR_BABYLONIAN = SimplifiedGenerator(
	M_BABYLONIAN,
	F_BABYLONIAN
	)

M_FIRST_BYZANTINE = [
	"Ionnes", "Theodorus", "Stephanus", "Stephanus", "Georgius",
	"Petrus", "Paulus", "Sergius", "Menas", "Constantinus",
	"Constantinus", "Theodosius", "Iulianus", "Leontius",
	"Anastasius", "Thomas", "Andreas", "Cosmas", "Gregorius", "Leo",
	"Alexander", "Phoebammon", "Dorotheus", "Dorotheus", "Elias",
	"Marinus", "Narses", "Victor", "Callinicus", "Cyrus", "Germanus",
	"Eustathius", "Michael", "Zacharias", "Iustinus", "Nicetas",
	"Theophylactus", "Athanasius", "Basilius", "Comitas", "Romanus",
	"Theodotus", "Anatolius", "Eusebius", "Felix", "Isidorus",
	"Marcellus", "Marianus", "Marcianus", "Patricius", "Strategius",
	"Bonus", "Damianus", "Demetrius", "Isaac", "Rufinus",
	"Theopemptus", "Dioscorus", "Gabriel", "Iustus", "Marcus",
	"Mauricius", "Procopius", "Abramius", "Ammonianus", "Laurentius",
	"Maximus", "Phillippus", "Philoxenus", "Phocas", "Asterius",
	"David", "Diogenes", "Gennadius", "Heraclius", "Honorius",
	"Iacobus", "Iustinianus", "Olympius", "Palladius", "Probus",
	"Albinus", "Antiochus", "Faustus", "Florentius", "Ioseph",
	"Marcellinus", "Martinus", "Nicolaus", "Nonnus", "Photius",
	"Plato", "Ptolemaeus", "Rusticus", "Timotheus", "Valentinus",
	"Acacius", "Aemilianus", "Andronicus", "Areobindus", "Colluthus",
	"Cyrillus", "Dionysius"
	]

M_FAMILY_BYZANTINE = [
	"Aboures", "Adrianos", "Agallon", "Akropolites", "Alyates",
	"Anemas", "Angelus", "Anicius", "Attaleiates", "Balsamon",
	"Batatzes", "Beccos", "Botaneiates", "Boumbalis", "Bourtzes",
	"Caloethus", "Canabus", "Cantacuzenus", "Chandrenos", "Choniates",
	"Choumnos", "Comnenus", "Contostephanus", "Critopoulo",
	"Dabatenus", "Dalassenos", "Dandalo", "Dermokaites", "Diasorenos",
	"Diogenes", "Doukas", "Ducas", "Eirenikos", "Eudocius",
	"Exazenus", "Ferro", "Flaccillus", "Gabras", "Glabas", "Genesius",
	"Harmenopoulos", "Herakleios", "Iagaris", "Ingerinus", "Justin",
	"Kabakes", "Kabasilas", "Kabasilis", "Kalamanos", "Kaloethes",
	"Lascaris", "Limenius", "Limpidares", "Longibardus", "Machoneos",
	"Makrembolites", "Malakes", "Marcian", "Maurocatacalon",
	"Mauropous", "Mavrozomes", "Mesopotamites", "Monachus",
	"Monomachus", "Murtzuphlas", "Nazianzen", "Neokaisareites",
	"Nestongos", "Nikephoros", "Palaeologus", "Pantechnes",
	"Paraspondylos", "Pegonites", "Pepagomenos", "Petraliphas",
	"Petzeas", "Photias", "Porphyrogenitus", "Radenos", "Rangabe",
	"Raoul", "Rizocopus", "Rossatas", "Sarantenos", "Sebastopoulos",
	"Sgouropoulos", "Skleras", "Stethatus", "Strategopoulos",
	"Tagaris",  "Tarchaneiotes",  "Tornikes",  "Trichas",
	"Trytherus",  "Tzamblakon",  "Tzetes",  "Vatatzes",  "Vlastos",
	"Zarides",  "Zautzes"
	]

F_FIRST_BYZANTINE = [
	"Maria", "Maria", "Agnes", "Ianuaria", "Anastasia", "Anthusa",
	"Ionna", "Patricia", "Antipatra", "Ionnia", "Constantina",
	"Anzoy", "Ionnina", "Euphemia", "Appa", "Iuliana", "Arabia",
	"Rusticana", "Arethusa", "Theodora", "Argentea", "Alexandria",
	"Armentaria", "Antonina", "Augustina", "Athanasia", "Aurelia",
	"Cesarea", "Basilia", "Dominica", "Basina", "Eugenia",
	"Baudegundis", "Gregoria", "Bobila", "Helena", "Bore",
	"Praeiecta", "Campana", "Sophia", "Catella", "Theocharista",
	"Cervella", "Aelia", "Charito", "Anna", "Clementina", "Aureliana",
	"Cleopatra", "Candida", "Columba", "Domentzia", "Comito",
	"Domnica", "Consolantia", "Epiphania", "Cyra", "Eusebia",
	"Damiane", "Georgia", "Destasia", "Gordia", "Didyma", "Iustina",
	"Domnola", "Leontia", "Epiphania", "Marcia", "Erchantrudis",
	"Martha", "Eudocia", "Martina", "Euphrasia", "Palatina",
	"Evantia", "Paulina", "Fausta", "Petronia", "Firmina", "Placidia",
	"Flavia", "Proba", "Flora", "Silvia", "Gabrielia", "Theodosia",
	"Galla", "Byzantia", "Germana", "Adeodata", "Gordiana", "Adula",
	"Gundesvinda", "Aemiliana", "Herena", "Aetheria", "Hesychia",
	"Aetia", "Honorata", "Agnella", "Honoria"
	]

F_FAMILY_BYZANTINE = [
	"Abourina", "Adrianina", "Agallonissa", "Akropolitissa",
	"Alyatissa", "Anemaina", "Angelina", "Anicia", "Attaleiatissa",
	"Balsamina", "Batatzina", "Beccina", "Botaneiate", "Boumbalina",
	"Bourtzina", "Caloethina", "Canabina", "Cantacuzene",
	"Chandrenina", "Choniatissa", "Choumnina", "Comnene",
	"Contostephane", "Critopoula", "Dabatene", "Dalassenina",
	"Dandala", "Dermokaitissa", "Diasorenina", "Diogenina",
	"Doukaina", "Ducaina", "Eirenikina", "Eudocia", "Exazene",
	"Ferra", "Flaccillina", "Gabraina", "Glabaina", "Genesia",
	"Harmenopoulina", "Herakleina", "Iagarina", "Ingerine", "Justina",
	"Kabakina", "Kabasilaina", "Kabasilina", "Kalamanina",
	"Kaloethina", "Lascarina", "Limenia", "Limpidarina",
	"Longibardina", "Machoneina", "Makrembolitissa", "Malakina",
	"Marcia", "Maurocatacaloina", "Mauropoina", "Mavrozomina",
	"Mesopotamitissa", "Monacheina", "Monomacheina", "Murtzuphaina",
	"Nazianza", "Neokaisareitissa", "Nestongina", "Nikephoroina",
	"Palaeologina", "Pantechnina", "Paraspondylina", "Pegonitissa",
	"Pepagomenina", "Petraliphina", "Petzeaina", "Photiaina",
	"Porphyrogenitina", "Radenina", "Rangabe", "Raoulaina",
	"Rizocopina", "Rossataina", "Sarantenina", "Sebastopoulina",
	"Sgouropoulina", "Skleraina", "Stethatina", "Strategopouloina",
	"Tagarina", "Tarchaneiotissa", "Tornikina", "Trichaina",
	"Trytherina", "Tzamblakina", "Tzetzissa", "Vatatzissa",
	"Vlastina", "Zaridina", "Zautzina"
	]

class ByzantineGenerator(Generator):

	def __init__(self, mFirst, fFirst, mFamily, fFamily):
		super(ByzantineGenerator, self).__init__(mFirst, fFirst, mFamily, fFamily, [])
		self.masculineFamily = mFamily
		self.feminineFamily = fFamily

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			return self.generateInternal(self.masculineFirstNames, self.masculineFamily, self.masculineFamily)
		else:
			return self.generateInternal(self.feminineFirstNames, self.feminineFamily, self.feminineFamily)

	def generateInternal(self, firstNames, middleNames, lastNames):
		unitName = ""

		firstName = self.choice(firstNames)
		middleName = self.choice(middleNames)
		lastName = self.choice(lastNames)

		unitName = firstName + " " + lastName

		if (len(unitName) < 17 and firstName != middleName and middleName != lastName):
			unitName = firstName + " " + middleName + " " + lastName

		return unitName

GENERATOR_BYZANTINE = ByzantineGenerator(
	M_FIRST_BYZANTINE, F_FIRST_BYZANTINE, M_FAMILY_BYZANTINE, F_FAMILY_BYZANTINE
	)

M_FIRST_CARTHAGINIAN = [
	"Abdalonymus", "Abdeshmun", "Abdhamon", "Abdmelqart", "Abdosir", "Abibaal", "Abimilki", "Abirami", "Acoholim", "Aderbaal", "Admago", "Adonibaal", "Agbal", "Ahinadab", "Ahirom", "Ahumm", "Akbar", "Anysus", "Arabo", "Asdrubal", "Ashtartyaton", "Ashtzaph", "Astegal", "Azmelqart", "Baalhaan", "Baalhanno", "Baaliahon", "Baaliaton", "Baalshillek", "Baalyaton", "Barekbaal", "Batnoam", "Bodashtart", "Bodeshmun", "Bodmelqart", "Bodtanit", "Bomilcar", "Boodes", "Bostar", "Carthalo", "Eshmounhilles", "Eshmouniaton", "Eshmunamash", "Eshmunazar", "Eshmunkhilletz", "Fierelus", "Fuabal", "Fuano", "Germelqart", "Gisgo", "Haggith", "Hamilax", "Hamilcar", "Hamiscora", "Hampsicora", "Hannibal", "Hanno", "Hannon", "Hasdrubal", "Himilco", "Hiram", "Itthobaal", "Jabnit", "Kandaulo", "Kanmi", "Khilletzbaal", "Luli", "Mago", "Maharbaal", "Maharbal", "Malchus", "Mapen", "Mathos", "Melqartpilles", "Melqart-shama'", "Merbal", "Metallo", "Milkherem", "Milkpilles", "Milkyaton", "Mintho", "Muttines", "Paltibaal", "Philosir", "Sakarbaal", "Sikarbaal", "Salicar", "Shafat", "Shipitbaal", "Sirom", "Tendao", "Tetramnestus", "Ummashtart", "Urumilki", "Yada'milk", "Yaroah", "Yehawwielon ", "Yehomilk", "Zaracas", "Zinnridi"
	]

F_FIRST_CARTHAGINIAN = [
	"Ahothmilchath", "Alissa", "Anath", "Arishat", "Asherah", "Astarte", "Athirat", "Ayzebel", "Ballat", "Batnoam", "Birich", "Dido", "Elissa", "Jezebel", "Melita", "Muttunbaal", "Nikkal", "Shapash", "Similce", "Sophoniba", "Sophonisba", "Sophonsba", "Tanis", "Tanit", "Tanith", "Thualath", "Thubab", "Thubabath", "Ummashtart", "Yzebel"
	]

LAST_CARTHAGINIAN = [
	"Barca", "Gisgon", "Rhodanus"
	]

GENERATOR_CARTHAGINIAN = MarkovGenerator(
	M_FIRST_CARTHAGINIAN,
	F_FIRST_CARTHAGINIAN,
	None, None,
	M_FIRST_CARTHAGINIAN + F_FIRST_CARTHAGINIAN + LAST_CARTHAGINIAN,
	4, 14
	)

M_FIRST_CELTIC = [
	"Anareuiseos", "Andecamulos", "Aneunos", "Arthfael",
	"Ategnatos", "Balaudos ", "Banona", "Bimmos", "Bratronos ",
	"Brice", "Britomaris", "Cabiros ", "Cadeyrn", "Caratacos",
	"Cingetorix", "Coisis", "Cunobelinus", "Cunwrig", "Cynbel",
	"Dannotalignoi ", "Diligenta ", "Doiros", "Drust",
	"Dumnorix", "Earwine", "Ector", "Elisedd", "Elowen",
	"Ferghus", "Fflam", "Fflergant", u"Frontú", "Galahad",
	"Galehodin", "Garmon", "Gwrtheyrn", "Haerviu", "Hafgan",
	"Heddwyn", "Huchon", "Iago", "Iau", "Iccauos ",
	"Indutiomarus", "Jakez", "Jones", "Judicael", "Judoc",
	"Kado", "Kai", "Kaourantin", "Kerron", "Leri", "Licnos ",
	"Lugubelenus", "Lugurix ", "Malo", "Martialis", "Missukos",
	"Morcant", "Naw", "Nedeleg", "Nele", "Nynniaw", "Odgar",
	"Olier", "Oran", "Orgetorix", "Padrig", "Parry", "Payl",
	"Per", "Reese", "Rigard", "Riok", "Ronan", "Sacer", "Samzun",
	"Sayer ", "Segomaros ", "Seisyll", "Tanet", "Tanotalos",
	"Teutorigos", "Tristan", "Uchdryd", "Uilleam", "Urmen",
	"Uther", "Vectitos", "Vercingetorix", "Viridomarus",
	"Vrittakos", "Wadu", "Wella", "Wilmot", "Yale", "Yestin",
	"Ysberin", "Zethar"
]

F_FIRST_CELTIC = [
	"Aderyn", "Aerona", "Aeronwen", "Agrona", "Alicia",
	"Andraste", "Angharat", "Aranrhod", "Beatha", "Bethan",
	"Betrys", "Blaanid", "Blodeuwedd", "Blodeuyn", "Blodwen",
	"Branwen", "Breeshey", "Cadi", "Caoilfhinn", "Caron",
	"Carys", "Catrin", "Ceinwen", "Dechtire", "Delyth", "Deryn",
	"Dilwyn", "Dilys", "Eduduwel", "Efa", "Eigyr", "Eimhir",
	"Elena", "Enith", "Epona", "Ewerich", "Fedelm", "Fenella",
	"Ffion", "Fflur", "Ffraid", "Gaenor", "Generys", "Genevra",
	"Genithles", "Genovefa", "Gladys", "Glaw", "Gwerith", "Haf",
	"Hefina", "Heledd", "Heulog", "Heulwen", "Hunith", "Idelisa",
	"Jennifer", "Keelia", "Lewke", "Lleucu", "Llewella",
	"Llinos", "Lowri", "Mabilia", "Maderun", "Margareta", "Mary",
	"Mevanou", "Milisandia", "Morud", "Morvel", "Nerys", "Nesta",
	"Nia", "Non", "Oifa", "Olwyn", "Owena", "Perweur", "Rhian",
	"Rhonwen", "Ronat", "Selma", "Seren", "Sian", "Sioned",
	"Tangwistel", "Tegan", "Tegwen", "Tesni", "Tiwlip",
	"Tudgech", "Ula", "Venetia", "Wen", "Wentlian", "Wervel",
	"Wir", "Wladus", "Wledyr"
]

LAST_CELTIC = [
	"Abgrall", "Angwin", "Bain", "Baines", "Baragwanath",
	"Beaglehole", "Beddoe", "Berthou", "Bodrugan", "Bolitho",
	"Cadogan", "Cadwaladr", "Caird", "Caradec", "Cardy", "Carew",
	"Carey", "Chenoweth", "Duncan", "Edwards", "Enys", "Erskine",
	"Evans", "Fearghas", "Floch", "Gallou", u"Goasdoué", "Goff",
	"Goldsworthy", "Gough", "Gourcuff", "Guillou", "Hammett",
	"Hamon", "Howell", "Hughes", "Isaacs", "Jago", u"Jézéquel",
	"Keller", "Kempthorne", "Kergoat", "Kewish", "Knowles",
	"Lagadec", "Lawless", "Le Bihan", "Le Bris", "Livingston",
	"Lloyd", "Llywelyn", "Lougheed", "MacAskill", u"MacCàba",
	"Madec", "McCown", "McDonnell", "Menez", "Merrick", "Moigne",
	"Nancarrow", "Nankivell", "Neil", "Neish", "Niven",
	"Olivier", "Omnes", "Owsley", "Parry", "Pasco", "Paynter",
	"Pelan", "Peutan", "Pichon", "Pinvidic", "Quemener",
	u"Quéré", "Quiniou", "Quiviger", "Rescorla", "Riou",
	"Ropars", "Roper", "Roscoe", "Rossiter", "Selkirk", "Seznec",
	"Short", "Sinnott", "Stephan", "Tanet", "Tanguy", "Teague",
	"Teare", "Thomas", "Trebilcock", "Tredinnick", "Urquhart",
	"Vaughan", "Woon"
]

GENERATOR_CELTIC = Generator(
	M_FIRST_CELTIC,
	F_FIRST_CELTIC,
	M_FIRST_CELTIC + LAST_CELTIC,
	F_FIRST_CELTIC + LAST_CELTIC,
	LAST_CELTIC
	)

CHINESE_FAMILY = [
	"An", "Bai", "Bao", "Bei", "Bi", "Bian", "Bu", "Cao", "Cen",
	"Chang", "Chen", "Cheng", "Chu", "Dai", "Di", "Dong", "Dou",
	"Fan", "Fang", "Fei", "Feng", "Fu", "Ge", "Gu", "Han", "Hao",
	"He", "Hua", "Huang", "Ji", "Jiang", "Jin", "Kang", "Kong",
	"Lang", "Lei", "Li", "Lian", "Liu", "Lu", "Luo", u"Lü", "Ma",
	"Mao", "Meng", "Mi", "Miao", "Ming", "Mu", "Ni", "Pan",
	"Pang", "Peng", "Pi", "Ping", "Qi", "Qian", "Qin", "Qu",
	"Ren", "Shao", "Shen", "Shi", "Shu", "Shui", "Song", "Su",
	"Sun", "Tan", "Tang", "Tao", "Ten", "Wan", "Wang", "Wei",
	"Wu", "Xi", "Xiang", "Xiao", "Xie", "Xiong", "Xu", "Xue",
	"Yan", "Yang", "Yao", "Yin", "You", "Yu", "Yuan", "Yue",
	"Yun", "Zang", "Zhan", "Zhang", "Zhao", "Zheng", "Zhou",
	"Zhu", "Zou"
]

CHINESE_MALE = [
			 "Ai", "Bai", "Bing", "Bo", "Chang", "Chao", "Chen",
			 "Cheng", "Chong", "Chuan", "Da", "Dan", "De",
			 "Ding", "Dong", "Du", "En", "Fa", "Fan", "Fang",
			 "Fei", "Feng", "Fu", "Gang", "Ge", "Gen", "Guang",
			 "Gui", "Guo", "Hai", "Han", "He", "Hei", "Heng",
			 "Hong", "Hui", "Jia", "Jian", "Jiang", "Jie", "Jin",
			 "Jing", "Jun", "Kang", "Lai", "Lei", "Li", "Liang",
			 "Lin", "Lun", "Meng", "Min", "Ming", "Nian", "Niu",
			 "Pei", "Peng", "Ping", "Pu", "Qi", "Qiang", "Qiao",
			 "Qin", "Qing", "Qiu", "Ren", "Rong", "Ru", "Shan",
			 "Shao", "Shen", "Sheng", "Shu", "Si", "Tao", "Teng",
			 "Ting", "Tong", "Wei", "Wen", "Xian", "Xiang",
			 "Xiao", "Xin", "Xing", "Xiu", "Yan", "Yang", "Yao",
			 "Ye", "Yi", "Yong", "Yu", "Yuan", "Ze", "Zhao",
			 "Zhe", "Zhen", "Zhi", "Zu"
]

CHINESE_FEMALE = [
		   "Ai", "An", "Bao", "Bi", "Bo", "Chang", "Chao",
		   "Chen", "Chu", "Chun", "Cui", "Dai", "Dan",
		   "Dong", "E", "Fan", "Fang", "Fei", "Fen", "Feng",
		   "Ge", "Guan", "Guang", "Hong", "Hua", "Huan",
		   "Huang", "Hui", "Jia", "Jiao", "Jie", "Jin",
		   "Jing", "Ju", "Juan", "Jun", "Kwang", "Lan", "Li",
		   "Lian", "Lin", "Ling", "Liu", "Lu", "Mei", "Ming",
		   "Mu", "Ngo", "Ning", "Niu", "Nuo", u"Nü", "O",
		   "Pei", "Ping", "Qi", "Qian", "Qiang", "Qiao",
		   "Qin", "Qing", "Qiu", "Rong", "Ru", "Ruo", "Shan",
		   "Shi", "Shu", "Shuang", "Song", "Su", "Tai",
		   "Tan", "Tao", "Ting", "Tung", "U", "Wen", "Xi",
		   "Xia", "Xiang", "Xiao", "Xing", "Xiu", "Xue",
		   "Ya", "Yan", "Yi", "Yin", "Ying", "Yu", "Yuan",
		   "Yue", "Yun", "Zhai", "Zhao", "Zhen", "Zhi",
		   "Zhu", "Zong"
]

class ChineseGenerator(Generator):

	def __init__(self, family, mPersonal, fPersonal):
		super(ChineseGenerator, self).__init__(mPersonal, fPersonal, [], [], family)

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			return self.generateInternal(self.masculineFirstNames, [], self.surnames)
		else:
			return self.generateInternal(self.feminineFirstNames, [], self.surnames)

	def generateInternal(self, personal, ignore, family):
		unitName = ""

		firstName = self.choice(family)
		lastName = self.choice(personal)
		personal2 = self.choice(personal)
		if (lastName != personal2):
			lastName = lastName + string.lower(personal2)

		unitName = firstName + " " + lastName

		return unitName

GENERATOR_CHINESE = ChineseGenerator(CHINESE_FAMILY, CHINESE_MALE, CHINESE_FEMALE)

M_FIRST_EGYPTIAN = [
	"Ahmose", "Amenemhab", "Amenemhet", "Amenhirkhepshef",
	"Amenhotep", "Amenken", "Amenmose", "Amunemhat",
	"Baufre'", "Bay", "Bebi", "Bek", "Dedi", "Dedu", "Djar",
	"Djau", "Djedefhor", "Djedptahaufankh", "Djehontyhetep",
	"Djehutihotep", "Ebana", "Hapu", "Hapuneseb", "Hardedef",
	"Haremhab", "Harkhaf", "Hekaib", "Hemiunu", "Henenu",
	"Ibebi", "Ibi", "Idu", "Ikernofret", "Ikudidy",
	"Imhotep", "Ineni", "Intef", "Kagemni", "Kawab",
	"Kenamon", "Kewab", "Kha", "Khaemweset", "Khamet",
	"Maherpa", "Mahu", "Mai", "Ma'nakhtuf", "Masaharta",
	"May", "Maya", "Nakht", "Nanefer-ka-ptah", "Nebamun",
	"Nebemakhet", "Nebenteru", "Nebetka", "Nebmakhet",
	"Padiaset", "Pamiu", "Panehsi", "Panhesy", "Parennefer",
	"Paser", "Pen-Nekhebet", "Rahotep", "Raia", "Ramose",
	"Ranofer", "Rawer", "Re'emkuy", "Re'hotep", "Sabaf",
	"Sabni", "Sabu", "Sarenpet", "Sebek-khu", "Sipair",
	"Sitayet", "Tchanun", "Tchay", "Teni-menu", "Thaneni",
	"Theshen", "Thethi", "Thuity", "Urhiya", "Userhat",
	"Wahneferhotep", "Wajmose", "Wenamon", "Weni",
	"Wenisankh", "Weshptah", "Yey", "Yuf", "Yuia", "Yuny",
	"Yuya", "Zezemonekh"
	]

F_FIRST_EGYPTIAN = [
		"A'at", "Ahhotep", "Ahmose", "Ahset", "Amtes", "Amunet",
	"Ana", "Aneksi", "Ankhesenamon", "Ankhesenpaaten",
	"Baketamon", "Bakt", "Baktwerel", "Beketaten", "Berenib",
	"Betresh", "Bint-Anath", "Bunefer", "Dedyet",
	"Fent-Ankhet", "Hapynma'at", "Hedjhekenu", "Henhenet",
	"Henite", "Hentaneb", "Hentempet", "Hentmereb",
	"Hent-Tenemu", "Henuttimeho", "Hornefrure'", "Imi",
	"Inhapi", "Intakaes", "Iput", "Ipwet", "Ipy",
	"Isetnofret", "Isis", "Istnofret", "Kasmut", "Kawit",
	"Kemanub", "Kemanut", "Kemsit", "Kentetenka", "Khama'at",
	"Khameretnebty", "Khemut", "Ma'at", "Maatkare", "Maia",
	"Maketaten", "Menhet", "Menwi", "Mereneith", "Mereryet",
	"Meryetamun", "Nebet", "Nebettawy", "Nebt", "Neferhent",
	"Neferhetep", "Neferhetepes", "Neferneferure",
	"Nefertary", "Nefertiti", "Rai", "Raia", "Redji",
	"Reputneb", "Sadeh", "Sebek-shedty-Neferu", "Senebsen",
	"Senisonbe", "Sennuwy", "Seshseshet", "Sitamun",
	"Sit-Hathor-Yunet", "Sitkamose", "Ta-Opet", "Tadukhipa",
	"Takhaet", "Tarset", "Taweret", "Tem", "Tener", "Teo",
	"Tumerisy", "Weret-Imtes"
	]

GENERATOR_EGYPTIAN = MarkovGenerator(
	M_FIRST_EGYPTIAN,
	F_FIRST_EGYPTIAN,
	M_FIRST_EGYPTIAN,
	F_FIRST_EGYPTIAN,
	M_FIRST_EGYPTIAN+F_FIRST_EGYPTIAN,
	3, 20
	)

M_FIRST_ENGLISH = [
	"Alfred", "Allen", "Alton", "Alvin", "Barry", "Bob",
	"Bradley", "Brent", "Brett", "Brigham", "Bruce", "Bud",
	"Burgess", "Burt", "Cade", "Cam", "Cameron", "Chad",
	"Charles", "Clifford", "Clive", "Clovis", "Cody",
	"Corey", "Corin", "Cory", "Craig", "Damon", "Dane",
	"Danior", "Darrel", "Darrell", "Darren", "Darryl",
	"Denzil", "Donald", "Douglas", "Drew", "Duane", "Dustin",
	"Dwight", "Earl", "Eddie", "Edgardo", "Edsel", "Edward",
	"Elmar", "Elmer", "Floyd", "Gary", "Geoffrey", "Gordon",
	"Harold", "Harvey", "Howard", "Hugh", "Irving", "James",
	"Jimmy", "Keith", "Kenneth", "Kyle", "Lance", "Lawrence",
	"Lee", "Lew", "Lowell", "Lyle", "Lyman", "Mac",
	"Maxwell", "Melor", "Merle", "Mitchell", "Morris",
	"Mortimer", "Morton", "Nelson", "Neville", "Norman",
	"Norris", "Nyle", "Orson", "Oswald", "Otis", "Percy",
	"Perry", "Ralph", "Raymond", "Reginald", "Rhett",
	"Richard", "Robert", "Rodney", "Roscoe", "Royce",
	"Rudyard", "Russel", "Scott", "Seymour", "Sherlock",
	"Spencer", "Spike", "Stan", "Stanislaw", "Stanley",
	"Studs", "Tab", "Thurlow", "Todd", "Trevor", "Trey",
	"Troy", "Tye", "Udolf", "Ulrich", "Van", "Vance",
	"Wallace", "Warren", "Wayne", "Wendell", "Wesley",
	"Whit", "Wilfred", "Willard", "Willis", "Wilmer",
	"Winston", "Woodrow", "Wyatt", "Wylie", "Zane"
	]

F_FIRST_ENGLISH = [
	"Aida", "Ailen", "Amaris", "Amberjill", "Ashley",
	"Audrey", "Avena", "Beccalynn", "Bethshaya", "Beverly",
	"Blossom", "Blythe", "Brenda", "Brina", "Bunny",
	"Chelsea", "Columbia", "Courtney", "Dana", "Daralis",
	"Dawn", "Demelza", "Dixie", "Dooriya", "Dory", "Eartha",
	"Ebony", "Edda", "Edolie", "Ella", "Ember", "Ena",
	"Erika", "Esmeralda", "Fara", "Farrah", "Fern", "Fleta",
	"Free", "Gail", "Gleda", "Goldie", "Gypsy", "Gytha",
	"Haley", "Harmony", "Harva", "Haylee", "Hazel",
	"Heather", "Holly", "Honey", "Hope", "Ida", "India",
	"Jamie", "Jillian", "Jocelyn", "Jonesy", "Joy", "Joyce",
	"Kaelyn", "Kim", "Kimberley", "Kimberly", "Kirsten",
	"Kismet", "Kody", "Kyla", "Lacey", "Lainey", "Lari",
	"Leslie", "Liberty", "Lindsey", "Luella", "Lyre",
	"Maida", "Maitane", "Mala", "Manhattan", "Mavis",
	"Mercy", "Meredith", "Merry", "Missy", "Misty", "Nara",
	"Neda", "Paige", "Palma", "Paris", "Pearl", "Perri",
	"Poppy", "Queena", "Queenie", "Quella", "Quenna",
	"Radella", "Rae", "Roberta", "Rowan", "Rowena", "Rumer",
	"Rylan", "Sabrina", "Salal", "Scarlet", "Scarlett",
	"Shirley", "Skyla", "Skylar", "Stacey", "Stacy", "Sunny",
	"Tatum", "Tawnie", "Tina", "Trudy", "Tuesday", "Ulla",
	"Ulrika", "Unity", "Vala", "Velvet", "Verity", "Welcome",
	"Wendy", "Willow", "Wilona", "Winifred", "Yedda", "Yule",
	"Zelene", "Zinnia"
	]

LAST_ENGLISH = [
	"Adin", "Akroyd", "Allum", "Archer", "Ashbee",
	"Attenborough", "Aykroyd", "Baines", "Barry", "Bayer",
	"Beamont", "Bedford", "Bell", "Bethune", "Blackett",
	"Bonniwell", "Bowie", "Braithwaite", "Brewer",
	"Broomfield", "Burdon", "Bywater", "Carpender", "Cauley",
	"Chisholm", "Cliburn", "Colegrove", "Cooper", "Cotton",
	"Crowley", "Dalby", "Daw", "Dimbleby", "Dowdall", "Duke",
	"Eakin", "Eidson", "Farley", "Fitzsimons", "Frampton",
	"Geddes", "Gold", "Grainger", "Greenwood", "Hackett",
	"Hallman", "Hardwick", "Hartnell", "Hawke",
	"Haythornthwaite", "Hector", "Hetherington", "Hoffman",
	"Horner", "Hudson", "Ingram", "Johnson", "Keith", "King",
	"Kyle", "Lang", "Leavitt", "Lewis", "Lister", "Lovell",
	"MacAskill", "Mackall", "Marley", "Maxwell", "McLennan",
	"Mildred", "Morrison", "Nelson", "Nicholl", "Norrington",
	"Osman", "Pancake", "Penfold", "Pickering", "Podmore",
	"Prescott", "Quinnett", "Reckord", "Robson", "Ryan",
	"Scruton", "Shave", "Shown", "Skillings", "Sorley",
	"Stanfield", "Stephenson", "Stonehouse", "Swinburne",
	"Thirdkill", "Thruston", "Townsend", "Turnbull",
	"Updike", "Wadsworth", "Walters", "Watkinson", "Weller",
	"Whiteside", "Wilshere", "Wolfwood", "Workman", "Zeal"
	]

GENERATOR_ENGLISH = Generator(
	M_FIRST_ENGLISH,
	F_FIRST_ENGLISH,
	M_FIRST_ENGLISH + LAST_ENGLISH,
	F_FIRST_ENGLISH + LAST_ENGLISH,
	LAST_ENGLISH
	)

M_FIRST_ETHIOPIAN = [
	"Abdi", "Abel", "Abreham", "Addis", "Ahmed", "Alex",
	"Alfred", "Alif", "Amanuel", "Amha", "Andualem",
	"Ashcalew", "Ashenafi", "Atex", "Barock", "Behailu",
	"Bekalu", "Belay", "Bereket", "Bini", "Birhanu", "Biruk",
	"Channel", "Dani", "Daniel", "Dave", "Dawit", "Dogz",
	"Endale", "Endalkachew", "Endris", "Ermias", "Estifanos",
	"Eyasu", "Fegegta", "Fiseha", "Getachew", "Getnet",
	"Habesha", "Habtamu", "Habte", "Haileab", "Haileyesus",
	"Hailu", "Henok", "Jemal", "John", "Johny", "Kalid",
	"Kassahun", "Kidus", "Kirubel", "Lapiso", "Leul",
	"Mahardis", u"Manassé", "Maru", "Melak", "Mengistu",
	"Mesay", "Mikias", "Muhamed", "Mulat", "Mulatu",
	"Mulugeta", "Nahom", "Natnael", "Nugus", "Ocram",
	"Oliyad", "Sasha", "Samson", "Seid", "Shambel",
	"Shemsedien", "Sheva", "Sibhat", "Sintayehu", "Siraj",
	"Sisay", "Sole", "Solomon", "Staven", "Steven", "Stive",
	"Sultan", "Tadele", "Ted", "Tesfaye", "Thomas", "Tsegay",
	"Urgesa", "Wek", "Wondimu", "Worku", "Yared", "Yishak",
	"Yonas", "Zekariyas", "Zelalem"
	]

F_FIRST_ETHIOPIAN = [
	"Afewerk", "Alife", "Ann", "Anna", "Annan", "Anu",
	"Asres", "Ayda", "Aysha", "Bebobaby", "Bekele", "Bemnit",
	"Betelhem", "Betty", "Beza", "Celine", "Chaple",
	"Cheren", "Deborah", "Debre", "Dina", "Eden", "Eldad",
	"Emebet", "Emeliya", "Emi", "Emu", "Eyerusalem", "Fayza",
	"Fedila", "Ferhan", "Feyise", "Genat", "Genet", "Grace",
	"Halim", "Hana", "Hani", "Hannah", "Hawi", "Helina",
	"Hewan", "Hilina", "Hiwot", "Jahzara", "Jazarah",
	"Jerusalem", "Kal", "Kaldikan", "Kidist", "Kino",
	"Legese", "Leilena", "Lilie", "Loret", "Marta", "Martha",
	"Melal", "Melod", "Meron", "Meskerem", "Milka", "Mimi",
	"Negasi", "Niya", "Niyyat", "Phoebe", "Qwara", "Rediet",
	"Rita", "Saba", "Salina", "Samira", "Samrawit", "Sara",
	"Seada", "Sefanit", "Sernat", "Sherry", "Sinetibeb",
	"Sofe", "Sol", "Sosen", "Sumeya", "Sweet", "Tessy",
	"Tinebeb", "Tinesa", "Tinsae", "Tirhas", "Tsega",
	"Wagaye", "Winta", "Yannet", "Yeabsira", "Yenu",
	"Yeshambel", "Yodit", "Zala", "Zinash"
	]

GENERATOR_ETHIOPIAN = Generator(
	M_FIRST_ETHIOPIAN,
	F_FIRST_ETHIOPIAN,
	M_FIRST_ETHIOPIAN,
	M_FIRST_ETHIOPIAN,
	M_FIRST_ETHIOPIAN
	)

M_FIRST_FRENCH = [
	"Adrien", u"Aimé", "Alain", "Alexandre", "Alexis",
	"Alfred", "Alphonse", "Amaury", u"André", "Antoine",
	"Anton", "Arthur", "Auguste", "Benjamin", u"Benoît",
	"Bernard", "Bertrand", "Bruno", "Charles", "Christian",
	"Christophe", "Daniel", "David", "Denis", "Didier",
	u"Édouard", u"Émile", "Emmanuel", u"Éric", u"Étienne",
	u"Eugène", u"François", u"Frédéric", "Franck", "Gabriel",
	"Gaston", "Georges", u"Gérard", "Gilbert", "Gilles",
	u"Grégoire", "Guillaume", "Gustave", "Henri", u"Honoré",
	"Hugues", "Ignace", "Isaac", "Jacques", "Jean",
	u"Jérôme", "Joseph", "Jules", "Julien", "Kevin",
	"Killian", "Laurent", u"Léon", "Louis", "Luc", "Lucas",
	"Marc", "Marcel", "Martin", "Matthieu", "Maurice",
	"Michel", "Nicolas", u"Noël", "Olivier", "Pascal",
	"Patrick", "Paul", "Philippe", "Pierre", "Quentin",
	"Raymond", u"Rémy", u"René", "Richard", "Robert",
	"Roger", "Roland", u"Sébastien", "Serge", u"Stéphane",
	u"Théodore", u"Théophile", "Thibaut", "Thierry",
	"Thomas", u"Timothée", "Tristan", "Ulrich", "Victor",
	"Vincent", "Winoc", "Xavier", "Yves", "Zacharie"
	]

F_FIRST_FRENCH = [
		u"Adélaïde", u"Adèle", "Adrienne", "Agathe", u"Agnès",
	u"Aimée", "Alexandrie", "Alice", u"Amélie", u"Anaïs",
	u"Andrée", "Anastasie", "Anne", "Anouk", "Bernadette",
	"Brigitte", "Capucine", "Caroline", "Catherine",
	u"Cécile", u"Céline", "Chantal", "Charlotte",
	"Christelle", "Christiane", "Christine", "Claire",
	"Claudine", u"Clémence", "Colette", "Danielle", "Denise",
	"Diane", u"Dorothée", u"Édith", u"Éléonore",
	u"Élisabeth", u"Élise", u"Élodie", u"Émilie",
	"Emmanuelle", u"Françoise", u"Frédérique", "Gabrielle",
	u"Geneviève", u"Hélène", "Henriette", "Hortense",
	u"Inès", "Isabelle", "Jacqueline", "Jeanne", "Jeannine",
	u"Joséphine", "Josette", "Julie", "Juliette", "Laetitia",
	"Laure", "Laurence", "Lorraine", "Louise", "Luce",
	"Madeleine", "Manon", "Margaux", "Marcelle",
	"Marguerite", "Marianne", "Marie", "Marine", "Marthe",
	"Martine", "Maryse", "Mathilde", u"Michèle", "Nathalie",
	"Nicole", u"Noémi", u"Océane", "Odette", "Olivie",
	"Patricia", "Paulette", u"Pénélope", "Philippine",
	u"Renée", "Sabine", "Simone", "Sophie", u"Stéphanie",
	"Susanne", "Sylvie", u"Thérèse", "Valentine", u"Valérie",
	u"Véronique", "Victoire", "Virginie", u"Zoé"
	]

LAST_FRENCH = [
		u"Affré", "Allard", "Appell", "Asselin", "Auclair",
	u"Azéma", "Baillieu", "Barbet", "Barreau", "Battier",
	"Bazalgette", "Beaulieu", "Beauvau", u"Béliveau",
	"Bergier", "Besnard", "Bittencourt", "Bocuse",
	"Bonhomme", "Bouchard", "Bougie", "Bourcier", "Bousquet",
	"Brassard", "Brosseau", "Brunet", "Calvet", "Carrell",
	"Celice", "Chaney", "Charbonnier", "Chatelain",
	u"Chéreau", "Choquet", "Coderre", "Cordonnier",
	"Coulomb", "Cousteau", "Crozier", "Danzas", "De Michele",
	"Delafosse", "Deloffre", "Desmarais", "Didier", "Droz",
	"Dubuisson-Lebon", "Dufriche-Desgenettes", "Dupuis",
	"Duval", u"Féret", u"Frère", "Galopin", "Gaubert",
	"Gavreau", u"Gérald", "Gigot", "Godeau", "Gribelin",
	"Guillaume", u"Hébras", "Houde", "Jacquet", u"Jégou",
	u"Kléber", "Laframboise", "Lambert", "Laurent",
	"Le Tonnelier", "Leclair", "Leloup", "Leroux", "Loup",
	"Mace", "Mallette", "Marchant", "Maurice", "Michaux",
	"Moitessier", "Morin", "Neri", "Parmentier",
	u"Pélissier", "Perrottet", "Pierlot", "Plouffe",
	"Poulin", "Quint", "Renou", "Robail", "Rochette",
	"Roulet", "Rouzet", "Schaeffer", "Simonot", "Soboul",
	"Subercaseaux", "Thibault", "Thiers", u"Trémaux",
	"Vaillancourt", "Vasseur", "Verninac"
	]

class FrenchGenerator(Generator):

	def generateInternal(self, firstNames, middleNames, lastNames):
		unitName = ""

		firstName = self.choice(firstNames)
		middleName = self.choice(middleNames)
		lastName = self.choice(lastNames)

		unitName = firstName + " " + lastName

		if (len(unitName) < 14 and firstName != middleName and middleName != lastName):
			unitName = firstName + "-" + middleName + " " + lastName

		return unitName

GENERATOR_FRENCH = FrenchGenerator(
	M_FIRST_FRENCH,
	F_FIRST_FRENCH,
	M_FIRST_FRENCH + M_FIRST_FRENCH + F_FIRST_FRENCH,
	F_FIRST_FRENCH + F_FIRST_FRENCH + M_FIRST_FRENCH,
	LAST_FRENCH
	)

M_FIRST_DUTCH = [
		  "Aalt", "Aart", "Abraham", "Abram", "Adlar",
		  "Adriaan", "Bartel", "Bartholomeus", "Bastiaan",
		  "Boudewijn", "Bram", "Bruin", "Carolus", "Caspar",
		  "Cees", "Chariovalda", "Christiaan",
		  "Christophorus", "Daan", u"Daniël", "Dick",
		  "Diederik", "Ditmer", "Dries", "Eduart", "Erasmus",
		  "Ewoud", "Faas", "Filippus", "Floris",
		  "Franciscus", "Frans", "Frederik", "Geeraard",
		  "Geert", "Gerardus", "Gerben", "Gerlach", u"Hæge",
		  "Haghen", "Hannes", "Harald", "Harber", "Hein",
		  "Ignaas", "Imrich", "Jaap", "Jacob", "Jacobin",
		  "Jan", "Jef", "Jelle", "Karel", "Kees", "Kerneels",
		  "Klaas", "Koen", "Koert", "Lambert", "Laurens",
		  "Leonard", "Lieve", "Lodewijk", "Lowie", "Maarten",
		  "Maas", "Marijn", "Marko", "Matthijs", "Maurits",
		  "Nicolaas", "Niels", "Pauwels", "Pepijn", "Piet",
		  "Pim", "Radboud", "Reinier", "Rembrandt",
		  "Riikard", "Roel", "Roosevelt", "Schuyler",
		  "Sebastiaan", "Sem", "Siemen", "Sjaak", "Sjef",
		  "Teun", "Theodor", "Thijs", "Thomas", "Tiede",
		  "Urian", "Valentijn", "Viktor", "Wiebe", "Willem",
		  "Wolter", "Xander"
		  ]

F_FIRST_DUTCH = [
		  "Aaltje", "Abagael", "Abrahamina", "Adelheid",
		  "Aleid", "Aletta", "Alexandra", "Angelien", "Anna",
		  "Ans", "Beatrix", "Bente", "Betje", "Carolien",
		  "Catharina", "Christiane", "Coby", u"Daniëlle",
		  "Daphne", "Doortje", "Edith", "Eleonora", "Eva",
		  "Febe", "Felicia", "Femke", "Geertje",
		  "Geertruida", "Gerarda", "Gerardina", "Gerda",
		  "Greet", "Hadewych", "Heleen", "Hendrika",
		  "Hennie", "Ida", "Ilse", "Ima", "Jacoba",
		  "Janneke", "Jantina", "Johanna", "Katelijn",
		  "Katrien", "Klaartje", "Klaasje", "Klara",
		  "Klasina", "Kunigonde", "Liesbeth", "Liesje",
		  "Liselot", "Loes", "Maaike", "Maartje", "Machteld",
		  "Margriet", "Marianne", "Marieke", "Marij",
		  "Marijse", "Marjolein", "Marloes", "Margaretha",
		  "Mia", "Mieke", "Miep", "Mies", "Mirjam", "Myrthe",
		  "Nes", "Nicole", "Nicoline", "Paula", "Paulien",
		  "Petra", "Rebecca", "Renate", "Rikila", "Roos",
		  "Sanne", "Sara", "Saskia", "Sofie", "Sterre",
		  "Susanna", "Theresia", "Trees", "Trijntje",
		  "Truus", "Ursula", "Vanessa", "Veer", "Viona",
		  "Wil", "Wilhelmina", "Xandra", "Yvonne", u"Zoë"
		  ]

LAST_DUTCH = [
	   "Aafjes", "Aaij", "Aakster", "ter Avest", "Baas",
	   "Bakker", "van den Berg", "van der Berg",
	   "van der Bijl", "de Boer", "van der Boor", "Bos",
	   "Brouwer", "van Buren", "van Buskirk", "Carl",
	   "Citroen", "van Coevorden", "Cornelissen", "Dekker",
	   "van Dijk", "Dijkstra", "van Dyck", "Eerkens",
	   "Eikenboom", "Elzinga", "Erckens", "Flipse",
	   "Flipsen", "Fortuin", "Fortuyn", "Geelen", "Geelens",
	   "de Graaf", "de Groot", "de Haan", "de Haas",
	   "Hendriks", "Hoebee", "van het Hoff", "'t Hooft",
	   "de Jaager", "Jansen", "Janssen", "de Jong",
	   "van Kampen", "Kappel", "Karl", "de Koning",
	   "Langbroek", "Lauwens", "van Leeuwen",
	   "van der Linden", "Maarschalkerweerd", "van der Meer",
	   "Meijer", "Mesman", "Meulenbelt", "Meyer",
	   "van der Molen", "Muis", "Mulder", "Naaktgeboren",
	   "Nagel", "Nelissen", "Nifterick", "Offermans",
	   "Ogterop", "Oomen", "Oorschot", "Peeters", "Peters",
	   "Pietersen", "Prins", "Rademaker", "van Rijn", "Ruis",
	   "Rynsburger", "Smit", "Smits", "Spaans", "Stegenga",
	   "Teunissen", "Theunissen", "Tuinstra", "Visser",
	   "van Vliet", "Vos", "de Vries", "Vroom", "de Wees",
	   "van der Westhuizen", "van Wijk", "Willems", "de Wit",
	   "de Wolff", "Xylander", "Zaal", "Zeeger", "Zondervan"
	   ]

GENERATOR_DUTCH = Generator(
	M_FIRST_DUTCH,
	F_FIRST_DUTCH,
	M_FIRST_DUTCH,
	F_FIRST_DUTCH,
	LAST_DUTCH
	)

M_FIRST_GERMAN = [
		   "Abbo", "Achim", "Albrecht", "Alexander",
		   "Andreas", "Ben", "Bernhard", "Bernd", "Berthold",
		   "Bodo", "Carsten", "Christian", "Christof",
		   "Clemens", "Conrad", "Dagobert", "Daniel",
		   "Dennis", "Detlef", "Dieter", "Egon", "Elias",
		   "Elmar", "Emil", "Ernst", "Fabian", "Felix",
		   "Finn", "Frank", "Friedrich", "Gebhard", "Georg",
		   "Gerhard", u"Günther", "Gustav", "Hans",
		   "Heinrich", "Heinz", "Helmuth", "Hermann",
		   "Horst", "Ignatius", "Ingemar", "Jan", "Jannik",
		   "Jonas", u"Jörg", u"Jürgen", "Kai", "Karl",
		   "Karlheinz", "Klaus", "Kurt", "Lars", "Leon",
		   "Luis", "Lukas", "Manfred", "Marcel", "Markus",
		   "Martin", "Matthias", "Max", "Michael", "Niklas",
		   "Nils", "Noah", "Norbert", "Oliver", "Olof",
		   "Oskar", "Otto", "Patrick", "Paul", "Peter",
		   "Philipp", "Raimund", "Rainer", "Randolf", "Rolf",
		   "Schorsch", "Sebastian", "Sepp", "Stefan",
		   "Thomas", "Tim", "Tobias", "Torsten", "Udo",
		   "Ulf", "Ulrich", "Uwe", "Veit", "Viktor",
		   "Vinzenz", "Volkard", "Walther", "Werner",
		   "Wilhelm", "Wolfgang"
		   ]

F_FIRST_GERMAN = [
		   "Achima", "Andrea", "Angelika", "Anja", "Anna",
		   "Barbara", "Berta", "Birgit", "Brigitte",
		   u"Cäcilia", "Christa", "Christina", "Claudia",
		   "Dietricha", "Edith", "Elfriede", "Elisabeth",
		   "Elke", "Elsa", "Emilia", "Emily", "Emma",
		   "Erika", "Erna", "Felicie", "Franziska", "Frauke",
		   "Frieda", "Gabriele", "Gerda", "Gertrud",
		   "Gisela", "Hannah", "Heike", "Helga", "Hertha",
		   "Hildegard", "Ilse", "Inge", "Ingeborg", "Ingrid",
		   "Irmgard", "Jannike", "Jennifer", "Jessika",
		   "Julia", "Karin", "Katharina", u"Käthe", "Katrin",
		   "Laura", "Lea", "Lena", "Leonie", "Lieselotte",
		   "Lilli", "Lina", "Lisa", "Margarethe", "Marie",
		   "Marion", "Martha", "Martina", "Melanie", "Mia",
		   "Monika", "Nadine", "Nicole", "Oda", "Odelia",
		   "Ortrun", "Otthild", "Petra", "Porsche",
		   "Rebekka", "Reinhilde", "Renata", "Ricarda",
		   "Sabine", "Sabrina", "Sandra", "Sarah", "Sofia",
		   "Stefanie", "Susanne", "Tabea", "Tanja",
		   "Teresia", "Ursula", "Uschi", "Ute", "Valda",
		   "Verena", "Viktoria", "Walborg", "Waltraud",
		   "Wanda", "Wibeke", "Zelda", "Zenzi"
		   ]

LAST_GERMAN = [
		"Albrecht", "Arnold", "Bauer", "Baumann", "Beck",
		"Becker", "Berger", "Bergmann", "Brandt", "Braun",
		"Busch", u"Böhm", "Dietrich", "Engel", "Fischer",
		"Frank", "Franke", "Friedrich", "Fuchs", "Graf",
		u"Groß", u"Günther", "Haas", "Hahn", "Hartmann",
		"Heinrich", "Herrmann", "Hoffmann", "Hofmann",
		"Horn", "Huber", "Jung", u"Jäger", "Kaiser",
		"Keller", "Klein", "Koch", "Kraus", "Krause",
		u"Krämer", u"Krüger", "Kuhn", u"Köhler", u"König",
		u"Kühn", "Lang", "Lange", "Lehmann", "Lorenz",
		"Ludwig", "Maier", "Martin", "Mayer", "Meier",
		"Meyer", u"Möller", u"Müller", "Neumann", "Otto",
		"Peters", "Pfeiffer", "Pohl", "Richter", "Roth",
		"Sauer", "Schmid", "Schmidt", "Schmitt", "Schmitz",
		"Schneider", "Scholz", "Schreiber", u"Schröder",
		"Schubert", "Schulte", "Schulz", "Schulze",
		"Schumacher", "Schuster", "Schwarz", u"Schäfer",
		"Seidel", "Simon", "Sommer", "Stein", "Thomas",
		"Vogel", "Vogt", "Voigt", "Wagner", "Walter",
		"Weber", u"Weiß", "Werner", "Winkler", "Winter",
		"Wolf", "Wolff", "Ziegler", "Zimmermann"
		]

GENERATOR_GERMAN = Generator(
	M_FIRST_GERMAN,
	F_FIRST_GERMAN,
	M_FIRST_GERMAN,
	F_FIRST_GERMAN,
	LAST_GERMAN
	)

M_FIRST_GREEK = [
	"Agathocles", "Agenor", "Ajax", "Alcaeus", "Alcibiades",
	"Alcman", "Alexander", "Alexios", "Ananias",
	"Anastasios", "Androcles", "Andronicus", "Andronicus",
	"Angel", "Anthiomos", "Arcesilaus", "Archelaus",
	"Archelochus", "Archimedes", "Argus", "Aristides",
	"Aristippus", "Aristo", "Aristocles", "Aristophanes",
	"Aristotle", "Arion", "Athanasios", "Atreas",
	"Charalambos", "Christoforos", "Christos", "Daedalus",
	"Damianos", "Demoleon", "Demosthenes", "Dimitrios",
	"Diodorus", "Diogenes", "Diomedes", "Dionysios",
	"Dioscoros", "Elias", "Eleutherius", "Erastus",
	"Eusebius", "Evangelos", "Georgios", "Grigorios",
	"Joachim", "Jonah", "Joseph", "Konstantinos", "Kyrillos",
	"Lambros", "Matthaios", "Michael", "Moses", "Nectarius",
	"Nicodemus", "Nicolas", "Nikephoros", "Panayiotis",
	"Panteleimon", "Pheidias", "Philemon", "Philoctetes",
	"Philon", "Pindar", "Plato", "Polemon", "Polybus",
	"Polynices", "Polybios", "Priam", "Procopios",
	"Pythagoras", "Pyrrhus", "Sakellarios", "Sergios",
	"Simeon", "Solomon", "Sophocles", "Spyridon",
	"Staurakios", "Stavros", "Stylianos", "Themistocles",
	"Theodoros", "Theofilos", "Theseus", "Thestor", "Thomas",
	"Thrasybulus", "Thrasymachus", "Thucydides", "Timotheos",
	"Vassileios", "Xenophon", "Xerxes", "Zacharias"
	]

F_FIRST_GREEK = [
	"Aikaterine", "Alcycone", "Andromache", "Andromeda",
	"Anna", "Antigone", "Aphrodite", "Arete", "Ariadne",
	"Artemis", "Aspasia", "Athena", "Barbara", "Baukis",
	"Berenike", "Bernice", "Calliope", "Callirrhoe",
	"Cassandra", "Cassiopeia", "Christina", "Cleopatra",
	"Clio", "Clytaemnestra", "Crino", u"Danaë", "Daphne",
	"Demeter", "Despina", "Electra", "Eleni", "Elizabeth",
	"Eudocia", "Eudoxia", "Europa", "Eurydice", "Eva",
	"Evgenia", "Foteini", "Frona", "Gabriel", "Gaea",
	"Galene", "Glykeria", "Harmonia", "Helianthe", "Hera",
	"Hermione", "Hippolyta", "Hyacinth", "Hypatia", "Ianthe",
	"Ileana", "Ino", "Ioulia", "Iphigenia", "Irene",
	"Ismene", "Jocasta", "Kalligeneia", "Kalliste",
	"Kalypso", "Lakhesis", "Laodice", "Lydia", "Margarita",
	"Maria", "Martha", "Medea", "Melpomene", "Michaela",
	"Michelle", "Nana", "Narkissa", "Nike", "Oinone",
	"Okyrhoe", "Olimpia", "Pandora", "Penelope", "Phoebe",
	"Phyllis", "Rhaab", "Rhachel", "Rhea", "Sarah", "Scylla",
	"Selene", "Sofia", "Tethys", "Thaleia", "Thetis",
	"Urania", "Vasiliki", "Xanthe", "Xanthippe", "Xena",
	"Zena", "Zenais", "Zoe"
	]

M_LAST_GREEK = [
	"Alexiou", "Anastasopoulos", "Andreadis", "Andreou",
	"Angelopoulos", "Antoniadis", "Antoniou", "Antonopoulos",
	"Apostolou", "Bakoyannis", "Botsaris", "Calazans",
	"Carras", "Cassavetes", "Chalkias", "Christodoulopoulos",
	"Christodoulou", "Christos", "Christou", "Cora",
	"Daskalakis", "Demetriou", "Diamantopoulos", "Dimas",
	"Dimitriou", "Fotiou", "Fotopoulos", "Gavalas", "Gavras",
	"Georgiadis", "Georgiou", "Giannakopoulos",
	"Giannopoulos", "Hatzis", "Ioannidis", "Ioannou",
	"Kaklamanis", "Kalogeropoulos", "Karras", "Katrakis",
	"Kefalogianni", "Kiriakidis", "Konstantinidis",
	"Konstantinou", "Konstantopoulos", "Labropoulos",
	"Leandros", "Lekkas", "Logothetis", "Makris",
	"Margaritis", "Markopoulos", "Matraxia", "Mitropoulos",
	"Mitsotakis", "Mitzou", "Nafpliotis", "Nerantzis",
	"Nikolaidis", "Nikopoulos", "Notaras", "Oikonomopoulos",
	"Oikonomou", "Orologas", "Pallis", "Panagiotopoulos",
	"Papadakis", "Papadopoulos", "Papageorgiou",
	"Papaioannou", "Papakonstantinou", "Papanastasiou",
	"Papandreou", "Rallis", "Roussopoulos", "Sakellarios",
	"Samaras", "Savalas", "Savva", "Skarlatos", "Spheeris",
	"Spiliotopoulos", "Spyropoulos", "Tadros", "Terzis",
	"Theodorakis", "Theodoridis", "Theotokis",
	"Triantafyllou", "Tsaldaris", "Tsamis", "Valavanis",
	"Vardinogiannis", "Vasileiou", "Vasiliou",
	"Vasilopoulos", "Vassiliadis", "Vlahos", "Vougiouklakis",
	"Xenakis"
	]

F_LAST_GREEK = [
	"Alexiou", "Anastasopoulou", "Andreadi", "Andreou",
	"Angelopoulou", "Antoniadou", "Antoniou", "Antonopoulou",
	"Apostolou", "Bakoyanni", "Botsari", "Calazans", "Carra",
	"Cassavetes", "Chalkia", "Christodoulopoulou",
	"Christodoulou", "Christos", "Christou", "Cora",
	"Daskalaki", "Demetriou", "Diamantopolou", "Dimas",
	"Dimitriou", "Fotiou", "Fotopoulou", "Gavala", "Gavras",
	"Georgiadi", "Georgiou", "Giannakopoulou",
	"Giannopoulou", "Hatzi", "Ioannidou", "Ioannou",
	"Kaklamani", "Kalogeropoulou", "Karra", "Katrakis",
	"Kefalogianni", "Kiriakidi", "Konstantinidis",
	"Konstantinou", "Konstantopoulou", "Labropoulou",
	"Leandros", "Lekka", "Logotheti", "Makri", "Margariti",
	"Markopoulou", "Matraxia", "Mitropoulou", "Mitsotaki",
	"Mitzou", "Nafpliotou", "Nerantzi", "Nikolaidi",
	"Nikopoulou", "Notara", "Oikonomopoulou", "Oikonomou",
	"Orologa", "Palli", "Panagiotopoulou", "Papadaki",
	"Papadopoulou", "Papageorgiou", "Papaioannou",
	"Papakonstantinou", "Papanastasiou", "Papandreou",
	"Ralli", "Roussopoulos", "Sakellariou", "Samara",
	"Savalas", "Savva", "Skarlatos", "Spheeris",
	"Spiliotopoulou", "Spyropoulos", "Tadros", "Terzi",
	"Theodorakis", "Theodoridou", "Theotoki",
	"Triantafyllou", "Tsaldari", "Tsamis", "Valavani",
	"Vardinoyannis", "Vasileiou", "Vasiliou", "Vasilopoulou",
	"Vassiliadou", "Vlahou", "Vougiouklaki", "Xenaki"
	]

class GreekGenerator(Generator):

	def __init__(self, mFirst, fFirst, mFamily, fFamily):
		super(GreekGenerator, self).__init__(mFirst, fFirst, mFamily, fFamily, [])
		self.masculineFamily = mFamily
		self.feminineFamily = fFamily

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			return self.generateInternal(self.masculineFirstNames, self.feminineFamily, self.masculineFamily)
		else:
			return self.generateInternal(self.feminineFirstNames, self.feminineFamily, self.feminineFamily)

	def generateInternal(self, firstNames, middleNames, lastNames):
		unitName = ""

		firstName = self.choice(firstNames)
		middleName = self.choice(middleNames)
		lastName = self.choice(lastNames)

		unitName = firstName + " " + lastName

		if (len(unitName) < 17 and firstName != middleName and middleName != lastName):
			unitName = firstName + " " + middleName + "-" + lastName

		return unitName

GENERATOR_GREEK = GreekGenerator(
	M_FIRST_GREEK, F_FIRST_GREEK, M_LAST_GREEK, F_LAST_GREEK
	)

M_FIRST_HOLY_ROMAN = [
	"Abbo", "Adalbert", "Adaldag", "Adalhard", "Adelard",
	"Aega", "Baugulf", "Benild", "Berchar", "Berengar",
	"Bernard", "Berno", "Birinus", "Ceufroy", "Charibert",
	"Charles", "Cheldric", "Childebert", "Childebrand",
	"Clodomir", "Dodo", "Dreux", "Drogo", "Dudon", "Ebbo",
	"Ebroin", "Ebrulf", "Erchinoald", "Evroul", "Evroult",
	"Fardulf", "Flodoard", "Folcard", "Folmar", "Fulbert",
	"Gerbert", "Gereon", "Gerold", "Godobald", "Grifo",
	"Grimald", "Hagen", "Hildebald", "Hildebold",
	"Hildeprand", "Huebald", "Humbert", "Hunald", "Imbert",
	"Imninon", "Jocelin", "Lambert", "Lanfranc", "Laudus",
	"Lebuin", "Ledger", "Leger", "Leodegar", "Meginhard",
	"Merobaudes", u"Médard", "Nithard", "Norbert",
	"Nordbert", "Notker", "Odger", "Odo", "Odulf", "Omer",
	"Orderic", "Otker", "Ouen", "Pepin", "Philibert",
	"Piligrim", "Poppo", "Puvis", "Radigis", "Ragnfred",
	"Razo", "Reginald", "Reginar", "Remi", "Sergius",
	"Sicho", "Sigebert", "Sigibert", "Suger", "Suidbert",
	"Thankmar", "Turpin", "Vedast", "Vicelin", "Vigor",
	"Vulmar", "Waiofar", "Wala", "Wibert", "Wulfram",
	"Zwentibold"
	]

F_FIRST_HOLY_ROMAN = [
	"Adallinda", "Adaltrude", "Adelheid", "Alpaida",
	"Alpais", "Amatilda", "Ansgard", "Aregund", "Aubirge",
	"Audofleda", "Audovera", "Austerchild", "Baldechildis",
	"Basina", "Basine", "Bathild", "Begga", "Berenga",
	"Bertechildis", "Bertha", "Bertrada", "Bertrude",
	"Bilichild", "Bilichilde", "Brunhilda", "Burgundefara",
	"Chimnechild", "Chunsina", "Clothild", "Clotilda",
	"Clotilde", "Deuteria", "Eadgithu", "Emma", "Engelberga",
	"Ermenberga", "Ermengard", "Ermentrudis", "Eustere",
	"Evochildis", "Faileube", "Fara", "Fastrada", "Foy",
	"Fredegund", "Fulberte", "Galswintha", "Genofeva",
	"Gersvinda", "Gisela", "Gomentrude", "Gudula", "Gudule",
	"Gundrada", "Guntheuc", "Haldetrude", "Herleva",
	"Hildegard", "Hildegarde", "Hildegund", "Hiltrude",
	"Hodierna", "Ingeltrude", "Ingeltrudis", "Ingoberga",
	"Ingund", "Joveta", "Liobsynde", "Liutgarde",
	"Madelgarde", "Marcatrude", "Marcovefa", "Mechtild",
	"Merofleda", "Moschia", "Nantechildis", "Nanthild",
	"Oda", "Ogiva", "Plectrudis", "Radegund", "Radogund",
	"Ragintrudis", "Rosamund", "Rothaide", "Rotrude",
	"Rotrudis", "Ruothilde", "Sichilde", "Suavegotha",
	"Theodelinda", "Theoderada", u"Théoudehilde",
	"Theudechild", "Theutberga", "Ultrogotha", u"Vénérande",
	"Waldrada", "Wisigard", "Wulfefundis"
	]

LAST_HOLY_ROMAN = [
	"Agilbert", "Agobard", "Aigulf", "Alberic", "Allowin",
	"Amalricus", "Amand", "Amator", "Angegisis", "Angilbart",
	"Angilbert", "Anno", "Ansegisel", "Anskar", "Arbitio",
	"Arbogast", "Arbogastes", "Arculf", "Arnoul", "Arnulf",
	"Artaud", "Asselin", "Atacinus", "Audoen", "Audomar",
	"Audoneus", "Audramnus", "Bauto", "Bavo", "Bero",
	"Bertelis", "Berthaire", "Bertin", "Bertulf", "Besso",
	"Blutmund", "Boso", "Bovo", "Brice", "Britius",
	"Brocard", "Bruno", "Burchard", "Butilin", "Carloman",
	"Cassyon", "Childeric", "Chilperic", "Chlodmer",
	"Chlodowig", "Chlotar", "Chrodegang", "Clotaire",
	"Clothair", "Clovis", "Corbinian", "Cyr", "Cyricus",
	"Dado", "Dagobert", "Dalfin", "Einhard", "Emme",
	"Emmeran", "Engilbert", "Enurchus", "Faro", "Fredegar",
	"Fridolin", "Fridugis", "Fulk", "Fulrad", "Gifemund",
	"Giseler", "Giso", "Godun", "Goisfrid", "Goscelin",
	"Gouzlim", "Gozbert", "Gozolon", "Grimbald", "Gunthar",
	"Guntramn", "Halinard", "Hartmut", "Helinand",
	"Helisachar", "Heribert", "Hilduin", "Hincmar",
	"Hlodver", "Letard", "Leufred", "Leufroy", "Leutfrid",
	"Leuthere", "Liudhard", "Liudolf", "Lo", "Lothar", "Lul",
	"Lull", "Maiuel", "Maixent", "Majorian", "Mallobaudes",
	"Mansuetus", "Maraulf", "Marcoul", "Matfrid", "Mauger",
	"Merovech", "Ouus", "Pacatian", "Pair", "Pancras",
	"Panteleon", "Pippin", "Reolus", "Richomer",
	"Richomeres", "Riquier", "Rothad", "Samo", "Suidger",
	"Syagrius", "Tassilo", "Taurin", "Tescelin", u"Théodard",
	"Theodoric", "Theodulf", "Theodulph", "Theudebert",
	"Theuderic", "Theutgaud", "Thierry", "Thietmar",
	"Walaric", "Waldolanus", "Waltgaud", "Wandregisel",
	"Wandregisilus", "Wandrille", "Warmann", "Werinbert",
	"Wichmann", "Willehad", "Willibald", "Willibrord"
	]

GENERATOR_HOLY_ROMAN = MarkovGenerator(
	M_FIRST_HOLY_ROMAN,
	F_FIRST_HOLY_ROMAN,
	M_FIRST_HOLY_ROMAN,
	F_FIRST_HOLY_ROMAN,
	LAST_HOLY_ROMAN,
	3, 13
	)

M_INCA = [
	"Acahuana", "Amaru", "Anku", "Anquimarca", "Anta-Accla",
	"Antay", "Apaec", "Apo", "Apo-Mayta", "Apocatequil",
	"Apu", "Asto", "Atahuallpa", "Atik", "Atoc", "Atoc-Sopa",
	"Atoc-Suqui", "Auqui", "Auqui-Huaman", "Ayar",
	"Ayar-Acar", "Ayar-Cachi", "Ayar-Colo", "Ayar-Manco",
	"Canchari", "Capac", "Capac-Tupac", "Cariapata",
	"Catequil", "Cayo-Topa", "Chalcuchima", "Challco",
	"Chasca-Coyllur", "Chiaquitinta", "Con", "Coniraya",
	"Cusi", "Cuyuchi", "Ekkekko", "Epunamun", "Guachimines",
	"Guamansuri", "Hakan", "Huacac", "Huallpa",
	"Huamanpallpa", "Huanca", "Huascar", "Huiracocha",
	"Ilyapa", "Inca", "Inti", "Khuno", "Kumya", "Kunak",
	"Kuntur", "Kuzco", "Maita", "Mallku", "Manco", "Manko",
	"Maricanchi", "Ninan", "Pacari", "Pachacamac",
	"Pachacuti", "Pahuac", "Paricia", "Paullu", "Piguerao",
	"Poma", "Punchau", "Qhapaq", "Quehuar", "Raymi",
	"Rimachi", "Roca", "Ruq'a", "Samin", "Sayri", "Sinchi",
	"Sumaq", "Supay", "Thonapa", "Titu", "Tupa", "Tupac",
	"Tupaq", "Uchu", "Ullanta", "Umaq", "Urcaguary", "Urcon",
	"Urqu", "Uturunku", "Vicaquirao", "Viracocha", "Waman",
	"Yahuar", "Yupanqui"
	]

F_INCA = [
	"Achiq", "Achiyaku", "Akllasisa", "Akllasumaq",
	"Alliyma", "Amancay", "Anahuarque", "Apacheta",
	"Axomamma", "Cava", "Cavillaca", "Chasca", u"Ch'ayña",
	"Chic'ya", "Chimpu", "Cocomama", "Copacati", "Cuca",
	"Curi", "Cuxi", "Hamk'a", "Huaco", "Huamanpallpa",
	"Huch'uykilla", "Huchuysisa", "Illpay", "Imasumaq",
	"Inguill", "Inkasisa", "Izhi", "Ka-Ata-Killa",
	"Karwasisa", "Killa", "Killasisa", "Killasumaq",
	u"Kukulí", "Kusi-Quyllur", "Mama-Allpa", "Mama-Cocha",
	"Mamanea", "Mama-Oullo", "Mama-Pacha", "Mama-Quilla",
	"Mama-Runtu", "Marca-Chimbo", "Micay", "Miski",
	"Moraeka", "Nina", "Ninasisa", u"Ñust'a", "Ocllo",
	"Palla", "Pillcu", "Pilpintu", "Qhawa", "Qhispe",
	"Qhispi", "Qhora", "Qispi", "Qora", "Qori", "Q'orianka",
	"Quila", "Quinuama", "Qullqi", "Qura", "Quri",
	"Quriquyllur", "Qurit'ika", "Quya", "Quyakusi",
	"Quyllur", "Quyllurit'i", "Runtu", "Sachasisa", "Si",
	"Sisa", "Sumaq", "Sumat'ika", "Suyana", "Tamiasisa",
	"Tamya", "Tamyasisa", "Tanitani", "Taruka",
	"Taruka", "Tuta", "Uarcay", u"Umiña", "Uqllu", "Urpi",
	"Urpihua-Chac", "Urpikusi", "Waqar", "Waylla",
	"Waytamayu", "Yachay", "Yma", "Zaramamma", "Zincheata"
	]

GENERATOR_INCA = MarkovGenerator(
	M_INCA,
	F_INCA,
	M_INCA,
	F_INCA,
	M_INCA + F_INCA,
	2, 13
	)

M_FIRST_NORTH_INDIAN = [
	'Ajeet', 'Ajit', 'Aman', 'Amar', 'Amarpreet', 'Ankit',
	'Ankur', 'Ankush', 'Arjun', 'Arvin', 'Arvind', 'Ashish',
	'Ashu', 'Balbir', 'Baljinder', 'Baljit', 'Bawa', 'Bittu',
	'Charanjit', 'Daljit', 'Dhruv', 'Dinesh', 'Dishank',
	'Gabo', 'Gaurav', 'Gurinder', 'Gurmej', 'Gurpreet',
	'Gurrinder', 'Hari', 'Harjeet', 'Harjinder', 'Harjit',
	'Harman', 'Harminder', 'Harnam', 'Harshad', 'Inderbir',
	'Inderpreet', 'Iqbal', 'Jas', 'Jugesh', 'Jujhar',
	'Jupvir', 'Karan', 'Keshav', 'Kush', 'Mahabir', 'Manish',
	'Manraj', 'Mohinder', 'Nasib', 'Nav', 'Navdeesh',
	'Navjosh', 'Navraj', 'Neeraj', 'Nikesh', 'Paldeep',
	'Paras', 'Pav', 'Praveen', 'Pritpal', 'Radha', 'Raj',
	'Raman', 'Ranjit', 'Ranvik', 'Ravinder', 'Ravsagar',
	'Rohan', 'Rohit', 'Saahil', 'Sahil', 'Salihli', 'Samir',
	'Sandeep', 'Sanjeev', 'Sanjit', 'Santokh', 'Sarabjit',
	'Sarb', 'Sarbdeep', 'Sarbjit', 'Satwant', 'Shakti',
	'Shammi', 'Sharad', 'Sharat', 'Shashank', 'Siddharth',
	'Sudesh', 'Sunil', 'Surjit', 'Tarun', 'Trishneet',
	'Vardaan', 'Vijay', 'Viraj', 'Vivek'
	]

F_FIRST_NORTH_INDIAN = [
	'Aayushi', 'Aidan', 'Aishwarya', 'Ajaree', 'Akanksha',
	'Alia', 'Alisha', 'Amandeep', 'Amanjit', 'Amar',
	'Amarjit', 'Amman', 'Amrita', 'Anita', 'Anjali',
	'Anushka', 'Apoorva', 'Armaan', 'Ashwini', 'Baldip',
	'Baljit', 'Bhaavna', 'Bhumika', 'Charnita', 'Charu',
	'Deepkika', 'Deepti', 'Dilpreet', 'Dipannita', 'Divya',
	'Drashti', 'Gauri', 'Gurunam', 'Harpeet', 'Himali',
	'Inderjit', 'Jas', 'Jasmeet', 'Jasmin', 'Jaspreet',
	'Jasvir', 'Joti', 'Kabeljit', 'Kainaat', 'Kal',
	'Kamaljit', 'Kinza', 'Kirin', 'Kirneet', 'Kulwant',
	'Malaika', 'Mandeep', 'Maninderjit', 'Manreet', 'Meenu',
	'Mehar', 'Mehma', 'Mirza', 'Navkirat', 'Navrita',
	'Nayantara', 'Niir', 'Nira', 'Pardeep', 'Parveen',
	'Payal', 'Pooja', 'Priya', 'Punya', 'Raj', 'Rajkumari',
	'Ratika', 'Roopan', 'Roopi', 'Sana', 'Sanchita',
	'Sangeeta', 'Sanya', 'Sarabjit', 'Sarb', 'Satwant',
	'Seher', 'Shilpa', 'Sharan', 'Sharanjeet', 'Shereen',
	'Shrestha', 'Simran', 'Simrin', 'Sona', 'Sonia',
	'Suhani', 'Sukhi', 'Suki', 'Sumit', 'Sumita', 'Taj',
	'Tamanna', 'Tanveer', 'Taz'
	]

NORTH_INDIAN_SURNAMES = [
	'Arora',  'Asthana',  'Atal',  'Atwal', 'Beigh',
	'Bhagati',  'Bhan',  'Bhat',  'Bhatia',  'Bhatnagar',
	'Bhola',  'Brar',  'Budshah',  'Chadha',  'Cheema',
	'Chetan',  'Chopra',  'Chowlia', 'Dahiya',  'Dedmari',
	'Deswal',  'Dhar',  'Dhawan',  'Dhillon',  'Drabu',
	'Duggal',  'Durani',  'Durrani',  'Gill',  'Goud',
	'Grewal',  'Jitan',  'Kaur',  'Khan',  'Khandol',
	'Khanna',  'Khar',  'Khemu',  'Kher',  'Khurmi',
	'Kilam',  'Kokiloo',  'Koul',  'Kulshreshtha',  'Kumar',
	'Matharoo',  'Mattoo',  'Mehta',  'Mir',  'Misger',
	'Moza', 'Mozaz',  'Mujoo',  'Nadeer',  'Nanda',
	'Sahota',  'Saigal',  'Saini',  'Salh', 'Sandhu',
	'Saproo',  'Saraaf',  'Sardana',  'Saxena',  'Sehgal',
	'Sekhon',  'Seth',  'Sethi',  'Shah',  'Shangloo',
	'Sharma',  'Shastri',  'Shaw',  'Shergill',  'Shoker',
	'Sidana',  'Sidhu',  'Singh',  'Singla',  'Sinha',
	'Smagh',  'Sobti',  'Sodhi',  'Soni',  'Sood',  'Sopori',
	'Srivastava',  'Sultan',  'Sumag',  'Tickoo',  'Toor',
	'Toshkhani',  'Trakroo',  'Tufchi',  'Turki',  'Verma',
	'Virk',  'Wazir',  'Wuthoo',  'Zutshi'
	]

GENERATOR_NORTH_INDIAN = Generator(
	M_FIRST_NORTH_INDIAN,
	F_FIRST_NORTH_INDIAN,
	['Singh'] * 7 + M_FIRST_NORTH_INDIAN,
	['Kaur'] * 7 + F_FIRST_NORTH_INDIAN,
	NORTH_INDIAN_SURNAMES
	)

M_FIRST_SOUTH_INDIAN = [
	'Abhishek', 'Ajay', 'Akki', 'Akshay', 'Aleen', 'Ali',
	'Ambareesh', 'Amit', 'Anand', 'Ananth', 'Ankit',
	'Anurag', 'Arvind', 'Ashrith', 'Ashwin', 'Bantwal',
	'Biju', 'Chandram', 'Chandrasekhar', 'Chandrashekara',
	'Charan', 'Chetan', 'Deepak', 'Dharamapal', 'Eeshaan',
	'Ekanath', 'Eshwar', 'Ganesh', 'Gopalakrishna',
	'Hansraj', 'Hemanth', 'Jagdish', 'Jaidev', 'Jaya',
	'Jayadev', 'Jayant', 'Jayaram', 'Kalyan', 'Karthik',
	'Kirti', 'Madhu', 'Madhukar', 'Manmohan', 'Manoj',
	'Mohan', 'Mohananan', 'Muralidhar', 'Nagaraj',
	'Nagaraju', 'Narasimha', 'Narayana', 'Narendranath',
	'Niranjan', 'Niret', 'Nitin', 'Pavan', 'Phaneendra',
	'Praanshu', 'Prabhakar', 'Prakash', 'Prasad', 'Praveen',
	'Purushothama', 'Radhakrishna', 'Ragavendra',
	'Raghavendra', 'Rahul', 'Rajesh', 'Rakesh', 'Ravi',
	'Rishabh', 'Rohan', 'Roopesh', 'Sandeep', 'Sandesh',
	'Sanketh', 'Sasidhar', 'Shantharam', 'Shibu',
	'Siddhartha', 'Sisir', 'Sivakumar', 'Srikanth',
	'Subramanya', 'Suhas', 'Suman', 'Sunil', 'Sushant',
	'Tushar', 'Tejus', 'Umakant', 'Vamsee', 'Varun',
	'Vasudev', 'Vasudeva', 'Venkat', 'Vinayak', 'Vineej',
	'Vivek', 'Vinod'
	]

F_FIRST_SOUTH_INDIAN = [
	'Aarthi', 'Abhilasha', 'Akansha', 'Akshari', 'Akshatha',
	'Alekhya', 'Amala', 'Ambika', 'Amrita', 'Aneesha',
	'Anita', 'Anitha', 'Anjali', 'Anuradha', 'Anusha',
	'Arati', 'Asha', 'Chandini', 'Chaya', 'Chirashree',
	'Deeksha', 'Deepa', 'Deepika', 'Divya', 'Divyangi',
	'Gayathri', 'Jyothsna', 'Kasturi', 'Kavita', 'Khushi',
	'Kavya', 'Kripa', 'Krishna', 'Lakshmi', 'Mala', 'Manira',
	'Mira', 'Mithra', 'Mona', 'Mounika', 'Nandini', 'Neha',
	'Neena', 'Nidhi', 'Nikita', 'Nikshitha', 'Nivedita',
	'Padma', 'Pooja', 'Poornima', 'Pranita', 'Prathibha',
	'Pratyusha', 'Preeti', 'Prithvi', 'Priya', 'Priyanka',
	'Rakshita', 'Rama', 'Rashmi', 'Rima', 'Rithika', 'Roopa',
	'Sandhya', 'Shailaja', 'Shakuntala', 'Shalini',
	'Shamata', 'Shanthala', 'Sharada', 'Shashi', 'Shifali',
	'Shivali', 'Shreya', 'Shrikala', 'Shruthi', 'Shruti',
	'Shweta', 'Sneha', 'Sohini', 'Sonya', 'Sowmya',
	'Srilatha', 'Srujana', 'Sucheta', 'Sugandhi', 'Sugathri',
	'Sujatha', 'Sulakshana', 'Suri', 'Swetha', 'Tammineni',
	'Tanisha', 'Usha', 'Varsha', 'Veena', 'Vijaylakshmi',
	'Vinusha', 'Vrinda', 'Vybhavi'
	]

SOUTH_INDIAN_SURNAMES = [
	'Adiga', 'Akkarakaran', 'Akkiraju', 'Akula',  'Alva',
	'Amin',  'Anchan',  'Baliga',  'Bangera',  'Bhamidipati',
	'Bhat', 'Biradar', 'Chetty',  'Chowdary', 'Desai',
	'Dhulipala',  'Gounder', 'Gudipudi',  'Gujran',
	'Guruvayoor', 'Ilaiya',  'Indrakanti', 'Karkera',
	'Karne', 'Kattimani', 'Kini',  'Kirodian',
	'Kocheralakota', 'Konar',  'Kondapalli', 'Kota',
	'Kothari',  'Kotian',  'Kudva',  'Kukian',  'Kular',
	'Kumar',  'Kurup',  'Maythil', 'Meena',  'Mudaliar',
	'Mudiraj', 'Muhammadutti', 'Munukutla',
	'Murthiyrakkaventharan',  'Murugan',  'Muthalaly',
	'Muthayan',  'Nair',  'Nambeesan',  'Nandumuru',
	'Nethala', 'Nori',  'Olappamanna', 'Palan',  'Pamarti',
	'Panicker',  'Parupalli',  'Payyade',  'Peera',
	'Peeramaswamyan',  'Pemmaraju',  'Pillai', 'Pisharody',
	'Poojary',  'Prabhu', 'Puranam', 'Puthenveetil',
	'Ranganatham',  'Rebbapragada',  'Reddy',  'Repalle',
	'Rimmalapudi', 'Salian',  'Senthil',  'Shastri',
	'Shenoy',  'Shett',  'Sooriyaprakash',  'Subrahmyan',
	'Sudhakar',  'Susarla',  'Suvarna',  'Tenali', 'Thampi',
	'Tharakan',  'Tirunellai', 'Todiyattu', 'Ullal',
	'Upiyan', 'Vaidyan',  'Valiathan',  'Valluri', 'Varma',
	'Vedantam',  'Vedula', 'Veluram',  'Vijay',
	'Vishwakarma',  'Yadhavar'
	]

GENERATOR_SOUTH_INDIAN = Generator(
	M_FIRST_SOUTH_INDIAN,
	F_FIRST_SOUTH_INDIAN,
	M_FIRST_SOUTH_INDIAN,
	F_FIRST_SOUTH_INDIAN,
	SOUTH_INDIAN_SURNAMES
	)

M_FIRST_EAST_INDIAN = [
	'Abhijit', 'Abinash', 'Ajay', 'Ajaya', 'Ajit', 'Akash',
	'Akshay', 'Ananda', 'Aniket', 'Anshuman', 'Ansuman',
	'Ardhendu', 'Arup', 'Ashirbad', 'Asim', 'Banarji',
	'Bhagaban', 'Bhaskar', 'Bhubaneswar', 'Bhusan', 'Bibhav',
	'Bijay', 'Bijaya', 'Binoy', 'Biswajit', 'Chakradhar',
	'Chandra', 'Chitra', 'Darshan', 'Dayanidhi',
	'Dharmananda', 'Dinesh', 'Ganeswar', 'Harekrushna',
	'Jayaram', 'Jitendra', 'Jogendra', 'Keshari', 'Kumar',
	'Laxman', 'Laxmidhar', 'Lipu', 'Loknath', 'Natraj',
	'Niranjan', 'Madhaba', 'Madhusudan', 'Manas', 'Mano',
	'Manoj', 'Manoranjan', 'Mohan', 'Nanda', 'Narayan',
	'Naresh', 'Pabitra', 'Padmanabh', 'Padmanava',
	'Pitabash', 'Pradeep', 'Prakash', 'Pranoy', 'Prasad',
	'Prasanna', 'Priyadarshan', 'Rabindra', 'Raj', 'Rakesh',
	'Rama', 'Ramakanta', 'Ranjan', 'Rasananda', 'Ratikant',
	'Rituraj', 'Sanat', 'Sangram', 'Sanjay', 'Santosh',
	'Saroj', 'Sashibhusan', 'Shashi', 'Shivam', 'Siddharth',
	'Sidharth', 'Somik', 'Soumit', 'Srastanka', 'Srikanta',
	'Srikrushna', 'Subha', 'Subhransu', 'Subrat', 'Sunil',
	'Suratha', 'Sushant', 'Swadhin', 'Tusar', 'Tushar',
	'Ujjal', 'Vineet'
	]

F_FIRST_EAST_INDIAN = [
	'Aiswarya', 'Anisha', 'Anita', 'Anjali', 'Anu',
	'Aparajita', 'Babina', 'Babu', 'Banita', 'Bhagyashree',
	'Bharati', 'Bidulata', 'Bunushree', 'Chinmayee',
	'Debasmita', 'Deepanjali', 'Deepika', 'Deepsikha',
	'Devoleena', 'Diptimayee', 'Gitanjali', 'Indrani',
	'Ipsita', 'Ishani', 'Itishree', 'Jayashree', 'Janhabi',
	'Jataka', 'Jharna', 'Jhilik', 'Jyotirmayee', 'Kumari',
	'Kuni', 'Lahari', 'Lakhmi', 'Lehenga', 'Lipika',
	'Madhusmita', 'Mala', 'Mamata', 'Mamuni', 'Manaswini',
	'Manju', 'Medha', 'Meenakshee', 'Minakhi', 'Minakshi',
	'Monalisa', 'Nandini', 'Nandita', 'Navnita', 'Nibedita',
	'Odissi', 'Pallabee', 'Pankajini', 'Parbati', 'Pooja',
	'Prabina', 'Preeti', 'Priya', 'Priyadarshini',
	'Priyanka', 'Puja', 'Puspanjali', 'Rashmita', 'Rasmita',
	'Rina', 'Rupali', 'Sandhya', 'Sangeeta', 'Sanjukta',
	'Santoshini', 'Santwona', 'Sareeta', 'Sarina', 'Sarita',
	'Sasmita', 'Shivangi', 'Shivani', 'Shreeja', 'Shreya',
	'Shweta', 'Simran', 'Sonali', 'Srujani', 'Subhalaxmi',
	'Subhashree', 'Subhasmita', 'Suchismita', 'Sunita',
	'Suprabha', 'Swapna', 'Swayam', 'Swayamprabha', 'Tanvi',
	'Tejaswani', 'Tiki', 'Tikismita', 'Tripta', 'Uma'
	]

EAST_INDIAN_SURNAMES = [
	'Behera',  'Bera',  'Bhagawati',  'Bhattacharjee',
	'Bhattacharya',  'Bhaumik',  'Bhowmick',  'Bhuinya',
	'Bidyadhara',  'Biswal',  'Biswas',  'Bodo',  'Bodosa',
	'Bora', 'Borbarua', 'Borbora', 'Borgohain', 'Borgoyary',
	'Boro',  'Borthakur',  'Bose',  'Brahma',  'Buragohain',
	'Bwisumatary',  'Chatterjee',  'Dasgupta',  'De',
	'Deb-Roy',  'Deraiya',  'Deria',  'Dev',  'Dewanji',
	'Dey',  'Diwedi',  'Dolui',  'Dutta',  'Duttagupta',
	'Dwivedi',  'Gotras',  'Guha',  'Gupta',  'Hazary',
	'Khuntia',  'Kundu',  'Maity',  'Malik',  'Mandal',
	'Mardaraj',  'Mazumdar',  'Mech',  'Mir', 'Mishra',
	'Misra',  'Mitra',  'Mochary',  'Mohanty', 'Mohapatra',
	'Mohilary',  'Mondal',  'Mukherjee',  'Mund',  'Muni',
	'Munshi',  'Mushahary',  'Nanda',  'Negi',  'Pati',
	'Pattasani',  'Pattjoshi',  'Pattnaik',  'Pradhan',
	'Praharaj',  'Pratihari',  'Purkayastha',  'Purohit',
	'Raya Guru',  'Routaray',  'Samatasinghar',  'Sanyal',
	'Sardar',  'Sarkar',  'Sarma',  'Satrusalya',
	'Satyapathy',  'Sen',  'Senapati',  'Sengupta',  'Sha',
	'Sharma',  'Shil', 'Sikdar',  'Sil',  'Singh',  'Sinha',
	'Som',  'Srichandan',  'Subba',  'Sundarray',  'Swain',
	'Swargiary'
	]

GENERATOR_EAST_INDIAN = Generator(
	M_FIRST_EAST_INDIAN,
	F_FIRST_EAST_INDIAN,
	M_FIRST_EAST_INDIAN,
	F_FIRST_EAST_INDIAN,
	EAST_INDIAN_SURNAMES
	)

M_FIRST_WEST_INDIAN = [
		'Aashish', 'Adnan', 'Afzal', 'Ajit', 'Ali', 'Alpesh',
	'Amala', 'Amirul', 'Amish', 'Amit', 'Amitabha', 'Anand',
	'Ankeel', 'Arpan', 'Ash', 'Atul', 'Bassem', 'Bharat',
	'Brij', 'Chirayu', 'Deepak', 'Devin', 'Divyesh',
	'Faisal', 'Farshid', 'Fattah', 'Hafizullah', 'Haitham',
	'Hetal', 'Hiren', 'Iftekhar', 'Jaffar', 'Jahirul',
	'Jatin', 'Jay', 'Jigar', 'Kadji', 'Karami', 'Kareem',
	'Kazi', 'Keval', 'Kushal', 'Mahul', 'Makhdoom',
	'Manjeshwar', 'Manoranjan', 'Mayur', 'Milan', 'Mitesh',
	'Mohamed', 'Moeness', 'Mubarek', 'Mukesh', 'Mustafa',
	'Narhari', 'Nariv', 'Nickhill', 'Nilu', 'Nishith',
	'Nusrat', 'Palak', 'Parth', 'Prak', 'Prateek', 'Pritesh',
	'Priyank', 'Punit', 'Punyashlok', 'Qasim', 'Raid', 'Raj',
	'Rajesh', 'Ramtin', 'Riawan', 'Raouf', 'Ruhul', 'Saajan',
	'Said', 'Saiful', 'Salman', 'Sami', 'Samir', 'Sanjib',
	'Sanjiv', 'Satyen', 'Saurabh', 'Shaan', 'Shady',
	'Shahid', 'Shailesh', 'Shilpan', 'Shimit', 'Shyam',
	'Sikandar', 'Tahir', 'Tarun', 'Trithankar', 'Umar',
	'Vilin', 'Yogesh'
	]

F_FIRST_WEST_INDIAN = [
	'Aashka', 'Abhidnya', 'Aishah', 'Alka', 'Amita', 'Anam',
	'Anisha', 'Anita', 'Anjali', 'Anjumon', 'Arti', 'Asha',
	'Ashwini', 'Bhavini', 'Bina', 'Chandni', 'Chetal',
	'Debasmita', 'Debasrita', 'Deepika', 'Dhara', 'Dina',
	'Dipaly', 'Dipita', 'Gauri', 'Hasiba', 'Hatel', 'Heena',
	'Hira', 'Jigna', 'Karishma', 'Kavita', 'Ketaki',
	'Khushbu', 'Leena', 'Maeeva', 'Manisha', 'Manjari',
	'Medha', 'Mira', 'Miral', 'Mona', 'Mousomi', 'Nandita',
	'Neeta', 'Nidhi', 'Nikita', 'Nilema', 'Nimah', 'Nimisha',
	'Nisha', 'Nimmi', 'Nivee', 'Poorvi', 'Pravina', 'Preeti',
	'Preya', 'Pri', 'Priti', 'Priya', 'Punam', 'Purvi',
	'Pushpa', 'Rajeshriben', 'Reema', 'Rina', 'Ritika',
	'Rupal', 'Rupali', 'Salwa', 'Sameen', 'Sampada', 'Sana',
	'Sanjini', 'Sanyogeeta', 'Sanyogita', 'Sarika', 'Savita',
	'Shaina', 'Shraddha', 'Shreya', 'Shreyasee', 'Shruti',
	'Sima', 'Smita', 'Sneha', 'Sonya', 'Sujata', 'Sumedha',
	'Sumitra', 'Surabhi', 'Sushma', 'Tania', 'Tejashree',
	'Toifa', 'Trishla', 'Varsha', 'Vasu', 'Vedika',
	'Vishakha'
	]

WEST_INDIAN_SURNAMES = [
	'Agarkar',  'Amin',  'Bhakta',  'Bhanushali',  'Bhat',
	'Bhave',  'Bhosale',  'Bhosle',  'Bidkar',  'Borkar',
	'Chaudhary',  'Chavan', 'Chawda',  'Chindarkar',
	'Chodankar',  'Chotaliya',  'Chudasama',  'Desai',
	'Deshpande',  'Deuskar',  'Doshi',  'Gadiyar', 'Gaude',
	'Gavaskar',  'Gokhale',  'Gore',  'Ingle',  'Jadhav',
	'Joglekar',  'Joshi', 'Joshi',  'Juhekar',  'Kadam',
	'Kakde',  'Kale',  'Kamerkar',  'Kelkar',  'Kerkar',
	'Khanvilkar',  'Khorjuvekar',  'Kolte',  'Korgaonkar',
	'Kuduva',  'Kulkarni',  'Madgulkar',  'Maindalkar',
	'Mangeshkar',  'Manglokar',  'Mankar',  'Matondkar',
	'Mayekar',  'Medhekar',  'Mehta',  'Merchant',
	'Mhaiskar', 'Mistry',  'Modhwadiya',  'Modi',  'Mohite',
	'Mondkar', 'Mulli', 'Nagpurkar',  'Naik',  'Naralkar',
	'Navalkar',  'Navle', 'Parpati',  'Patel',  'Patil',
	'Pawar',  'Pendharkar',  'Prabhu',  'Rahane',  'Raikar',
	'Rana',  'Rande',  'Rao',  'Rathod',  'Salgaonkar',
	'Salvi',  'Sarvankar',  'Savarkar',  'Shah',  'Shanbhog',
	'Shegaonkar',  'Shekatkar',  'Shinde',  'Shroff',
	'Sisodiya',  'Soman',  'Soni',  'Sukenkar', 'Tanksali',
	'Teli',  'Tendulkar',  'Thakre',  'Vaidya',  'Velip',
	'Vernekar',  'Wankhade'
	]

GENERATOR_WEST_INDIAN = Generator(
	M_FIRST_WEST_INDIAN,
	F_FIRST_WEST_INDIAN,
	M_FIRST_WEST_INDIAN,
	F_FIRST_WEST_INDIAN,
	WEST_INDIAN_SURNAMES
	)

class IndianGenerator(Generator):

	def __init__(self):
		self.north = GENERATOR_NORTH_INDIAN
		self.south = GENERATOR_SOUTH_INDIAN
		self.east  = GENERATOR_EAST_INDIAN
		self.west  = GENERATOR_WEST_INDIAN

	def generate(self, pUnit, pCity, masculine):
		x0y0 = getDataValue("IndianGenerator")
		(x1, y1) = (pCity.getX(), pCity.getY())
		if x0y0 is None:
			x0y0 = (x1, y1)
			setDataValue("IndianGenerator", x0y0)
		(x0, y0) = x0y0
		(dx, dy) = (abs(x1 - x0), abs(y1 - y0))
		BugUtil.debug("Comparing points (%d, %d) ~ (%d, %d)" % (x0, y0, x1, y1))
		if (dx > dy):
			if (x1 > x0):
				return self.east.generate(pUnit, pCity, masculine)
			else:
				return self.west.generate(pUnit, pCity, masculine)
		elif (y1 < y0):
			return self.south.generate(pUnit, pCity, masculine)
		else:
			return self.north.generate(pUnit, pCity, masculine)

GENERATOR_INDIAN = IndianGenerator()

JAPANESE_FAMILY = [
	"Abe", "Ando", "Aoki", "Arai", "Chiba", "Endo",
	"Fujihara", "Fujii", "Fujita", "Fujiwara", "Fukuda",
	"Goto", "Hara", "Harada", "Hasegawa", "Hashimoto",
	"Hayashi", "Hirano", "Ichikawa", "Ikeda", "Imai",
	"Inoue", "Ishida", "Ishii", "Ishikawa", "Ito", "Iwasaki",
	"Kaneko", "Kato", "Kawano", "Kikuchi", "Kimura",
	"Kinoshita", "Kobayashi", "Kojima", "Kondo", "Kono",
	"Koyama", "Kudo", "Maeda", "Maruyama", "Masuda",
	"Matsuda", "Matsui", "Matsumoto", "Miura", "Miyamoto",
	"Miyasaki", "Miyazaki", "Mori", "Morita", "Murakami",
	"Murata", "Nakagawa", "Nakajima", "Nakamura", "Nakano",
	"Nakashima", "Nakayama", "Nishimura", "Noguchi",
	"Nomura", "Ogawa", "Okada", "Okamoto", "Ono", "Ono",
	"Ota", "Otsuka", "Oyama", "Saito", "Saito", "Sakai",
	"Sakamoto", "Sakurai", "Sano", "Sasaki", "Sato",
	"Shibata", "Shimada", "Shimizu", "Sugahara", "Sugawara",
	"Sugiyama", "Suzuki", "Takada", "Takagi", "Takahashi",
	"Takaki", "Takata", "Takeda", "Taketa", "Takeuchi",
	"Tamura", "Tanaka", "Taniguchi", "Uchida", "Ueda",
	"Ueno", "Ueta", "Wada", "Watabe", "Watanabe", "Watanabe",
	"Yamada", "Yamaguchi", "Yamamoto", "Yamasaki",
	"Yamashita", "Yamazaki", "Yokoyama", "Yoshida"
	]

JAPANESE_MALE_GIVEN = [
	"Akemi", "Akihiko", "Akio", "Akira", "Aoi", "Arata",
	"Ayumu", "Daichi", "Daiki", "Daisuke", "Goro", "Gorou",
	"Hachiro", "Hachirou", "Haru", "Haruka", "Haruki",
	"Haruto", "Hayate", "Hayato", "Hibiki", "Hideaki",
	"Hideki", "Hideyoshi", "Hikaru", "Hinata", "Hiraku",
	"Hirohito", "Hiroki", "Hiromasa", "Hiroshi", "Hiroto",
	"Hisoka", "Ichiro", "Ichirou", "Isamu", "Isas", "Itsuki",
	"Jiro", "Jirou", "Jun", "Juro", "Jurou", "Kaede",
	"Kaito", "Kaoru", "Kane", "Katashi", "Katsu", "Katsuo",
	"Katsuro", "Katsurou", "Kazuki", "Kazuo", "Ken",
	"Ken'ichi", "Kenji", "Kenshin", "Kenta", "Kichiro",
	"Kichirou", "Kin", "Kiyoshi", "Kohaku", "Kouki", "Kouta",
	"Kuro", "Kurou", "Kyo", "Kyou", "Makoto", "Masahiro",
	"Masao", "Masaru", "Masato", "Michi", "Minato", "Minoru",
	"Naoki", "Naomi", "Naoko", "Noboru", "Nobu", "Noburu",
	"Nobuyuki", "Nori", "Osamu", "Ren", "Riku", "Rikuto",
	"Rin", "Rokuro", "Rokurou", "Ryo", "Ryoichi", "Ryota",
	"Ryou", "Ryouichi", "Ryouta", "Ryuu", "Ryuunosuke",
	"Saburo", "Saburou", "Shichiro", "Shichirou", "Shin",
	"Shinobu", "Shiori", "Shiro", "Shirou", "Sho", "Shota",
	"Shou", "Shouhei", "Shouta", "Shun", "Sora", "Sota",
	"Souma", "Souta", "Susumu", "Taichi", "Taiki",
	"Takahiro", "Takara", "Takashi", "Takehiko", "Takeshi",
	"Takuma", "Takumi", "Takuya", "Taro", "Tarou", "Tomi",
	"Toshihiro", "Tsubasa", "Yamato", "Yasahiro", "Yasu",
	"Yasuo", "Yemon", "Yori", "Yoshi", "Yoshiro", "Yoshirou",
	"Youta", "Yuki", "Yukio", "Yuu", "Yuudai", "Yuuma",
	"Yuuta", "Yuuto"
	]

JAPANESE_FEMALE_GIVEN = [
	"Ai", "Aiko", "Aimi", "Aina", "Airi", "Akane", "Akemi",
	"Aki", "Akiko", "Akira", "Ami", "Aoi", "Asuka", "Atsuko",
	"Aya", "Ayaka", "Ayako", "Ayame", "Ayane", "Ayano",
	"Chihiro", "Chika", "Chikako", "Chinatsu", "Chiyo",
	"Chiyoko", "Cho", "Chou", "Chouko", "Emi", "Etsuko",
	"Hana", "Hanae", "Hanako", "Haru", "Haruka", "Haruko",
	"Haruna", "Hibiki", "Hikari", "Hikaru", "Hina", "Hinata",
	"Hiroko", "Hitomi", "Honoka", "Hoshi", "Hoshiko",
	"Hotaru", "Izumi", "Junko", "Kaede", "Kanon", "Kaori",
	"Kaoru", "Kasumi", "Kazue", "Kazuko", "Keiko", "Kiku",
	"Kimiko", "Kiyoko", "Kohaku", "Koharu", "Kokoro",
	"Kotone", "Kumiko", "Kyo", "Kyou", "Mai", "Makoto",
	"Mami", "Manami", "Mao", "Mariko", "Masami", "Masuyo",
	"Mayu", "Megumi", "Mei", "Michi", "Michiko", "Midori",
	"Miho", "Mika", "Miki", "Miku", "Minako", "Minato",
	"Minoru", "Mio", "Misaki", "Mitsuko", "Miu", "Miyako",
	"Miyu", "Mizuki", "Moe", "Momoka", "Momoko", "Moriko",
	"Nana", "Nanako", "Nanami", "Naoko", "Naomi", "Natsuki",
	"Natsuko", "Natsumi", "Noa", "Noriko", "Ran", "Rei",
	"Ren", "Riko", "Rin", "Rina", "Rio", "Sachiko", "Saki",
	"Sakura", "Sakurako", "Satomi", "Sayaka", "Sayuri",
	"Setsuko", "Shinju", "Shinobu", "Shiori", "Shizuka",
	"Shun", "Sora", "Sumiko", "Suzu", "Suzume", "Takako",
	"Takara", "Tamiko", "Tomiko", "Tomoko", "Tomomi",
	"Tsubaki", "Tsubame", "Tsubasa", "Tsukiko", "Ume",
	"Umeko", "Wakana", "Yasu", "Yoko", "Yoshi", "Yoshiko",
	"Youko", "Yua", "Yui", "Yuina", "Yuki", "Yukiko", "Yuko",
	"Yumi", "Yumiko", "Yuri", "Yuu", "Yuuka", "Yuuki",
	"Yuuko", "Yuuna", "Yuzuki"
	]

class GenericAsianGenerator(Generator):

	def __init__(self, family, mPersonal, fPersonal):
		super(GenericAsianGenerator, self).__init__(mPersonal, fPersonal, [], [], family)

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			return self.generateInternal(self.masculineFirstNames, [], self.surnames)
		else:
			return self.generateInternal(self.feminineFirstNames, [], self.surnames)

	def generateInternal(self, personal, ignore, family):
		unitName = ""

		firstName = self.choice(family)
		lastName = self.choice(personal)

		unitName = firstName + " " + lastName

		return unitName

GENERATOR_JAPANESE = GenericAsianGenerator(JAPANESE_FAMILY, JAPANESE_MALE_GIVEN, JAPANESE_FEMALE_GIVEN)

KHMER_FAMILY = [
			"Aang", "Aek", "Ang", "Aok", "Bun", "Chan", "Chap",
		"Chea", "Cheam", "Chen", "Cheng", "Chey", "Chhan",
		"Chhay", "Chhem", "Chhet", "Chhim", "Chhit", "Chhorn",
		"Chim", "Chin", "Choem", "Din", "Dith", "Dul", "Duong",
		"Dy", "Eam", "Eav", "Ek", "Hak", "Ho", "Hong", "Hu",
		"Hun", "Iam", "Iem", "Im", "Iv", "Jan", "Jay", "Jen",
		"Jey", "Jin", "Kem", "Keo", "Kep", "Khat", "Khay",
		"Kheang ", "Khiev", "Khim", "Khin", "Khlot",
		"Kim", "Kouch", "Kuy", "Lay", "Lim", "Liv", "Long", "Ly",
		"Ma", "Mao", "Mean", "Meas", "Meng", "Mul", "Muy",
		"Nhek", "Ny", "Ok", "Om", "Ong", "Ouch", "Pang", "Pech",
		"Pen", "Phan", "Phy", "Pich", "Pok", "Ros", "Rouy",
		"Sam", "San", "Sang", "Sao", "Sar", "Sat", "Say",
		"Seang", "Sen", "Seng", "Seoung", "Sieng", "Sin", "So",
		"Sok", "Som", "Son", "Son", "Song", "Sor", "Soun", "Su",
		"Suy", "Taing", "Tang", "Tat", "Teav", "Tep", "Than",
		"Thy", "Toch", "Touch", "Try", "Tum", "Ty", "Uch", "Um",
		"Uy", "Vang", "Yim", "Yos", "Yous", "Yu", "Yun"
	]

KHMER_MALE_GIVEN = [
	"Arun", "Atith", "Bona", "Boran", "Borey", "Bunroeun",
	"Chakra", "Chamroeun", "Chan", "Chankrisna", "Chea",
	"Chhay", "Chhaya", "Chhean", "Chhoum", "Chivan", "Dara",
	"Darany", "Darareaksmey", "Davy", "Haing", "Heng",
	"Khieu", "Khmer", "Kiri", "Kosal", "Kunthear", "Leng",
	"Makara", "Many", "Narith", "Nimith", "Nimol",
	"Noreaksey", "Nuon", "Oudom", "Phala", "Pheakdei",
	"Phirun", "Pich", "Piseth", "Pisey", "Poeu", "Ponleak",
	"Ponleu", "Ponlok", "Prak", "Pros", "Puthyrith",
	"Rachana", "Rainsey", "Raksmei", "Rangsei", "Rangsey",
	"Rasmey", "Rath", "Rathana", "Rathanak", "Rith",
	"Rithipol", "Rithisak", "Samay", "Sambath", "Samnang",
	"Sangha", "Sann", "Saroeun", "Sathea", "Saveth", "Serey",
	"Sereyvuth", "Seven", "Simsung", "Soda", "Sok", "Sokha",
	"Sokhem", "Sokhom", "Somethea", "Sonith", "Sophal",
	"Sophan", "Sophana", "Sophea", "Sopheaktra", "Sopheap",
	"Soriya", "Sorn", "Sotear", "Soth", "Sotha", "Sothea",
	"Sothy", "Srey", "Sunhong", "Thearith", "Vanna",
	"Veasna", "Vibol", "Vichhay", "Vireak", "Visal",
	"Vivadh", "Youk"
	]

KHMER_FEMALE_GIVEN = [
	"Achariya", "Akara", "Anchali", "Arunny", "Ary", "Bopha",
	"Botum", "Boupha", "Champei", "Champey", "Chamroeun",
	"Chan", "Chankrisna", "Chanlina", "Chanmony", "Channary",
	"Chanthavy", "Chantou", "Chantrea", "Chanvatey",
	"Chariya", "Chavy", "Chaya", "Chea", "Chenda", "Chhaiya",
	"Chhean", "Chhorvin", "Chivy", "Choum", "Da", "Daevy",
	"Dara", "Darareaksmey", "Davi", "Jorani", "Kalianne",
	"Kaliyanei", "Kalliyan", "Kanleakhana", "Kannareth",
	"Kannitha", "Kanya", "Kesor", "Kolab", "Kolthida",
	"Kravann", "Kunthea", "Leakena", "Leap", "Mach",
	"Makara", "Malis", "Maly", "Mau", "Mealea", "Mean",
	"Mliss", "Mony", "Nakry", "Nary", "Nearidei", "Neary",
	"Nuon", "Peou", "Phally", "Phary", "Pheakdei",
	"Pheakkley", "Phhoung", "Pich", "Pisey", "Ponlok",
	"Ponnleu", "Punthea", "Putrea", "Rachana", "Rachany",
	"Rangsei", "Reach", "Reaksmey", "Reasmey", "Rom",
	"Rotha", "Roumduol", "Roumjong", "Saley", "Samnang",
	"Samphy", "Savady", "Sawatdee", "Seda", "Seyha", "Sikha",
	"Sinuon", "Sita", "Soboen", "Socheat", "Sok", "Sokha",
	"Sokhanya", "Sokhom", "Sombo", "Sonisay", "Sophal",
	"Sophea", "Sopheap", "Sopheary", "Sophon", "Sophorn",
	"Soportevy", "Soriya", "Sorpheny", "Sotear", "Sotheara",
	"Sothy", "Sourkea", "Sovanara", "Sovandary", "Sovanna",
	"Sovannai", "Sraem", "Srey", "Sreymau", "Sreynuon",
	"Sreypich", "Sros", "Suorsdey", "Taevy", "Thavary",
	"Theary", "Thom", "Thyda", "Tina", "Toch", "Tola",
	"Vanna", "Veasna", "Veata", "Vimean"
	]

GENERATOR_KHMER = GenericAsianGenerator(KHMER_FAMILY, KHMER_MALE_GIVEN, KHMER_FEMALE_GIVEN)

KOREAN_FAMILY = [
		"A", "Aan", "Ae", "Ah", "Ahn", "Ai", "An", "Ar", "Arn",
	"Au", "Ay", "Back", "Bae", "Baek", "Bahk", "Bahn",
	"Bahng", "Bai", "Baik", "Bak", "Ban", "Bang", "Bay",
	"Bean", "Bee", "Been", "Beom", "Bhan", "Bhang", "Bhi",
	"Bhong", "Bi", "Bih", "Bihn", "Bin", "Bing", "Bock",
	"Bog", "Bohng", "Bok", "Bom", "Bong", "Boo", "Booh",
	"Bou", "Bu", "Buh", "Buhm", "Bum", "Byeon", "Byon",
	"Byoun", "Byun", "Ch'a", "Ch'ae", "Ch'ang", "Ch'o",
	"Ch'oe", "Ch'on", "Ch'u", "Cha", "Cha", "Chae", "Chah",
	"Chahng", "Chai", "Chang", "Changgok", "Char", "Che",
	"Chee", "Chegal", "Chekal", "Cheon", "Cheong", "Cheub",
	"Cheung", "Cheup", "Chey", "Chi", "Chin", "Cho", "Choa",
	"Choe", "Choh", "Choi", "Chom", "Chon", "Chong", "Choo",
	"Choon", "Chou", "Choun", "Choung", "Chow", "Choy",
	"Chu", "Chub", "Chuhn", "Chun", "Chung", "Chup", "Chwa",
	"Chwe", "Chyu", "Chung", "Chup", "Cook", "Cynn", "Dae",
	"Dahm", "Dahn", "Dai", "Dam", "Dan", "Dang", "Day",
	"Dea", "Dham", "Dhang", "Dhong", "Do", "Dockko", "Doe",
	"Dogko", "Doh", "Dohn", "Dokgo", "Dokko", "Doko", "Don",
	"Dong", "Dongbang", "Dongpang", "Doo", "Dou", "Du", "Em",
	"Eo", "Eogeum", "Eoh", "Eokeum", "Eom", "Eum", "Eun",
	"Ga", "Gae", "Gah", "Gahl", "Gahm", "Gahn", "Gai", "Gal",
	"Gam", "Gan", "Gang", "Gangjeon", "Gangjon", "Gangjoun",
	"Gangjun", "Gar", "Garl", "Gee", "Geum", "Geun", "Ghim",
	"Gho", "Gi", "Gil", "Gill", "Gim", "Gin", "Go", "Gog",
	"Goh", "Gok", "Gong", "Goo", "Goon", "Goung", "Gu",
	"Guem", "Gug", "Guhn", "Guk", "Gum", "Gun", "Gung",
	"Gwag", "Gwak", "Gwog", "Gwok", "Gwon", "Gye", "Gyeon",
	"Gyeong", "Gyo", "Gyoh", "Ha", "Haam", "Hae", "Hag",
	"Hah", "Hahg", "Hahk", "Hahm", "Hahn", "Hai", "Hak",
	"Ham", "Hamm", "Han", "Hann", "Har", "Hay", "Heo",
	"Heoh", "Her", "Heung", "Ho", "Hoa", "Hoan", "Hoh",
	"Hong", "Hoo", "Hooh", "Houng", "Howa", "Howan", "Hu",
	"Huh", "Huhng", "Hur", "Hwa", "Hwa", "Hwan", "Hwang",
	"Hwangbo", "Hwangpo", "Hyeon", "Hyeong", "Hyon", "Hyong",
	"Hyoun", "Hyoung", "Hyun", "Hyung", "Hung", "I", "Ihn",
	"Im", "In", "Inn", "Ja", "Jae", "Jaegal", "Jahng",
	"Jang", "Janggok", "Je", "Jea", "Jeagal", "Jee", "Jeen",
	"Jegal", "Jei", "Jekal", "Jeo", "Jeom", "Jeon", "Jeong",
	"Jeub", "Jeung", "Jeup", "Jew", "Jhang", "Jhe", "Jhi",
	"Jhun", "Ji", "Jin", "Jo", "Joa", "Joe", "Joh", "Jong",
	"Joo", "Joon", "Jou", "Joung", "Ju", "Jub", "Juhn",
	"Jun", "Jung", "Jup", "Jwa", "Ka", "Kae", "Kah", "Kahl",
	"Kahm", "Kahn", "Kahng", "Kai", "Kal", "Kam", "Kan",
	"Kang", "Kangjeon", "Kangjon", "Kangjoun", "Kangjun",
	"Kar", "Karl", "Kay", "Kee", "Keel", "Keem", "Keum",
	"Keun", "Key", "Khang", "Khee", "Khil", "Kho", "Khong",
	"Khoo", "Khu", "Ki", "Kie", "Kiehl", "Kihl", "Kil",
	"Kim", "Ko", "Koak", "Kog", "Koh", "Kohng", "Kok",
	"Kong", "Koo", "Kook", "Koon", "Koong", "Kor", "Kou",
	"Koung", "Ku", "Kuark", "Kuem", "Kug", "Kuh", "Kuhn",
	"Kuk", "Kum", "Kun", "Kung", "Kwack", "Kwag", "Kwak",
	"Kweon", "Kwog", "Kwok", "Kwon", "Kwoong", "Ky", "Kye",
	"Kyeh", "Kyeon", "Kyeong", "Kym", "Kyo", "Kyoh", "Kyon",
	"Kyong", "Kyoun", "Kyoung", "Kyun", "Kyung", "Kum",
	"Kun", "Lang", "Lee", "Leem", "Lim", "Lin", "Lyang",
	"Lyong", "Ma", "Mae", "Maeng", "Mah", "Mahn", "Maing",
	"Man", "Mangjeol", "Mangjol", "Mangjoul", "Mangjuhl",
	"Mangjul", "Mann", "Mar", "May", "Mee", "Meeh", "Mi",
	"Mih", "Mihn", "Min", "Minn", "Mio", "Mo", "Mock", "Moe",
	"Mog", "Moh", "Mok", "Mook", "Moon", "Mork", "Muhn",
	"Muk", "Mun", "Myeong", "Myo", "Myoh", "Myong", "Myoung",
	"Myung", "Na", "Nae", "Nahm", "Nahn", "Nahng", "Nai",
	"Nam", "Namgoong", "Namguhng", "Namgung", "Namkoong",
	"Namkuhng", "Namkung", "Nan", "Nang", "Narm", "Nay",
	"Nham", "Nhan", "No", "Noe", "Nu", "O", "Oag", "Oak",
	"Ock", "Oe", "Og", "Ogum", "Oh", "Ohg", "Ohk", "Ohm",
	"Ohn", "Ohng", "Ohnn", "Ok", "Okeum", "Okum", "Om", "On",
	"One", "Ong", "Ou", "Oum", "Oung", "P'aeng", "P'an",
	"P'i", "P'il", "P'o", "P'ung", "P'yo", "P'yon", "P'yong",
	"Pack", "Pae", "Pae", "Paek", "Paeng", "Pahk", "Pahn",
	"Pahng", "Pai", "Paik", "Paing", "Pak", "Pan", "Pang",
	"Pann", "Park", "Parn", "Paw", "Pay", "Pean", "Peel",
	"Peng", "Peo", "Peom", "Phan", "Phang", "Phee", "Phi",
	"Phil", "Phin", "Pho", "Phy", "Phyo", "Pi", "Pih",
	"Pihn", "Pil", "Pin", "Ping", "Pio", "Po", "Pock", "Pog",
	"Poh", "Pohng", "Pok", "Pom", "Pong", "Pooh", "Poohng",
	"Poong", "Pou", "Pu", "Puhm", "Puhng", "Pum", "Pung",
	"Pyen", "Pyeng", "Pyeon", "Pyeong", "Pyo", "Pyoh",
	"Pyon", "Pyong", "Pyoun", "Pyoun", "Pyoung", "Pyun",
	"Pyung", "Rah", "Ree", "Rha", "Rhan", "Rhee", "Rhie",
	"Rhim", "Rie", "Rim", "Ro", "Rou", "Ryang", "Ryong",
	"Ryoo", "Ryou", "Ryu", "Ryuk", "Sa", "Sagong", "Sagoung",
	"Sah", "Sahm", "Sahng", "Sakong", "Sakoung", "Sam",
	"Sang", "Sar", "Sarm", "Sea", "See", "Seeb", "Seem",
	"Seen", "Seep", "Sek", "Sen", "Seo", "Seoh", "Seok",
	"Seol", "Seomoon", "Seomun", "Seon", "Seong", "Seonu",
	"Seonwoo", "Seonwu", "Seul", "Seung", "Sheem", "Sheen",
	"Shi", "Shim", "Shin", "Shinn", "Ship", "Shobong",
	"Shopong", "Si", "Si", "Sib", "Sie", "Sihb", "Sihm",
	"Sihp", "Sim", "Sin", "Sinn", "Sip", "So", "Sobong",
	"Soh", "Sohbong", "Sohn", "Sohpong", "Sok", "Sol",
	"Somoon", "Somun", "Son", "Song", "Sonu", "Sonwu", "Soo",
	"Sooh", "Soon", "Sopong", "Soun", "Soung", "Su", "Suh",
	"Suhmoon", "Suhmun", "Suhn", "Suk", "Sul", "Sull", "Sun",
	"Sung", "Sunoo", "Sunwoo", "Sunwou", "Sur", "Surh",
	"Sung", "T'ae", "T'ak", "T'an", "Tack", "Tae", "Tag",
	"Tahk", "Tahm", "Tahn", "Tai", "Tak", "Tam", "Tan",
	"Tang", "Tann", "Tark", "Tay", "Tham", "Than", "Thang",
	"Thong", "To", "Toe", "Togko", "Toh", "Tohn", "Tokko",
	"Toko", "Ton", "Tong", "Tongbang", "Tongpang", "Too",
	"Tou", "Tu", "U", "Ugeum", "Uh", "Uhm", "Ukeum", "Ukum",
	"Um", "Un", "Unn", "Urh", "Van", "Vong", "Wang", "We",
	"Wee", "Weon", "Whun", "Wi", "Wie", "Wo", "Woen", "Won",
	"Wone", "Woo", "Woon", "Wu", "Wuhn", "Wun", "Ya", "Yah",
	"Yang", "Yar", "Ye", "Yeh", "Yeo", "Yeob", "Yeom",
	"Yeon", "Yeong", "Yeop", "Yeoum", "Yeoun", "Yeu", "Yeum",
	"Yeun", "Yi", "Yim", "Yin", "Yo", "Yob", "Yoh", "Yom",
	"Yon", "Yong", "Yoo", "Yook", "Yoon", "Yop", "You",
	"Youb", "Youk", "Youm", "Youn", "Young", "Yu", "Yub",
	"Yuck", "Yug", "Yuh", "Yuk", "Yum", "Yun", "Yune", "Yup",
	"Zoo", "Zu"
	]

KOREAN_MALE_GIVEN = [
	"Beom-soo", "Byung-hoon", "Chang-woo", "Cheol-min",
	"Chi-won", "Chul", "Chul-soo", "Chul-soon", "Dae-hyun",
	"Deok-su", "Do-hun", "Dong-gun", "Dong-won", "Duri",
	"Eun-jae", "Gun", "Hae-il", "Ha-joon", "Ha-neul",
	"Han-jae", "Hee-joon", "Ho", "Ho-jun", "Hong-gi", "Hoon",
	"Hyuk", "Hyun-seok", "Hyung-won", "In-young", "Ja-kyung",
	"Jae", "Jae-geun", "Jae-gyu", "Jae-seop", "Ji-hae",
	"Ji-won", "Jin-wook", "Jong-hyun", "Jong-seok",
	"Joo-hyun", "Joon-hyuk", "Joon-ki", "Jun-seok",
	"Jung-nam", "Ki-ha", "Kwang", "Kwang-hoon", "Kwang-hyok",
	"Kwang-hyun", "Kwang-jo", "Kwang-seon", "Kwang-su",
	"Kyu-chul", "Kyung-chul", "Kyung-gu", "Kyung-hwan",
	"Kyung-lim", "Kyung-mo", "Kyung-tae", "Kyung-taek",
	"Kyung-wan", "Man-soo", "Min-chul", "Min-hyuk",
	"Min-seok", "Min-woo", "Moon-sik", "Mu-yeol", "Mu-young",
	"Myung-hoon", "Myung-hwan", "Myung-soo", "Nam-il",
	"Nam-sun", "Oh-seong", "Sang-chul", "Sang-hoon",
	"Sang-hyun", "Sang-woo", "Se-hun", "Se-yoon", "Seo-jun",
	"Seok-ho", "Seok-ju", "Seong", "Seong-han", "Seong-hoon",
	"Seul-ki", "Seung-heon", "Shi-woo", "Soo-geun",
	"Suk-won", "Sung-chul", "Sung-ha", "Sung-ho",
	"Sung-keun", "Sung-ki", "Sung-soo", "Sung-won",
	"Sung-woo", "Tae-ho", "Tae-soo", "Tae-won", "Tae-woo",
	"Tae-wook", "Tae-woong", "Tae-yong", "Won-chul",
	"Won-ho", "Won-il", "Won-sik", "Won-yong", "Ye-jun",
	"Yeon-seok", "Yo-han", "Yong-gi", "Yong-ho", "Yoon-sung",
	"Young-chul", "Young-geun", "Young-gi", "Young-ha",
	"Young-ho", "Young-hoon", "Young-hwan", "Young-joo",
	"Young-nam", "Young-sik", "Young-soo", "Young-tae",
	"Young-wook", "Yu-jin"
	]

KOREAN_FEMALE_GIVEN = [
	"Areum", "Bit-na", "Bo-kyung", "Bora", "Boram",
	"Byung-hee", "Chae-young", "Chun-ja", "Da-hee", "Do-hee",
	"Do-yeon", "Eun", "Eun-bi", "Eun-chae", "Eun-byul",
	"Eun-mi", "Ga-young", "Go-eun", "Ha-eun", "Hae-won",
	"Hana", "Hee-sun", "Ho-jung", "Hye-bin", "Hye-kyung",
	"Hye-rim", "Hyo-jin", "Hyun", "Hyun-kyung", "In-sook",
	"Iseul", "Jae-shin", "Jae-won", "Jang-mi", "Jeong-ja",
	"Ji-min", "Ji-yeon", "Jin-soo", "Jin-sung", "Jina",
	"Jong-ok", "Joo-won", "Joon-hee", "Jung-ah", "Jung-sook",
	"Ki-jung", "Kwang-hee", "Kyu-won", "Kyung-ah",
	"Kyung-ju", "Kyung-sook", "Man-hee", "Mi-ran", "Mi-sook",
	"Mi-sun", "Mi-yeon", "Mi-young", "Min-jae", "Min-ju",
	"Min-jun", "Min-kyung", "Min-soo", "Min-sun",
	"Min-young", "Mina", "Myung-hwa", "Myung-sook",
	"Na-young", "Nam-seon", "Nari", "Sang", "Sang-mi",
	"Se-bin", "Se-yeon", "Se-young", "Seo-hyeon", "Seo-yeon",
	"Seo-yun", "Seon-ok", "Seong-gyeong", "Si-yeon",
	"So-young", "Soo-ah", "Soo-hee", "Soo-hyun", "Soo-jung",
	"Soo-kyung", "Soo-min", "Soo-yeon", "Soo-young",
	"Sook-ja", "Soon-hee", "Soon-ja", "Sora", "Su-bin",
	"Su-ji", "Su-mi", "Sun-hee", "Sun-hwa", "Sun-mi",
	"Sun-ok", "Sun-young", "Sung-hee", "Sung-hyun",
	"Sung-mi", "Sung-min", "Sung-sook", "Tae-hyun", "Ye-ji",
	"Yeo-jin", "Yeon-hee", "Yeon-woo", "Yeong-ok",
	"Yi-kyung", "Yong-hwa", "Yoo-jung", "Yoo-kyung",
	"Yoon-hee", "Yoon-sook", "Young-ae", "Young-hee",
	"Young-ja", "Young-mi", "Young-sook", "Yu-bin", "Yu-ri",
	"Yumi"
	]

GENERATOR_KOREAN = GenericAsianGenerator(KOREAN_FAMILY, KOREAN_MALE_GIVEN, KOREAN_FEMALE_GIVEN)

MALIAN_FAMILY = [
	u"Abouta", u"Alphadi", u"Amadu", u"Amar", u"Ascofaré",
	u"Aya", u"Ba", u"Bagayogo", u"Bagayoko", u"Bal",
	u"Bangoura", u"Barry", u"Bastide", u"Bathily", u"Berthe",
	u"Bezi", u"Bocoum", u"Bokar", u"Camara", u"Cissé",
	u"Coulibaly", u"Dabo", u"Damba", u"Dao", u"Dei",
	u"Demba", u"Dembelé", u"Deo", u"Diabaté", u"Diagho",
	u"Diagouraga", u"Diakité", u"Diallo", u"Diamoutene",
	u"Diarra", u"Diawara", u"Dicko", u"Dissa", u"Djikine",
	u"Doucoure", u"Doumbia", u"Drabo", u"Dramé", u"Dunbia",
	u"Fakoly", u"Fana", u"Fofana", u"Fonghoro", u"Gandega",
	u"Ghaly", u"Ghoussoub", u"Guindo", u"Hamaha", u"Hanne",
	u"Kalle", u"Kanouté", u"Kanté", u"Koité", u"Konaré",
	u"Konaté", u"Konte", u"Koné", u"Kouyaté", u"Kébé",
	u"Kéita", u"M'Bodji", u"Maiga", u"Musa", u"N'Diaye",
	u"Namory", u"Ndiaye", u"Niane", u"Niang", u"Nimaga",
	u"Ouane", u"Ouologuem", u"Sacko", u"Samake", u"Samassa",
	u"Sangaré", u"Sata", u"Seck", u"Semega", u"Sidibé",
	u"Sinayoko", u"Sininta", u"Sissoko", u"Soumare", u"Sow",
	u"Sumano", u"Suso", u"Sy", u"Tall", u"Tamboura",
	u"Tigana", u"Tounkara", u"Touré", u"Traoré", u"Yahya",
	u"Yatabare"
	]

MALIAN_MALE_GIVEN = [
	u"Abdou", u"Abdoulaye", u"Abdramane", u"Aboubacar",
	u"Adama", u"Afel", u"Ali", u"Alioune", u"Alou", u"Alpha",
	u"Amadou ", u"Amadu", u"Ascofare", u"Assane", u"Baba",
	u"Babemba", u"Bakari", u"Bala", u"Bitòn", u"Boubacar",
	u"Boucader", u"Boureima", u"Cheick", u"Choguel", u"Daba",
	u"Daouda", u"Dioncounda", u"Djelimady", u"Djibril",
	u"Djimi", u"Doumbi", u"Dramane", u"Drissa", u"Fabou",
	u"Falaba", u"Farka", u"Fousseni", u"Gao", u"Garan",
	u"Habib", u"Hampaté", u"Ibrahima", u"Issa", u"Issoufi",
	u"Jah", u"Jali", u"Kankan", u"Kassa", u"Kokalla",
	u"Lobi", u"Magha", u"Maghan", u"Mahamadou", u"Malick",
	u"Mamadou", u"Mamady", u"Mandé", u"Mansong", u"Mari",
	u"Massa", u"Mintou", u"Moctar", u"Modibo", u"Mohamed",
	u"Mory", u"Mountaga", u"Moussa", u"Ngolo", u"Nyama",
	u"Makan", u"Mamadi", u"Nassif", u"Oulematou", u"Oumar",
	u"Ousmane", u"Ouati", u"Rafan", u"Sakura", u"Salif",
	u"Sandaki", u"Sédonoudé", u"Sékou", u"Seku", u"Seydou",
	u"Souéloum", u"Souleymane", u"Soumaila", u"Soumana",
	u"Sundiata", u"Tenema", u"Tiébilé", u"Tiken", u"Toumani",
	u"Wali", u"Yambo", u"Yaya", u"Yeah", u"Yoro",
	u"Younoussi", u"Youssouf"
	]

MALIAN_FEMALE_GIVEN = [
	u"Abibatou", u"Adame", u"Adiaratou", u"Adja", u"Agna",
	u"Aicha", u"Aida", u"Aiicha", u"Aissata", u"Alexia",
	u"Amande", u"Amina", u"Aminata", u"Anata", u"Anita",
	u"Anna", u"Aoua", u"Assitan", u"Aurelie", u"Awa", u"Ba",
	u"Bibata", u"Binette", u"Bintou", u"Chloe",
	u"Christiane", u"Coumba", u"Damba", u"Daouda", u"Diarra",
	u"Dily", u"Djello", u"Djen'hai", u"Djenebou", u"Djenly",
	u"Djenlyy", u"Djènèba", u"Déni", u"Eleonore", u"Fanta",
	u"Fathim", u"Fatim", u"Fatima", u"Fatimah", u"Fatou",
	u"Fatoumata", u"Galia", u"Germaine", u"Halima", u"Haoua",
	u"Hawa", u"Hawaou", u"Inna", u"Jeanne", u"Kadidia",
	u"Kan", u"Kandia", u"Kankou", u"Keita", u"Khadijatou",
	u"Khady", u"Kilia", u"Ko", u"Korian", u"Lara", u"Leila",
	u"Lucie", u"Mady", u"Maimouna", u"Maria", u"Mariam",
	u"Marika", u"Mathi", u"Meryam", u"Micheline", u"Mina",
	u"Monica", u"Moussa", u"Nagobe", u"Nana", u"Nene",
	u"Ouleymatou", u"Oumou", u"Pauline", u"Rahama", u"Rama",
	u"Rokia", u"Sadio", u"Sali", u"Sanou", u"Sara", u"Sarah",
	u"Saratou", u"Sidibé", u"Sira", u"Sophie", u"Stephanie",
	u"Tatiska", u"Touremariam", u"Wassa"
	]

GENERATOR_MALIAN = Generator(MALIAN_MALE_GIVEN, MALIAN_FEMALE_GIVEN, MALIAN_MALE_GIVEN, MALIAN_FEMALE_GIVEN, MALIAN_FAMILY)

MAYAN_MALE = [
		"Acan", "Acat", "Ah", "Ahau", "Ahpu", "Ajbit", "Ajtzak",
	"Alom", "Awilix", "Bacab", "Bahlam", "Batz", "Bitol",
	"Bolon", "Bolontiku", "Buluc", "Cab", "Cabrakan",
	"Cacoch", "Camazotz", "Came", "Can", "Caquix", "Chaac",
	"Chabtan", "Chamahez", "Chicchan", "Chimalmat", "Chin",
	"Chowen", "Chuaj", "Cimi", "Cit", "Cizin", "Colop",
	"Coyopa", "Cum", "Ek", "Gukumatz", "Gutch", "Hachak'yum",
	"Hau", "Hobnil", "Hozanek", "Hun", "Hunab", "Hunahpu",
	"Huracan", "Itzamna", "Itzananohk'u", "Ixbalanque",
	"Ixim", "Ixmucane", "Ixpiyacoc", "Ixtab", "Jacawize",
	"K'awiil", "Kaax", "Kakmo", "Kinich", "Kisin", "Ku",
	"Mam", "Maximon", "Muzen", "Nal", "Naum", "Nohochacym",
	"Oxlahuntiku", "Puch", "Q'uq'umatz", "Qaholom", "Sip",
	"Tabai", "Tepeu", "Ticab", "Tohil", "Ts'akab", "Tum",
	"Tzicnal", "U", "Uayab", "Uichkin", "Utiu", "Uuc",
	"Vatanchu", "Votan", "Vucub", "Xaman", "Xbalanque",
	"Xcarruchan", "Xoc", "Xpiacoc", "Yaluk", "Ye", "Yokte'",
	"Yopaat", "Yuum", "Zac", "Zipacna"
	]

MAYAN_FEMALE = [
	"Akhushtal", "Akna", "Alaghom", "Cab", "Chalchiuhtlicue",
	"Chimalmat", "Colel", "Eme", "Emetaly", "Ha", "Ichika",
	"Inka", "Itzel", "Ixazaluoh", "Ixchel", "Ixtab", "Izta",
	"Kisa", "Mahaway", "Kuk", "Nai", "Nakin", "Naom",
	"Naylay", "Nicte", "Nikaj", "Nikte", "Nimah", "Nimla",
	"Noonsa", "Oyama", "Raxka", "Sacnite", "Sak", "Tikal",
	"Xbalanque", "Xelha", "Xmucane", "Xoc", "Xpiayoc",
	"Xquic", "Yatzil", "Yudelle", "Zac"
	]

GENERATOR_MAYAN = MarkovGenerator(MAYAN_MALE, MAYAN_FEMALE, MAYAN_MALE, MAYAN_FEMALE, MAYAN_MALE + MAYAN_FEMALE, 1, 14)

MONGOLIAN_MALE = [
	"Abaqa", "Abishqa", "Agwang", "Akbarjin", "Altan",
	"Amur", "Arghun", "Aslandorj", "Asudai", "Basang",
	"Bat-Erdene", "Batbayar", "Batsaikhan", "Batu",
	u"Batumöngke", "Bayan", "Bazar", "Bimba", "Borte", "Buqa",
	"Buyan", "Cagdur", "Changha'an", "Chuluunbold", "Damdin",
	"Damrin", "Danzin", "Dorji", "Elbegdorj", "Eljigidey",
	"Enebish", "Engke", "Esen", "Gaanbatar", "Gammala",
	"Ganbold", u"Gansükh", "Gantulga", "Ganzorig", "Ghazan",
	"Gombo", u"Gürragchaa", "Hasi", "Hulagu", "Hulegu",
	"Ibarhasvad", "Irinchin", "Ismayil", "Ivaanjav",
	"Jamsrang", "Jamyang", "Jirgal", "Jochi", "Kesig",
	"Kharbanda", "Khenbish", "Khubilai", u"Khünbish",
	"Khwaja", u"Köke", "Lubsang", "Manduul", "Mangghudai",
	u"Markörgis", "Mart", u"Medekhgüi", "Migmar", u"Möngke",
	u"Mönkhbat", "Nasu", "Nekhii", u"Nergüi", "Nima", "Nohai",
	"Ochir", "Ogtbish", "Oktyabr", "Oljei", "Oljeitu",
	"Otryad", "Orus", "Otgonbayar", "Purbu", "Qutlugh",
	"Sangjai", "Sartaq", "Shagdur", "Teb-tengeri", "Temujin",
	u"Temür", "Terbish", "Toghus", "Tolui", u"Tömörbaatar",
	"Toqto'a", "Toytoya", "Tsakhia", "Wachir", "Yisu",
	"Zhenjin"
	]

MONGOLIAN_FEMALE = [
	"Alan", "Alaqa", "Altanchimeg", "Altani", "Altansarnai",
	"Altansetseg", "Badma", "Barghujin", "Batuldzii",
	"Batzorig", "Bayarmaa", "Berude", "Bolorerdene",
	"Bolormaa", "Boragchin", "Chabi", "Chagur", "Chakha",
	"Chambui", "Dagasi", "Dari", "Dashi", "Dawa",
	"Delgerdzaya", "Delgermaa", "Delgernandjil",
	"Delgerzayaa", "Dorgene", "Dorjpalam", "Dulma",
	"Dzoldzaya", "Ebegei", "Enkhjargal", "Enkhtuya",
	"Enktuyaa", "Erdenechimeg", "Erdeni", "Erdentungalag",
	"Ergene", "Gerel", "Ghoa", "Gorbeljin", u"Gündegmaa",
	"Gurbesu", "Hogelun", "Holuikhan", "Hujaghur", "Ibakha",
	"Idertuyaa", "Jaliqai", "Khadagan", "Khogaghchin",
	"Khojin", "Khongordzol", "Khulan", "Lhagba", "Liankhua",
	u"Lkhagvasüren", "Maral", "Mide", "Mongoljin",
	u"Mönkh-Erdene", u"Mönkhtsetseg", "Mungentuya",
	"Munkhjargal", "Munkhtseteg", "Narengawa", "Narangerel",
	"Narantsetseg", "Narantuyaa", u"Nergüi", "Nomolun",
	"Odgerel", "Odtsetseg", "Odval", "Oghul",
	"Oghul-Qaimish", "Orbei", "Otgonbayar", "Oyon",
	"Oyunbileg", "Oyunchimeg", "Oyuunchimeg", "Radna",
	"Rashi", "Rinchin", "Samga", "Sarangerel", "Sarnai",
	"Sechen", "Shurentsetseg", "Solongo", "Sorqaqtani",
	"Tegusken", "Temulun", "Tsetseg", "Tsetsegmaa",
	"Uranchimeg", "Yesugen", "Yesui"
	]

MONGOLIAN_PATRONYMIC = [
	"Agvaantserengiin", "Ajvaagiin", "Altangerel", "Amgalan",
	"Anandyn", "Balingiin", "Bat-Erdeniin", "Battsetseg",
	"Begziin", "Bekhbat", "Bilegiin", "Bishindeegiin",
	"Borkhuugiin", "Byambajav", "Byambasurn", "Byambyn",
	"Buyanjavyn", "Chimedbazaryn", "Chinbat", "Chuluuny",
	"Dagvyn", "Damdin", "Damdinsurengiin", "Damdiny",
	"Danzandarjaagiin", "Dashdorj", "Dashdorjiin", "Dashiin",
	"Dorjpalamyn", "Dorjsurengiin", "Dugarsurengiin", "Dul",
	"Dulduityn", "Dumaagiin", "Enkhbatyn", "Erdene-Ochiryn",
	"Erdenebileg", "Erdeniin", "Eregzengiin", "Galsan",
	"Ganbaatar", "Ganbaataryn", "Ganzorig", "Gonchigiin",
	"Jambyn", "Jamsrangiin", "Jamtsyn", "Jigidiin",
	"Jugderdemidiin", "Khaisan", "Khashbaataryn",
	"Khatanbaatar", "Khorloogiin", "Losolyn", "Luvsangiin",
	"Luvsanjambyn", "Luvsannorovyn", "Marzan",
	"Mendsaikhany", "Monkhbaataryn", "Munkh-Od", "Murun",
	"Naidangiin", "Namjilyn", "Natsagiin", u"Nergüin",
	"Norovyn", "Ochirbatyn", "Otryadyn", "Pelijidiin",
	"Purevdorjiin", "Ravdangiin", "Rinchen", "Rinchingiin",
	"Ryenchinii", "Sainjargalyn", "Sangidorjiin",
	"Sanjaagiin", "Sanjaasurengiin", "Sembiin", "Sendoo",
	"Sengiin", "Shirnengiin", "Sukhbaatar", "Sukhbaataryn",
	"Tomoriin", "Tsakhiagiin", "Tsedenbal", "Tsegmidiin",
	"Tsendiin", "Tsengeltiin", "Tserenjav", "Tseveensuren",
	"Tsyben", "Vanchinbalyn", "Yumjaagiin", "Yumjiriin",
	"Zandaakhuugiin", "Zevegiin", "Zunduin"
	]

MONGOLIAN_CLAN = [
	"Abag", "Adarkin", "Anggu", "Aruladd", "Bagarin",
	"Bairin", "Barga", "Barghun", "Barulas", "Bayagud",
	"Bayid", "Belgunud", "Besud", "Bolar", "Borjigin",
	"Budagad", "Bugunud", "Buriat", "Chagshighud", "Chahar",
	"Chinos", "Dalad", "Darhad", "Dariganga", "Daur",
	"Dhorolas", "Dongkhayid", "Dorben", "Dorvod", "Ebugejin",
	"Ejine", "Geniges", "Gorolas", "Harachin", "Hoshuud",
	"Hotgoyd", "Hotoh", "Ikires", "Jadaran", "Jalair",
	"Jalayir", "Jarchigud", "Jeghureyid", "Jirgin", "Jungar",
	"Jurud", "Jurkin", "Kazahg", "Kerait", "Kerel",
	"Kereyid", "Kesdiyim", "Khabkhanas", "Khadagid",
	"Khangli", "Kharlugh", "Khatagin", "Khongkhotad",
	"Khourlas", "Manghud", "Merkid", "Monguor", "Myangad",
	"Naiman", "Noyakin", "Oirat", "Olkhunugud", "Olkunud",
	"Onggur", "Onniud", "Oold", "Ordos", "Oronar", "Oyirad",
	"Saghayid", "Saljigud", "Sansar", "Sant", "Sukeken",
	"Sunid", "Taijut", "Tanghut", "Tatar", "Tayichigud",
	"Torguud", "Tsaatan", "Tsagaan", "Tubas", "Tubegen",
	"Tumd", "Ugusin", "Uighur", "Ungirad", "Uriangkhai",
	"Urit", "Ursud", "Urugud", "Uzemchin", "Zahchin",
	"Zerdnoot"
	]

class MongolianGenerator(Generator):

	def __init__(self, patronymic, mPersonal, fPersonal, clan, minlen, maxlen):
		super(MongolianGenerator, self).__init__(mPersonal, fPersonal, [], [], [])
		self.patronymic = patronymic
		self.clan = clan
		self.minlen = minlen
		self.maxlen = maxlen
		BugUtil.debug("%s" % self.__dict__)

	def generate(self, pUnit, pCity, masculine):
		BugUtil.debug("generate(%s, %s, %s)" % (pUnit, pCity, masculine))
		if (masculine):
			return self.generateInternal(self.masculineFirstNames, self.patronymic, self.clan)
		else:
			return self.generateInternal(self.feminineFirstNames, self.patronymic, self.clan)

	def generateInternal(self, personal, patronymic, clan):
		BugUtil.debug("generateInternal(%s, %s, %s)" % (personal, patronymic, clan))

		primaryName = self.choice(personal)
		secondaryName = self.choice(patronymic)
		tertiaryName = self.choice(clan)

		shortName = secondaryName + ' ' + primaryName
		longName = tertiaryName + ' ' + shortName

		if (len(shortName) < self.minlen and len(longName) <= self.maxlen):
			return longName
		else:
			return shortName

GENERATOR_MONGOLIAN = MongolianGenerator(MONGOLIAN_PATRONYMIC, MONGOLIAN_MALE, MONGOLIAN_FEMALE, MONGOLIAN_CLAN, 21, 30)

# From Personal Names Of Indians Of New Jersey, By William Nelson, 1904
NATIVE_AMERICAN = [
	"Abozaweramud", "Acchipoor", "Achcolsoet", "Ackitoauw",
	"Agnamapamund", "Ahtakkones", "Ahwaroeb", "Aiarottw",
	"Aiarotuv", "Allowayes", "Alpoongan", "Ambehoes",
	"Amegatha", "Amois", "Amoneino", "Anachkooting",
	"Anaren", "Anasan", "Ancnock", "Anennath", "Apahon",
	"Apauko", "Apinamough", "Appamankaogh", "Apperinges",
	"Apperingues", "Aquaywochtu", "Arackquiaaksi",
	"Arahiccon", "Aronioco", "Aroorhikan", "Arouweo",
	"Arouwere", "Arromeauw", "Arrorickan", "Ashanham",
	"Ashitaman", "Assawakow", "Assemahaman", "Assowaka",
	"Attahissha", "Auspeakan", "Aweham", "Awehela",
	"Aweonemo", "Awhehon", "Awhips", "Awies", "Awips",
	"Awisham", "Awoonemo", "Awquawaton", "Ayamanug",
	"Ayamanugh", "Barrenach", "Bawagtoons", "Beoppo",
	"Bomokan", "Bussabenaling", "Cacanakque", "Calkanicha",
	"Camoins", "Canackamack", "Canandus", "Cancheris",
	"Canundus", "Capatamin", "Capatamine", "Capenikirckon",

	"Capenokanickon", "Capenokirckon", "Capesteham",
	"Capeteham", "Caponeaoconeacn", "Caponockous", "Capoose",
	"Captahem", "Captamin", "Capteham", "Carakkoon",
	"Carstangh", "Cawackes", "Charaakoon", "Charakkaon",
	"Charakon", "Charraroon", "Chechanaham", "Checokas",
	"Cherawas", "Chygoe", "Cinanthe", "Coathowe",
	"Cockalalaman", "Cohevwichick", "Comascoman", "Commoris",
	"Comshopy", "Comtcommon", "Conackamack", "Conckee",
	"Conincks", "Coninko", "Contomohickon", "Coovang",
	"Coovange", "Copenakoniskon", "Coponnockou",
	"Cosecoping", "Cottenochque", "Cowalanuck", "Cowescomen",
	"Croppun", "Cuahiccon", "Cuish", "Cuttencquoh",
	"Echkamare", "Eckenerehim", "Edgaques", "Egohohoun",
	"Egotchowen", "Egshohoun", "Ekinerchin", "Elalie",
	"Emeros", "Emerus", "Emoros", "Emris", "Encheim",
	"Enequete", "Ensanckes", "Eramky", "Eriwoneck",
	"Eschapous", "Eschapouse", "Escharck", "Escharecek",
	"Eschereck", "Eshokey", "Eskokey", "Etgaqui", "Ethoe",
	"Etthunt", "Feetee", "Gapee", "Genemay", "Ghonnojea",
	"Gnickap", "Gooteleeke", "Gosque", "Gottawamerk",
	"Gwach", "Hagkinsiek", "Haham", "Haharois", "Hairish",
	"Hamahem", "Hamakenon", "Hamemohakun", "Hanayaham",
	"Hanayahame", "Hanrapen", "Hanyaham", "Hanyahanum",
	"Hapehucquona", "Hapehucquoxa", "Hapenomo", "Harmanus",
	"Haughnum", "Haverstroo", "Hayamakeno", "Henemohakun",
	"Henemohokun", "Hepeneman", "Hepihance", "Hielawith",
	"Hiphockanoway", "Hippoquonow", "Hitock", "Hiton",
	"Hoaham", "Hoaken", "Hockan", "Hoeham", "Hoham",
	"Homeyquoan", "Homeyquoaw", "Hooham", "Hopaijock",
	"Houghamc", "Hughon", "Iakhursoe", "Iareandy",
	"Iauwandy", "Ichchepe", "Ipan", "Ireoseke", "Irooseeke",
	"Irramgen", "Irramighkim", "Irramigkin", "Isarick",
	"Ishavekak", "Jackickon", "Jahkiosol", "Jakhursoe",
	"Jantekoes", "Japaan", "Japhome", "Jehokemun",
	"Kaanserein", "Kagkennip", "Kagnoonnen", "Kahaew",
	"Kaharosse", "Kanashalees", "Karstangh", "Kasamen",
	"Kastangh", "Katamas", "Keckquennen", "Keekott",
	"Kekehela", "Kekroppamant", "Keksameghn", "Kenarenawack",
	"Keneckome", "Kenockome", "Kepanoockonickon", "Keromack",
	"Keromacke", "Kesshuwicon", "Kesyaes", "Kewigtaham",
	"Kichewiffwam", "Kickan", "Kighewigwom", "Kikitoauw",
	"Kitmarius", "Knatsciosan", "Knoshieoway", "Kohonk",
	"Konackama", "Konjuring", "Konockama", "Konran",
	"Korougha", "Kovand", "Kueshmoway", "Kwoytes", "Lames",
	"Lammusecon", "Laparomza", "Lapink", "Lappawinza",
	"Lawicowighe", "Lawyhaman", "Lawykaman", "Loantique",
	"Loulax", "Lumoseecon", "Lumoseecon", "Machcopoikan",
	"Machcopoiken", "Macheses", "Machierek", "Machkote",
	"Machockan", "Machohan", "Machpetuske", "Machpoikan",
	"Machpunk", "Mackquinakhim", "Maemsey", "Maghpeta",
	"Mahagpeta", "Mahamickwon", "Mahawksey", "Mahgpeta",
	"Mahomecum", "Mahwtatatt", "Maiskanapulig", "Mameeress",
	"Mamerisco", "Mamustome", "Manamasamet", "Manamowaone",
	"Manansamit", "Manansamitt", "Manawayrtim", "Manawayrum",
	"Manawkyhickon", "Mandenark", "Manhauxett", "Manickopin",
	"Manickty", "Manisem", "Manisinim", "Manoky", "Manschy",
	"Manseim", "Manshim", "Manshuen", "Mansiem", "Mansinim",
	"Manumie", "Marchaiit", "Marenaw", "Mariner",
	"Marquinaskim", "Maskainapulig", "Massetuewop",
	"Mastewap", "Matachena", "Matamyca", "Matanoo",
	"Matapeeck", "Mataro", "Mataros", "Matchaak", "Matchues",
	"Materas", "Matskath", "Mattamiska", "Mattano",
	"Mattapeas", "Mattenon", "Mattsom", "Matyawakum",
	"Maundicon", "Mayawaykum", "Mechekamee", "Mecliat",
	"Mecokin", "Mecoppy", "Meheekissne", "Mejawapapim",
	"Mekekett", "Mekemickon", "Mekquam", "Mellnighperim",
	"Memerescum", "Memereskum", "Memewockan", "Memiseraen",
	"Memmes", "Menanse", "Menarhohondoo", "Menaukahickon",
	"Mendawack", "Mendawasey", "Mendenmass", "Mengootecus",
	"Mennesey", "Mensier", "Menumheck", "Merchant",
	"Merickanaipugh", "Meridanasey", "Merkvan", "Meroppe",
	"Mesawapapim", "Mesawpapim", "Mesehoppe", "Meshocorrang",
	"Meshuhow", "Messingpejun", "Messingpepin", "Metamisco",
	"Metapes", "Metapis", "Metappis", "Metasheny", "Metjes",
	"Metremickin", "Mettatoch", "Mettechmahon", "Mettkett",
	"Mihiowen", "Mindawas", "Mindowashwen", "Mindowaskein",
	"Mingm", "Minqua", "Minqualakyn", "Mintagetquis",
	"Mintamessems", "Mitop", "Mochsay", "Mochson",
	"Mockhanghan", "Mogquack", "Mohawksey", "Mohing",
	"Mohocksey", "Mohowuquando", "Mohowuqvande",
	"Mohusowungie", "Mohutt", "Mokohoss", "Mokowisguanda",
	"Mokowuquande", "Mokowuquarule", "Molhunt", "Mondsolom",
	"Monouckkomen", "Moonis", "Mowessawach", "Mowppy",
	"Mullis", "Mumshaw", "Naamucksha", "Nachoenkquy",
	"Nacholas", "Nachpong", "Nackoniakene", "Nackpunck",
	"Naktzekena", "Namenish", "Namerisko", "Nameth",
	"Namiliskont", "Nanhamman", "Nantzechena",
	"Nathpoenckque", "Nauhoosing", "Naweenak", "Nawenaka",
	"Nawishawan", "Nawishawor", "Nechtan", "Neckaoch",
	"Necomis", "Necosshebesco", "Nectothhoathhocke",
	"Negacape", "Neheekan", "Nehuoing", "Nekachtqua",
	"Nekolhuck", "Nekolkuk", "Nelquethun", "Neman",
	"Nemeness", "Nemeno", "Nemow", "Nepeas", "Neshowwan",
	"Neskeglat", "Neskiglawit", "Neskilanitt", "Neskorhock",
	"Netothhothhocke", "Newenapee", "Neweneka", "Newsego",
	"Nianick", "Nieshaw", "Nieshawand", "Nieshwand",
	"Niesquawende", "Nigkanis", "Nihcopwn", "Nihcowen",
	"Nikolhuck", "Nimham", "Nimhammowe", "Nimhaon",
	"Nockapowicke", "Nomalughalen", "Nomaquwaken",
	"Nonaragnen", "Nonsechem", "Nonzieckim", "Nopuck",
	"Notthornon", "Nouxpecoshot", "Nowanike", "Nowenock",
	"Nummi", "Nummy", "Ockanickon", "Oheloakhi", "Ohwsilopp",
	"Okanickkon", "Okeyman", "Okonycan", "Olamoeerinck",
	"Olamonossectink", "Olamonossecunk", "Olomosecunk",
	"Onachpong", "Onachponguam", "Onagepunk", "Onatagh",
	"Onoragquin", "Opollon", "Opollonwhen", "Oragnap",
	"Orandawaco", "Oranddaqua", "Oratam", "Oratamin",
	"Oratamy", "Oratan", "Oraton", "Osolowhema",
	"Osolowhenia", "Ouiasecamont", "Ouramokon",
	"Ourapakomun", "Ourapo", "Oweeneno", "Owonomus",
	"Owramokan", "Owramokoan", "Paakek", "Paakeksikaak",
	"Paaklisekaak", "Pachem", "Paghquehom", "Paiquahakopawa",
	"Paiquashakopawa", "Pajpemoor", "Pakehautas",
	"Pamacorne", "Pamascome", "Pamascone", "Pamehelett",
	"Panaway", "Panktoe", "Papejeco", "Papejecop",
	"Paponerom", "Paquasha", "Paquashakoppawa", "Pasachynom",
	"Passakegkey", "Patchtan", "Pawark", "Pawarone",
	"Pawmetop", "Payhicken", "Paymell", "Paywarren",
	"Peanto", "Pearawe", "Peccachica", "Peckcanouse",
	"Pecrore", "Pekawan", "Pekomon", "Pelopec", "Pelowash",
	"Pemattase", "Pemekoy", "Pemendoway", "Pemhacky",
	"Pemhus", "Pemropo", "Pemus", "Penkoanus", "Pennekeck",
	"Pequacheak", "Pequehohup", "Perawae", "Perewyn",
	"Perkaonus", "Perketeecka", "Pernpath", "Peropay",
	"Perowes", "Perro", "Peruptah", "Petheatus",
	"Pewaherenoes", "Pewerighweiraghen", "Pewropa",
	"Pewropo", "Pierwim", "Piewecherenoes", "Pishot",
	"Pleeze", "Pluze", "Poanto", "Pojpemoor", "Pombelus",
	"Pombolus", "Pomiechowar", "Porrupha", "Potasko",
	"Powantapis", "Powas", "Poyhek", "Preakae", "Pulalum",
	"Pumalum", "Pumpshire", "Pyahicken", "Quackpacktequa",
	"Quaghhum", "Quahick", "Quanalam", "Quanolam",
	"Quaquahela", "Quaquay", "Quaquenow", "Queehloe",
	"Queenemenka", "Queickolen", "Quenajowmon",
	"Quenalowmon", "Quenamaka", "Queneemaka", "Quenelowmon",
	"Quenemeka", "Queramack", "Queramacke", "Querameck",
	"Queremack", "Queromack", "Queromak", "Queskakous",
	"Quiasecament", "Quiatemans", "Quichtoe", "Quiekquaaren",
	"Quindamen", "Quiquahalah", "Quiqvonde", "Quishive",
	"Quisquand", "Ragolen", "Ragolin", "Raljolin",
	"Rarawaken", "Rawantagwas", "Rawantagwaywoahg",
	"Rawantaques", "Rawatones", "Rawautaqwaywoahg", "Rawtom",
	"Remmatap", "Rennowighwan", "Romasickamen", "Rookham",
	"Roweyton", "Rumashekah", "Sacarois", "Saccatorey",
	"Sachema", "Sackares", "Sackarois", "Sackatois",
	"Sackima", "Sackwomeck", "Sacqueerawe", "Saghkow",
	"Saghtew", "Sagnhoora", "Sagtew", "Sakamoy", "Sames",
	"Saphoc", "Saphow", "Saquemoy", "Sarqueeawee",
	"Sasakaman", "Sasakomau", "Sasakomaus", "Savankun",
	"Sawotbouc", "Schoppie", "Seaheppee", "Seapeckne",
	"Secane", "Secatareus", "Sehoppy", "Sekappie",
	"Sennachus", "Seowcghamin", "Sepeconah", "Sepequena",
	"Sereckham", "Serickham", "Seskiquoy", "Sesrigkam",
	"Sessom", "Seuakhenos", "Sewapierinom ", "Sewecbromb",
	"Seweckronek", "Seweggkamin", "Seytheypoey", "Shacanum",
	"Shaphae", "Shappeara", "Shapundqueho", "Shawkanum",
	"Shawsuna", "Shenocktos", "Shenolape", "Shenolope",
	"Sheoppy", "Sherikham", "Shochanam", "Shopawa",
	"Showpawa", "Sickajo", "Sickonesyns", "Siekaak",
	"Sietey", "Sipham", "Sipheme", "Siphemerawantaques",
	"Soaltus", "Sopon", "Squahicken", "Squekkon",
	"Succolana", "Suckey", "Supapatonarum", "Swampy",
	"Swanamemigh", "Swanpis", "Swauela", "Sweikkon",
	"Sycakeska", "Tachthochear", "Tadeuskund", "Taepan",
	"Taepgan", "Taghkospeno", "Taghquekom", "Talaman",
	"Talawnemun", "Tallaca", "Tallquapie", "Tamack",
	"Tamage", "Tamaque", "Tantaqua", "Tantaque", "Tanteguas",
	"Tapan", "Tapashito", "Tapehaw", "Tapehou", "Tapehow",
	"Tapeshaw", "Tapgow", "Taphaow", "Taphome", "Taphow",
	"Tapionawikon", "Taptawappamund", "Tashopwycam",
	"Tatameckko", "Tatamoekho", "Tawagkis", "Tawakwhekon",
	"Tawapung", "Tawawoino", "Tawhaman", "Tawlaman",
	"Teanish", "Teaunis", "Teedyescung", "Teedyescunk",
	"Tehokemun", "Tekwappo", "Temeny", "Temris",
	"Tenishmonhoman", "Tepgaw", "Teptaomun", "Teptaopamun",
	"Teshmokamm", "Tessiocon", "Tetakomes", "Tetakomis",
	"Teteuscun", "Tetgwambes", "Therinques", "Thetochhulun",
	"Thingorawis", "Tichewokamin", "Timmecole",
	"Tiptaopaman", "Tishiwokamin", "Tockney", "Tohenem",
	"Tokung", "Tokuny", "Tollquapie", "Tolomhon",
	"Tontomohikon", "Topgow", "Topheom", "Tophouw",
	"Toppanickon", "Topphow", "Topponickon", "Torocho",
	"Tospecsmick", "Totamy", "Touwithwitch", "Towachkack",
	"Towchwa", "Toweckwa", "Turantecos", "Tutalayo",
	"Veraggeppe", "Vevenutting", "Vorgaon", "Vugahen",
	"Wachtaew", "Waertsen", "Wagakseni", "Waghkseni",
	"Waiwemitting", "Wakaghshum", "Wakitaroe",
	"Wallammassekaman", "Walloughkomor", "Walough",
	"Waloughpekomon", "Wamascuoning", "Wamesane",
	"Wamveguponge", "Wanamasoa", "Wanparent", "Wapamuck",
	"Waparent", "Wappappen", "Wapparent", "Warham",
	"Warinanco", "Warkop", "Wasconhtow", "Washenoa",
	"Washorkeheen", "Waskoena", "Waskonahtaw", "Wassakorois",
	"Wataamemau", "Watamim", "Wataminian", "Watehpogtaen",
	"Wathkath", "Wauhaway", "Waukaucoimau", "Waukaucoimaus",
	"Wauweguponge", "Wauxyash", "Wauyasteen",
	"Wavveeinetting", "Wawakerewanan", "Wawaleaseed",
	"Waweeinetting", "Waweiagin", "Wawejaik", "Wawejask",
	"Wawenoton", "Waweyask", "Wawinotunce", "Wawmasawing",
	"Wawopekeshot", "Waymote", "Waypeka", "Wayqueenhunt",
	"Waywaramong", "Wayweenhunt", "Wayweenotan",
	"Waywinontunce", "Wayworarnong", "Wecaprokikan",
	"Weequahalaw", "Weequehelah", "Weequoehela",
	"Weequohela", "Weghwewenin", "Wegwowerim", "Wehakemeco",
	"Weighrerens", "Weimenes", "Weiquaheilah", "Wellocke",
	"Wenacanikoman", "Wenamick", "Wendamkamon", "Wennaminck",
	"Wequahalah", "Wequalia", "Wequeala", "Wequehalah",
	"Wequehalye", "Wesavanekunk", "Weshevanakun",
	"Weskeakitt", "Wettanesseck", "Wewanapo", "Wewanatimus",
	"Wewenatokwee", "Wewernoling", "Wewonapee",
	"Weyarawaghheyn", "Weyarawoghhecum", "Wheren", "Whinsis",
	"Whokengapet", "Whusquataghey", "Wicham", "Wickawela",
	"Wickquaylas", "Wickwam", "Wickwamrookham", "Wickwela",
	"Wickwella", "Wiequahila", "Wiewyt", "Wighkokenmi",
	"Wikgaylas", "Wikquaylas", "Willockwis", "Winocksop",
	"Winym", "Wiquales", "Wittamackpao", "Woerantaghquey",
	"Woggermahameck", "Wogwapchakin", "Woloughpekemon",
	"Wowapekoshot", "Wowapekoshots", "Wromananung",
	"Wyannattamo", "Yamatabenties", "Yaupis", "Youthsen"
	]

class NativeAmericanGenerator(MarkovGenerator):

	def __init__(self, names, minlen, maxlen):
		super(NativeAmericanGenerator, self).__init__(names, names, names, names, names, minlen, maxlen)

	def generateMarkov(self, mcf, mcm, mcl):
		firstName = ""

		while (len(firstName) < self.minlen):
			firstName = mcf.newName()

		secondName = ""
		while (len(secondName) < self.minlen):
			secondName = mcf.newName

		return firstName + " " + secondName

GENERATOR_NATIVE_AMERICAN = NativeAmericanGenerator(
	NATIVE_AMERICAN,
	4, 18
	)

M_FIRST_OTTOMAN = [
	u"Abd al-Aziz", u"Abdul Baqi", u"Abdul Halim",
	u"Abdul Hamid", u"Abdul Haq", u"Abdul Jamil",
	u"Abdul Karim", u"Abdul Latif", u"Abdul Majid",
	u"Abdul Malik", u"Abdul Kadir", u"Abdullah",
	u"Abd al-Rahman", u"Abidin", u"Adem", u"Adnan",
	u"Afshin", u"Ahmad", u"Akagündüz", u"Akdemir", u"Akif",
	u"Akin", u"Aladdin", u"Ali", u"Ali Reza", u"Alican",
	u"Alisan", u"Alkan", u"Alp", u"Alparslan", u"Alpaslan",
	u"Alpay", u"Alper", u"Altan", u"Altug", u"Amir", u"Anil",
	u"Apak", u"Arat", u"Arda", u"Arif", u"Arslan", u"Artun",
	u"Asem", u"Asik", u"Aslan", u"Ata", u"Atay", u"Atif",
	u"Atil", u"Atiq", u"Attila", u"Avni", u"Ayberk",
	u"Aydemir", u"Aydin", u"Aydogan", u"Ayik", u"Aykut",
	u"Aytek", u"Ayvaz", u"Azmi", u"Baba", u"Baha",
	u"Baha'al-Din", u"Bahadir", u"Bahri", u"Baki", u"Baris",
	u"Barlas", u"Barlas", u"Basar", u"Basri", u"Batikan",
	u"Batu", u"Batuhan", u"Bayram", u"Bedrettin", u"Bedri",
	u"Behçet", u"Bekir", u"Berat", u"Berk", u"Berkay",
	u"Besim", u"Beyazid", u"Bilal", u"Birkan", u"Birol",
	u"Bolad", u"Bora", u"Boran", u"Bugra", u"Bülent",
	u"Bulut", u"Bünyamin", u"Burak", u"Burhan", u"Büyük",
	u"Cafer", u"Çagatay", u"Çagdas", u"Çaglar", u"Cahit",
	u"Can", u"Candemir", u"Caner", u"Cavit", u"Celal",
	u"Çelik", u"Cem", u"Cemal", u"Cemil", u"Cengiz", u"Cenk",
	u"Çetin", u"Cevdet", u"Cevher", u"Çevik", u"Ceyhun",
	u"Cihat", u"Coskun", u"Cumali", u"Cumhur", u"Cüneyt",
	u"Daud", u"Dede", u"Demir", u"Dervis", u"Devlet",
	u"Dilaver", u"Dogan", u"Dogu", u"Dogukan", u"Dogus",
	u"Doruk", u"Dündar", u"Durmus", u"Dursun", u"Edip",
	u"Efe", u"Ege", u"Egemen", u"Ekrem", u"Emin", u"Emrah",
	u"Emre", u"Ender", u"Enes", u"Engin", u"Enis", u"Enver",
	u"Eray", u"Ercan", u"Ercüment", u"Erdal", u"Erdem",
	u"Erden", u"Erdinç", u"Erdogan", u"Erem", u"Eren",
	u"Ergin", u"Ergün", u"Erhan", u"Eris", u"Erkan",
	u"Erkin", u"Erman", u"Erol", u"Ersan", u"Ersin",
	u"Ertan", u"Ertug", u"Ertugrul", u"Esref", u"Ethem",
	u"Evrim", u"Eyüp", u"Ezel", u"Fadel", u"Fahir", u"Fahri",
	u"Farooq", u"Fatih", u"Fatin", u"Fazil", u"Fazli",
	u"Fehmi", u"Ferdi", u"Ferhat", u"Feridun", u"Ferit",
	u"Ferman", u"Fethi", u"Fevzi", u"Feyyaz", u"Fikri",
	u"Fuad", u"Fuat", u"Furkan", u"Galip", u"Ghazanfar",
	u"Giray", u"Gökay", u"Gökçen", u"Gökdemir", u"Gökhan",
	u"Göksu", u"Gültekin", u"Gündogdu", u"Gündüz", u"Güner",
	u"Günes", u"Gür", u"Gürhan", u"Gürkan", u"Gürsel",
	u"Güven", u"Güvenç", u"Haci", u"Hakan", u"Hakki",
	u"Haldun", u"Halim", u"Halit", u"Haluk", u"Hamdi",
	u"Hamit", u"Hamza", u"Hanefi", u"Hani", u"Harun",
	u"Hasib", u"Hasim", u"Hassan", u"Hayati", u"Haydar",
	u"Hayrettin", u"Hayri", u"Hifzi", u"Hikmet", u"Hilmi",
	u"Hizir", u"Hoca", u"Hulusi", u"Hurairah", u"Hürriyet",
	u"Hursit", u"Hüsnü", u"Hüsrev", u"Hussein", u"Ibrahim",
	u"Ibro", u"Idris", u"Ihsan", u"Ilhami", u"Ilhan",
	u"Ilker", u"Ilter", u"Ilyas", u"Inan", u"Inanç",
	u"Irfan", u"Irsadi", u"Isa", u"Ishak", u"Isik",
	u"Iskender", u"Ismail", u"Ismet", u"Istemi",
	u"Istemihan", u"Izzet", u"Kaan", u"Kadir", u"Kadri",
	u"Kagan", u"Kahraman", u"Kamran", u"Kartal", u"Kaya",
	u"Kazem", u"Kemal", u"Kenan", u"Kerem", u"Kerim",
	u"Khalil", u"Kivanç", u"Koca", u"Köksal", u"Koray",
	u"Korhan", u"Korkut", u"Kubilay", u"Kürsad", u"Kürsat",
	u"Kurtoglu", u"Kutalmis", u"Kutay", u"Kutlu", u"Kutlug",
	u"Levent", u"Levni", u"Lokman", u"Mahir", u"Mahmud",
	u"Majid", u"Mamdouh", u"Mansur", u"Marwan", u"Mazlum",
	u"Mehmed", u"Mehmet Akif", u"Mehmet Ali", u"Mehmet Emin",
	u"Melih", u"Memis", u"Menderes", u"Mengi", u"Mengü",
	u"Mert", u"Mesut", u"Mete", u"Metehan", u"Metin",
	u"Mevlüt", u"Mithat", u"Muammer", u"Müfit", u"Muhammad",
	u"Muharrem", u"Muhiddin", u"Muhsin", u"Muhtar",
	u"Müjdat", u"Mukerrem", u"Mumtaz", u"Munib", u"Munir",
	u"Musa", u"Muslim", u"Mustafa", u"Mutlu", u"Muzaffar",
	u"Nabi", u"Naci", u"Nadeem", u"Nafiz", u"Naim", u"Namik",
	u"Nasim", u"Nasir", u"Nasri", u"Nasuh", u"Nazif",
	u"Nazim", u"Nazmi", u"Necati", u"Necdet", u"Necip",
	u"Necmettin", u"Necmi", u"Nejat", u"Nevzat", u"Nezir",
	u"Niazi", u"Nihat", u"Nizamettin", u"Nuri", u"Nurullah",
	u"Nusrat", u"Ogün", u"Oguz", u"Oguzhan", u"Okan",
	u"Okay", u"Oktay", u"Öktem", u"Okur", u"Olcan",
	u"Olcayto", u"Omar", u"Önder", u"Onur", u"Orhan",
	u"Orkut", u"Osman", u"Özalp", u"Özcan", u"Özdemir",
	u"Özden", u"Özen", u"Özer", u"Özhan", u"Özkan", u"Özker",
	u"Öztürk", u"Polat", u"Kasim", u"Raci", u"Ragip",
	u"Rahman", u"Rahmi", u"Rajaei", u"Ramazan", u"Rasim",
	u"Rasit", u"Rasul", u"Recep", u"Remzi", u"Resat",
	u"Resid", u"Reza", u"Ridvan", u"Rifat", u"Rizvan",
	u"Ruhi", u"Rüstem", u"Rüstü", u"Saadallah",
	u"Sabahattin", u"Sabri", u"Sadettin", u"Sadik",
	u"Saffet", u"Sahan", u"Sahin", u"Sait", u"Sakir",
	u"Saleh", u"Salim", u"Salman", u"Samet", u"Sancak",
	u"Savas", u"Sedat", u"Sefa", u"Seker", u"Selahattin",
	u"Selçuk", u"Semih", u"Sener", u"Senol", u"Sercan",
	u"Serdal", u"Serdar", u"Seref", u"Serhan", u"Serhat",
	u"Serif", u"Serkan", u"Sertan", u"Sevket", u"Sevki",
	u"Sezer", u"Sezgin", u"Sidqi", u"Sinan", u"Sinasi",
	u"Soner", u"Suat", u"Suhail", u"Sükrü", u"Suleiman",
	u"Sultan", u"Sümer", u"Sunay", u"Taha", u"Taher",
	u"Tahsin", u"Talat", u"Taner", u"Tanju", u"Tansel",
	u"Tardu", u"Tariq", u"Tarkan", u"Tayfun", u"Tayfur",
	u"Taylan", u"Tayyar", u"Tayyip", u"Tekin", u"Temel",
	u"Teoman", u"Tevfik", u"Tezcan", u"Timur", u"Togan",
	u"Tolga", u"Tolgahan", u"Tolgay", u"Tonguç", u"Tosun",
	u"Tufan", u"Tugay", u"Tümer", u"Tuna", u"Tunç",
	u"Tuncay", u"Tuncel", u"Turan", u"Turgay", u"Turgut",
	u"Turhan", u"Türker", u"Türkyilmaz", u"Ugur", u"Ulvi",
	u"Ümit", u"Umran", u"Ünal", u"Üner", u"Üzeyir", u"Vahap",
	u"Vahid", u"Vedat", u"Vehbi", u"Veli", u"Veysel",
	u"Volkan", u"Vural", u"Vael", u"Vajdi", u"Yagiz",
	u"Yahya", u"Yakup", u"Yalçin", u"Yalim", u"Yanki",
	u"Yasar", u"Yasin", u"Yasser", u"Yavuz", u"Yazar",
	u"Yekta", u"Yenal", u"Yener", u"Yigit", u"Yildiray",
	u"Yildirim", u"Yildiz", u"Yilmaz", u"Yücel", u"Yüksel",
	u"Yunus", u"Yusuf", u"Zafer", u"Zainal Abidin",
	u"Zakariya", u"Zeeshan", u"Zeki", u"Zeynel", u"Zihni",
	u"Ziya", u"Zülfü"
	]

F_FIRST_OTTOMAN = [
	u"Abiha", u"Adile", u"Afet", u"A'isha", u"Ajla",
	u"Akgül", u"Alev", u"Aliye", u"Altan", u"Arzu", u"Asena",
	u"Asli", u"Aslihan", u"Aybike", u"Aybüke", u"Ayça",
	u"Ayda", u"Aydan", u"Ayfer", u"Aygül", u"Ayla", u"Aylin",
	u"Aynur", u"Aysegül", u"Aysel", u"Aysenur", u"Aysu",
	u"Aysun", u"Ayten", u"Azra", u"Bahar", u"Banu", u"Basak",
	u"Begum", u"Belkis", u"Bengi", u"Bengü", u"Beren",
	u"Betül", u"Bike", u"Birgül", u"Birsen", u"Büke",
	u"Burçak", u"Burcu", u"Çagla", u"Canan", u"Cansever",
	u"Cansu", u"Cemre", u"Ceren", u"Ceyda", u"Çigdem",
	u"Damla", u"Demet", u"Dicle", u"Didem", u"Dilara",
	u"Dilek", u"Ebru", u"Ece", u"Ecem", u"Ekin", u"Elif",
	u"Emel", u"Emine", u"Erendiz", u"Esma", u"Esra",
	u"Evrim", u"Eylem", u"Ezel", u"Fatima", u"Feryal",
	u"Fethiye", u"Fidan", u"Filiz", u"Funda", u"Gamze",
	u"Gizem", u"Gökçe", u"Gökçen", u"Göksu", u"Göksun",
	u"Gönül", u"Gözde", u"Gul", u"Gülbahar", u"Gülcan",
	u"Güler", u"Gülsah", u"Gülsen", u"Günes", u"Günseli",
	u"Haleh", u"Halide", u"Handan", u"Hande", u"Hanife",
	u"Harika", u"Hatice", u"Hatun", u"Havva", u"Hayrünnisa",
	u"Hazal", u"Hülya", u"Idil", u"Ilgin", u"Ipek", u"Irem",
	u"Irmak", u"Isenbike", u"Isil", u"Isin", u"Izel",
	u"Jale", u"Jara", u"Kadriye", u"Konca", u"Kubra",
	u"Lamia", u"Lara", u"Latife", u"Leila", u"Mehtap",
	u"Melek", u"Melike", u"Melis", u"Meltem", u"Meral",
	u"Merve", u"Meryem", u"Muazzez", u"Müjde", u"Mukerrem",
	u"Nadia", u"Nagehan", u"Nalan", u"Nariman", u"Nasrin",
	u"Nazan", u"Nazli", u"Nebahat", u"Necla", u"Nese",
	u"Neslihan", u"Nevin", u"Nezihe", u"Nihal", u"Nihan",
	u"Nilay", u"Nilüfer", u"Nuray", u"Oya", u"Oylum",
	u"Özge", u"Özgü", u"Özgül", u"Özlem", u"Pelin",
	u"Pervin", u"Pinar", u"Rabia", u"Reyhan", u"Sabiha",
	u"Safiye", u"Sanaz", u"Sanem", u"Saziye", u"Sebnem",
	u"Selda", u"Selma", u"Semiha", u"Semra", u"Senay",
	u"Serap", u"Sermin", u"Serpil", u"Sevgi", u"Sevil",
	u"Sevim", u"Sevin", u"Sevinç", u"Seyran", u"Sezen",
	u"Shanzay", u"Sibel", u"Sila", u"Sinem", u"Sirin",
	u"Songül", u"Sükran", u"Sule", u"Sumru", u"Suna",
	u"Süyümbike", u"Tomris", u"Tuba", u"Tugçe", u"Tülay",
	u"Tülin", u"Yaprak", u"Yasmin", u"Yelda", u"Yeliz",
	u"Yesim", u"Yildiz", u"Yonca", u"Zeeshan", u"Zekiye",
	u"Zerrin", u"Zeynep", u"Zuhal"
	]

OTTOMAN_SURNAMES = [
	u"Abaci", u"Abay", u"Abdil", u"Acar", u"Açik", u"Adanir",
	u"Adem", u"Adin", u"Adivar", u"Aga", u"Agaoglu", u"Agca",
	u"Agçay", u"Ahmad", u"Ak", u"Akagündüz", u"Akalin",
	u"Akan", u"Akar", u"Akarsu", u"Akbaba", u"Akbas",
	u"Akbay", u"Akbulut", u"Akburç", u"Akça", u"Akçam",
	u"Akçatepe", u"Akdag", u"Akdari", u"Akdemir", u"Akdeniz",
	u"Akgül", u"Akgün", u"Akin", u"Akinci", u"Akkas",
	u"Akkaya", u"Akkoyun", u"Akman", u"Akpinar", u"Aksit",
	u"Aksoy", u"Aksu", u"Aktas", u"Aktuna", u"Akyol",
	u"Akyürek", u"Akyüz", u"Alabora", u"Aladag", u"Albayrak",
	u"Aldemir", u"Ali", u"Alkan", u"Alpay", u"Alptekin",
	u"Altan", u"Altin", u"Altintop", u"Altintas", u"Altug",
	u"Altun", u"Apak", u"Arat", u"Arica", u"Arikan",
	u"Armagan", u"Arman", u"Arslan", u"Asani", u"Asena",
	u"Asik", u"Aslan", u"Ata", u"Atakan", u"Atalar",
	u"Atalay", u"Ataman", u"Atan", u"Ataseven", u"Atay",
	u"Ates", u"Avci", u"Avni", u"Ayda", u"Aydan", u"Aydemir",
	u"Aydin", u"Aydinlar", u"Aydogan", u"Aydogdu", u"Aygün",
	u"Ayhan", u"Ayik", u"Aykaç", u"Akyildiz", u"Aykut",
	u"Ayral", u"Ayranci", u"Aytaç", u"Ayvaz", u"Baba",
	u"Babacan", u"Babaoglu", u"Bagci", u"Bahadir", u"Bakkal",
	u"Balbay", u"Balcan", u"Balci", u"Balkan", u"Bardakçi",
	u"Basak", u"Basar", u"Basaran", u"Baser", u"Bastürk",
	u"Batuk", u"Batur", u"Bayar", u"Bayat", u"Baybasin",
	u"Baydar", u"Bayindir", u"Baykara", u"Bayrak",
	u"Bayraktar", u"Bayram", u"Bayramoglu", u"Behçet",
	u"Benli", u"Bereket", u"Berk", u"Berker", u"Bilge",
	u"Bilgi", u"Bilgili", u"Bilgin", u"Bilici", u"Birdal",
	u"Birkan", u"Birol", u"Birsen", u"Bolat", u"Bölükbasi",
	u"Bora", u"Boran", u"Boz", u"Bozdag", u"Bozer",
	u"Bozgüney", u"Bozkurt", u"Boztepe", u"Bucak", u"Budak",
	u"Bugra", u"Büker", u"Buldan", u"Bulut", u"Buruk",
	u"Büyük", u"Çagatay", u"Çaglar", u"Çaglayan", u"Çagri",
	u"Çakir", u"Çakmak", u"Çalhanoglu", u"Çalik", u"Çalis",
	u"Can", u"Candan", u"Candemir", u"Caner", u"Çatli",
	u"Çavdarli", u"Cavus", u"Celal", u"Çelebi", u"Çelik",
	u"Cerci", u"Ceren", u"Çetin", u"Çetinkaya", u"Cevahir",
	u"Cevdet", u"Çevik", u"Ceylan", u"Çiçek", u"Çiftçi",
	u"Cigerci", u"Cihan", u"Çimen", u"Çinar", u"Çoban",
	u"Çolak", u"Çorlu", u"Coskun", u"Çubukçu", u"Cumali",
	u"Dagdelen", u"Dagtekin", u"Dal", u"Dalkiliç", u"Dalman",
	u"Dede", u"Deliktas", u"Demir", u"Demirbas", u"Demirci",
	u"Demirel", u"Demirkan", u"Demirören", u"Demirtas",
	u"Deniz", u"Denizli", u"Denkel", u"Denktas", u"Dereli",
	u"Derici", u"Dervis", u"Dicle", u"Dikmen", u"Dilaver",
	u"Dinç", u"Dinçer", u"Dink", u"Diyadin", u"Dogan",
	u"Dogançay", u"Dogu", u"Doruk", u"Duman", u"Durak",
	u"Durmaz", u"Dursun", u"Ece", u"Ecevit", u"Efendi",
	u"Egemen", u"Ekici", u"Ekinci", u"Ekren", u"Eksi",
	u"Elmas", u"Emin", u"Emre", u"Engin", u"Enver",
	u"Erbakan", u"Erbil", u"Ercan", u"Erçetin", u"Erdal",
	u"Erdem", u"Erdemir", u"Erden", u"Erdinç", u"Erdogan",
	u"Erem", u"Eren", u"Ergen", u"Ergin", u"Ergün", u"Erim",
	u"Eris", u"Erkan", u"Erkin", u"Erkoç", u"Eroglu",
	u"Erol", u"Ersin", u"Ersoy", u"Ersöz", u"Ertegün",
	u"Ertug", u"Ertugrul", u"Eser", u"Eyüboglu", u"Fahri",
	u"Farhi", u"Firat", u"Fisek", u"Fraserli", u"Genç",
	u"Giray", u"Gökay", u"Gökbakar", u"Gökçe", u"Gökçek",
	u"Gökçen", u"Gökdemir", u"Gökmen", u"Göllü", u"Gönül",
	u"Görgülü", u"Gözübüyük", u"Güçer", u"Güçlü", u"Gul",
	u"Gulden", u"Gülek", u"Gulen", u"Güler", u"Gülpinar",
	u"Gültekin", u"Gün", u"Günay", u"Günaydin", u"Gündogan",
	u"Gündogdu", u"Gündüz", u"Günes", u"Güney", u"Güngör",
	u"Gür", u"Gürsel", u"Gürses", u"Gürsu", u"Güven",
	u"Güvenç", u"Hacioglu", u"Halefoglu", u"Hamdi",
	u"Hamzaoglu", u"Hanim", u"Hasim", u"Hayrettin",
	u"Hazinedar", u"Hekimoglu", u"Heper", u"Hikmet", u"Hoca",
	u"Hulusi", u"Hussein", u"Ilgaz", u"Ilhan", u"Ilkin",
	u"Inal", u"Inan", u"Inanç", u"Ince", u"Incesu", u"Inci",
	u"Inönü", u"Ipekçi", u"Irmak", u"Iscan", u"Isik",
	u"Isler", u"Izzet", u"Jamakovic", u"Kaan", u"Kaba",
	u"Kahraman", u"Kahveci", u"Kahya", u"Kaldirim",
	u"Kalkan", u"Kaner", u"Kaptan", u"Karabulut", u"Karaca",
	u"Karacan", u"Karadag", u"Karadeniz", u"Karadere",
	u"Karaduman", u"Karagöz", u"Karahan", u"Karakas",
	u"Karakaya", u"Karakoç", u"Karakus", u"Karaman",
	u"Karasu", u"Karatay", u"Kartal", u"Kas", u"Kavak",
	u"Kavur", u"Kaya", u"Kayhan", u"Kaymak", u"Kaynarca",
	u"Kayyali", u"Kekilli", u"Keles", u"Kemal", u"Kent",
	u"Kerimoglu", u"Keser", u"Keskin", u"Kiliç", u"Kiliçli",
	u"Kimyacioglu", u"Kinali", u"Kiraç", u"Kiraz", u"Kirdar",
	u"Kivanç", u"Kizil", u"Kizilirmak", u"Kizilkaya",
	u"Kobal", u"Koç", u"Koca", u"Koçak", u"Kocaman",
	u"Koçer", u"Koçoglu", u"Koçyigit", u"Köksal", u"Konca",
	u"Köprülü", u"Koray", u"Korkmaz", u"Korkut", u"Köse",
	u"Koyuncu", u"Koz", u"Közen", u"Kubat", u"Kubilay",
	u"Kunt", u"Kunter", u"Kurt", u"Kurtar", u"Kurtoglu",
	u"Kurtulus", u"Kus", u"Kut", u"Kutay", u"Kutlu",
	u"Levni", u"Mardin", u"Mehmed", u"Memis", u"Mencik",
	u"Menderes", u"Meric", u"Metin", u"Muhiddin", u"Muhtar",
	u"Müjde", u"Mumcu", u"Mungan", u"Mustafa", u"Mutlu",
	u"Nabi", u"Nadi", u"Nalband", u"Nalci", u"Namli", u"Nas",
	u"Nazif", u"Nazli", u"Nazmi", u"Necmi", u"Neyzi",
	u"Niazi", u"Noor", u"Ocak", u"Öcal", u"Öçal", u"Öcalan",
	u"Odabasi", u"Oguz", u"Okay", u"Öktem", u"Okur",
	u"Okyar", u"Okyay", u"Olgun", u"Ölmez", u"Önal",
	u"Onaral", u"Onarici", u"Onay", u"Öncel", u"Önder",
	u"Onut", u"Orbay", u"Örnek", u"Osman", u"Öz", u"Oz",
	u"Özal", u"Özbek", u"Özbey", u"Özbilen", u"Özbilgin",
	u"Özcan", u"Özçelik", u"Özdemir", u"Özden", u"Özek",
	u"Özel", u"Özen", u"Özer", u"Özgen", u"Özgür", u"Özhan",
	u"Özkan", u"Özker", u"Özkök", u"Özkul", u"Özmen",
	u"Özmert", u"Özoguz", u"Özsoy", u"Öztoprak", u"Öztürk",
	u"Pamuk", u"Parlak", u"Pasa", u"Peker", u"Poçan",
	u"Polat", u"Poyraz", u"Remzi", u"Renda", u"Reza",
	u"Saatchi", u"Sabanci", u"Sabri", u"Saçan", u"Sadak",
	u"Safak", u"Saglam", u"Saglik", u"Sahan", u"Sahin",
	u"Saka", u"Sakir", u"Saltik", u"Samdereli", u"Samet",
	u"Sancak", u"Sancakli", u"Sançar", u"Sanli", u"Sari",
	u"Sarica", u"Sarigül", u"Sarikaya", u"Sarp", u"Sarper",
	u"Sasmaz", u"Savas", u"Saygi", u"Sayin", u"Saylan",
	u"Seker", u"Selçuk", u"Selen", u"Sen", u"Sener",
	u"Sengül", u"Sensoy", u"Sentürk", u"Serif", u"Sevgi",
	u"Sevim", u"Seyfi", u"Sezen", u"Sezer", u"Sezgin",
	u"Simsek", u"Sipal", u"Sirin", u"Sisli", u"Sofuoglu",
	u"Sökmen", u"Sokullu", u"Solak", u"Sönmez", u"Soysal",
	u"Sözen", u"Sporel", u"Süleymanoglu", u"Sümer", u"Sunay",
	u"Sunter", u"Suvari", u"Taher", u"Talay", u"Tandogan",
	u"Taner", u"Tansel", u"Tanyu", u"Tarhan", u"Tas",
	u"Tasçi", u"Tasdemir", u"Taskiran", u"Tayfur", u"Taylan",
	u"Tekeli", u"Tekin", u"Terzi", u"Terzioglu", u"Tezcan",
	u"Tiryaki", u"Togan", u"Togay", u"Toker", u"Toner",
	u"Topal", u"Topaloglu", u"Topbas", u"Topçu", u"Toprak",
	u"Topuz", u"Toraman", u"Torun", u"Tosun", u"Tufan",
	u"Tüfekçi", u"Tümer", u"Tuna", u"Tunç", u"Tuncel",
	u"Tuncer", u"Turan", u"Türel", u"Turgut", u"Turk",
	u"Türkay", u"Türker", u"Türkoglu", u"Türkyilmaz",
	u"Tüzmen", u"Tüzün", u"Uçar", u"Üçüncü", u"Ugurlu",
	u"Ulusoy", u"Ünal", u"Üner", u"Ünsal", u"Usak", u"Uslu",
	u"Uyanik", u"Uygun", u"Uygur", u"Uysal", u"Uzer",
	u"Üzümcü", u"Uzunlar", u"Vardar", u"Veli", u"Volkan",
	u"Vural", u"Yagci", u"Yagcilar", u"Yagmur", u"Yakin",
	u"Yakut", u"Yalaz", u"Yalçin", u"Yalçinkaya", u"Yalman",
	u"Yanki", u"Yasar", u"Yasin", u"Yavas", u"Yavuz",
	u"Yazar", u"Yazici", u"Yenal", u"Yener", u"Yerli",
	u"Yerlikaya", u"Yesil", u"Yesilnil", u"Yetis", u"Yigit",
	u"Yildirim", u"Yildiz", u"Yildizeli", u"Yildizoglu",
	u"Yilmaz", u"Yüce", u"Yücel", u"Yüksel", u"Yumlu",
	u"Zaim", u"Zaimoglu", u"Zarakolu", u"Zengin", u"Zeybek",
	u"Zorlu"
	]

GENERATOR_OTTOMAN = Generator(M_FIRST_OTTOMAN, F_FIRST_OTTOMAN,
							  M_FIRST_OTTOMAN,
							  F_FIRST_OTTOMAN+OTTOMAN_SURNAMES,
							  OTTOMAN_SURNAMES)

M_FIRST_PERSIAN = [
	u"Abbas", u"Abd al-Aziz", u"Abd al-Rahman", u"Abdolreza",
	u"Abdul Ali", u"Abdul Hamid", u"Abdul Hussein",
	u"Abdul Karim", u"Abdul Majid", u"Abdul Malik",
	u"Abdul Qadir", u"Abdul Wahhab", u"Abdullah", u"Adib",
	u"Afshin", u"Aftab", u"Ahmad", u"Aladdin", u"Ali",
	u"Ali Reza", u"Amir", u"Arash", u"Armin", u"Arya",
	u"Asadullah", u"Ashk", u"Aydın", u"Babak", u"Bahram",
	u"Bardiya", u"Behnam", u"Behrouz", u"Bobak", u"Buksh",
	u"Danish", u"Dariush", u"Dhikrullah", u"Dilawar",
	u"Esfandiar", u"Farbod", u"Farhad", u"Fariborz",
	u"Farid", u"Farzan", u"Freydun", u"Ghasem", u"Habib",
	u"Hamid", u"Hashem", u"Hassan", u"Haydar", u"Heydar",
	u"Homayoun", u"Hushang", u"Hussein", u"Ibrahim",
	u"Ihsan", u"Inayat", u"Irad", u"Iraj", u"Irfan",
	u"Iskandar", u"Ismail", u"Jahan", u"Jahangir",
	u"Jamshid", u"Jan", u"Jawad", u"Jawed", u"Kamran",
	u"Kaveh", u"Kayvan", u"Kazem", u"Khorshid", u"Khosrow",
	u"Kourosh", u"Manuchehr", u"Masoud", u"Maytham",
	u"Mehdi", u"Mehrdad", u"Mohammad-Reza", u"Moin",
	u"Mojtaba", u"Muhammad", u"Muharrem", u"Muhsin",
	u"Mumtaz", u"Murad", u"Murtaza", u"Muslim", u"Mustafa",
	u"Nariman", u"Nasrallah", u"Navid", u"Nazim", u"Nima",
	u"Omar", u"Omid", u"Parviz", u"Pejman", u"Peyman",
	u"Pourang", u"Pouria", u"Radney", u"Rahman", u"Ramin",
	u"Rashid", u"Rasul", u"Reza", u"Rostam", u"Ruhullah",
	u"Sa'id", u"Salar", u"Samir", u"Shahriyar", u"Shahrokh",
	u"Shahzad", u"Shapur", u"Siavash", u"Suleiman",
	u"Surena", u"Vahid", u"Vardan", u"Zeeshan", u"Zubin"
	]

F_FIRST_PERSIAN = [
	u"Alina", u"Anahita", u"Anousheh", u"Arezu", u"Arian",
	u"Ariana", u"Ashraf", u"Astar", u"Atoosa", u"Atusa",
	u"Azadeh", u"Azar", u"Bahar", u"Baharak ", u"Banu",
	u"Bita", u"Daria", u"Dilara", u"Donya", u"Farah",
	u"Farangis", u"Fariba", u"Farnaz", u"Farzaneh",
	u"Fatemeh", u"Fatima", u"Fereshteh", u"Feryal", u"Frida",
	u"Goli", u"Gordafarid", u"Gurandukht", u"Haleh", u"Hana",
	u"Hayat", u"Jahan Ara", u"Jale", u"Jaleh", u"Jamileh",
	u"Katayoun", u"Khorshid", u"Kiana", u"Kira", u"Laleh",
	u"Leila", u"Mahd-i Ulya", u"Mahnoosh", u"Mahshid",
	u"Mahtab", u"Mandana", u"Maryam", u"Marzieh",
	u"Mehregan", u"Mina", u"Mithra", u"Mojugan", u"Mozhgan",
	u"Nadia", u"Nagisa", u"Nargess", u"Nasrin", u"Nazanin",
	u"Negar", u"Negin", u"Nika", u"Niloufar", u"Nina",
	u"Parastu", u"Pardis", u"Parisa", u"Parvin", u"Payvand",
	u"Reyhan", u"Roksaneh", u"Roshanak", u"Roxana", u"Roya",
	u"Rudaba", u"Sahar", u"Salma", u"Samira", u"Sanaz",
	u"Sara", u"Sareh", u"Sepideh", u"Setareh", u"Shai",
	u"Shantia", u"Shanzay", u"Sherine", u"Shirin",
	u"Shohreh", u"Sima", u"Simin", u"Sindukht", u"Soheila",
	u"Soraya", u"Susan", u"Tahmina", u"Tahmineh", u"Tala",
	u"Tannaz", u"Tara", u"Taraneh", u"Tarsa", u"Wafaa",
	u"Yasamin", u"Yasmin", u"Zarine", u"Zaynab", u"Zhila",
	u"Zivar", u"Zohreh"
	]

PERSIAN_SURNAMES = [
	u"Abdullahi", u"Abedini", u"Ahadi", u"Ahmadi", u"Akbari",
	u"Akhtar", u"Alizadeh", u"Arbab", u"Asadi",
	u"Astarabadi", u"Balkhi", u"Banai", u"Banu Hashim",
	u"Baraghani", u"Behzadi", u"Bukhari", u"Darvish",
	u"Ebrahimi", u"Eftekhari", u"Esfahani", u"Fanaei",
	u"Farahani", u"Farsi", u"Farzan", u"Fikri",
	u"Gharabaghi", u"Ghasemi", u"Ghaznavi", u"Ghorbani",
	u"Ghoreishi", u"Gilani", u"Golshiri", u"Gul",
	u"Haghighi", u"Hamadani", u"Hamidi", u"Heidari",
	u"Hijazi", u"Husseini", u"Ipekçi", u"Iravani",
	u"Jahanbani", u"Jalili", u"Jamshidi", u"Javadi",
	u"Kadivar", u"Kamali", u"Karimi", u"Kazmi", u"Khadem",
	u"Khalaji", u"Khansari", u"Khatibi", u"Khomeini",
	u"Khonsari", u"Khorsandi", u"Kirmani", u"Mahdavi",
	u"Mahmoudi", u"Mahmoudieh", u"Majidi", u"Makhmalbaf",
	u"Mazanderani", u"Mirzaei", u"Mokri", u"Nabavi",
	u"Naceri", u"Nafisi", u"Najafi", u"Nalbandian", u"Nalci",
	u"Namazi", u"Namdar", u"Namjoo", u"Nariman", u"Nazari",
	u"Norouzi", u"Pahlavi", u"Paria", u"Pashaei", u"Pejman",
	u"Qazwini", u"Rahimi", u"Rahmani", u"Rajaei",
	u"Ramezani", u"Rashidi", u"Rouhani", u"Saatchi",
	u"Sadeghi", u"Safavi", u"Salehi", u"Salemi", u"Semnani",
	u"Shahabi", u"Shahbazi", u"Shahidi", u"Shahzad",
	u"Sharifi", u"Shirazi", u"Shojaei", u"Soomekh",
	u"Soroush", u"Tabatabaei", u"Taghavi", u"Talebi",
	u"Tirmizi", u"Tousi", u"Veisi", u"Yazdani", u"Yazdi",
	u"Yousefi", u"Zadeh", u"Zandi"
	]

GENERATOR_PERSIAN = Generator(M_FIRST_PERSIAN, F_FIRST_PERSIAN, M_FIRST_PERSIAN, F_FIRST_PERSIAN, PERSIAN_SURNAMES)

M_FIRST_PORTUGUESE = [
	u"Aarão", u"Abel", u"Abelardo", u"Abraão", u"Adalberto", u"Adão",
	u"Adelino", u"Ademar", u"Adilmar", u"Adolfo", u"Adriano",
	u"Afonso", u"Agostinho", u"Aguinaldo", u"Alarico", u"Alberto",
	u"Aldo", u"Aleixandre", u"Aleixo", u"Alexandre", u"Alfonso",
	u"Alfredo", u"Alírio", u"Aloísio", u"Álvaro", u"Amadeu",
	u"Américo", u"Amílcar", u"André", u"Ângelo", u"Aníbal", u"Antão",
	u"Antero", u"António", u"Antônio", u"Armando", u"Arnaldo",
	u"Artur", u"Augusto", u"Aurélio", u"Balduíno", u"Baltasar",
	u"Baltazar", u"Barnabé", u"Bartolomeu", u"Belarmino", u"Belmiro",
	u"Benedito", u"Bento", u"Bernardo", u"Bernardim", u"Bernardino",
	u"Boaventura", u"Bráulio", u"Breno", u"Brites", u"Bruno",
	u"Caetano", u"Caim", u"Caio", u"Calisto", u"Camilo", u"Cândido",
	u"Carlos", u"Casimiro", u"Cássio", u"Cecilio", u"César",
	u"Cláudio", u"Clemente", u"Conrado", u"Constantino", u"Cristiano",
	u"Cristóvão", u"Damião", u"Daniel", u"Danilo", u"David", u"Davi",
	u"Diego", u"Diogo", u"Dionísio", u"Dinis", u"Dirce", u"Dirceu",
	u"Domingos", u"Donato", u"Duarte", u"Edelberto", u"Edgar",
	u"Edmundo", u"Eduardo", u"Elias", u"Eliseu", u"Emanuel",
	u"Emílio", u"Epaminondas", u"Érico", u"Ernesto", u"Estanislau",
	u"Estêvão", u"Eugénio", u"Eugênio", u"Eurico", u"Eusébio",
	u"Evandro", u"Evaristo", u"Everaldo", u"Ezequiel", u"Fabiano",
	u"Fábio", u"Fabrício", u"Faustino", u"Fausto", u"Feliciano",
	u"Felício", u"Felipe", u"Félix", u"Fernando", u"Fernão",
	u"Filipe", u"Firmino", u"Flávio", u"Flor", u"Florêncio",
	u"Floriano", u"Florípes", u"Fradique", u"Francisco", u"Frederico",
	u"Gabriel", u"Gaspar", u"Gastão", u"Gaudêncio", u"George",
	u"Georgio", u"Geraldo", u"Gerard", u"Germano", u"GianFrancesco",
	u"GianLuca", u"Gil", u"Gilberto", u"Giorgio", u"Gonçalo",
	u"Graciano", u"Graciliano", u"Gregório", u"Guido", u"Guilherme",
	u"Guiomar", u"Gustavo", u"Heitor", u"Hélio", u"Hélder",
	u"Henrique", u"Herculano", u"Hermínio", u"Hermenegildo",
	u"Higino", u"Hilário", u"Hipólito", u"Honório", u"Horácio",
	u"Hugo", u"Humberto", u"Inácio", u"Ivo", u"Jacinto", u"Jaime",
	u"Jean", u"Jeremias", u"João", u"Joaquim", u"Joel", u"Jonas",
	u"Jorge", u"José", u"Júlio", u"Juliano", u"Justino", u"Juvenal",
	u"Lauro", u"Laurus", u"Lázaro", u"Leandro", u"Leonardo",
	u"Leonel", u"Leopoldo", u"Lineu", u"Lino", u"Lourenço", u"Lucas",
	u"Lúcio", u"Luciano", u"Ludovico", u"Luís", u"Luiz", u"Manuel",
	u"Manoel", u"Marco", u"Marcos", u"Marcelino", u"Marcelo",
	u"Mário", u"Martim", u"Martinho", u"Mateus", u"Matheus",
	u"Matias", u"Maurício", u"Maurílio", u"Mauro", u"Máximo",
	u"Maximiliano", u"Mécia", u"Mendo", u"Miguel", u"Murilo",
	u"Narciso", u"Natalino", u"Nelson", u"Nestor", u"Nicolau",
	u"Norberto", u"Nuno", u"Octávio", u"Otávio", u"Odílio", u"Olavo",
	u"Olegário", u"Olímpio", u"Olívio", u"Onofre", u"Orestes",
	u"Orlando", u"Óscar", u"Oscar", u"Osório", u"Otelo", u"Ovídio",
	u"Palmiro", u"Pascoal", u"Patrício", u"Paulino", u"Paulo",
	u"Pedro", u"Petronio", u"Plácido", u"Plínio", u"Políbio",
	u"Prazeres", u"Prímio", u"Querubim", u"Quintiliano", u"Quirino",
	u"Quitério", u"Rafael", u"Ramiro", u"Raimundo", u"Raul",
	u"Reginaldo", u"Reinaldo", u"Renato", u"Ricardo", u"Rivelino",
	u"Roberto", u"Rodolfo", u"Rodrigo", u"Rogério", u"Romão",
	u"Romeu", u"Rómulo", u"Rômulo", u"Ronaldo", u"Roque", u"Rúben",
	u"Rúbem", u"Rui", u"Salomão", u"Salvador", u"Samuel", u"Sancho",
	u"Sandoval", u"Sandro", u"Sebastião", u"Serafim", u"Sérgio",
	u"Severino", u"Silvano", u"Silvério", u"Sílvio", u"Silvino",
	u"Simão", u"Simeão", u"Solano", u"Tadeu", u"Telmo", u"Teobaldo",
	u"Teodoro", u"Tiago", u"Thiago", u"", u"Timóteo", u"Tobias",
	u"Tomás", u"Thomaz", u"Trajano", u"Ubaldo", u"Ulisses",
	u"Umbelino", u"Urbano", u"Valentim", u"Valério", u"Vasco",
	u"Venâncio", u"Ventura", u"Vicente", u"Victor", u"Vinicius",
	u"Violante", u"Virgílio", u"Viriato", u"Vítor", u"Xavier",
	u"Xisto", u"Zacarias"
	]

F_FIRST_PORTUGUESE = [
	u"Adelaide", u"Adélia", u"Adelina", u"Adriana", u"Ágata",
	u"Alberta", u"Alda", u"Aldina", u"Alexandra", u"Alice", u"Alzira",
	u"Amália", u"Amanda", u"Amélia", u"Ana", u"Andreia", u"Andréia",
	"Ângela", u"Angélica", u"Angelina", u"Anita", u"Antónia",
	u"Antônia", "", "Ava", u"Augusta", u"Augustina", u"Aurélia",
	u"Aurora", u"Bárbara", u"Beatriz", u"Belarmina", u"Belém",
	u"Benedita", u"Berengária", u"Bernardete", "Bernarda",
	u"Bernardina", u"Branca", u"Brígida", u"Brízida", u"Bruna",
	u"Caetana", u"Camila", u"Cândida", u"Capitolina", u"Carina",
	u"Carla", u"Carlota", u"Carmen", u"Carmem", "Carolina",
	u"Catarina", u"Cássia", u"Cátia", u"Cecília", u"Celeste",
	u"Célia", u"Celina", u"Cesária", u"Cidália", u"Clara", u"Cláudia",
	"Clementina", u"Clotilde", u"Conceição", u"Constança",
	u"Constantina", u"Corina", u"Cristiana", u"Cristina", u"Custódia",
	u"Daniela", u"Débora", u"Denilde", u"Denise", u"Diana", "Dina",
	u"Diná", u"Donata", u"Doroteia", u"Dorotéia", "Edite", u"Edna",
	u"Eduarda", u"Elia", u"Elisa", u"Elisabete", u"Elizabete",
	u"Elsa", u"Elvira", u"Elza", "Ema", u"Emerenciana", u"Emília",
	u"Epifânia", u"Érica", u"Ermelinda", u"Esmeralda", u"Estefânia",
	u"Estela", u"Estrela", u"Eugénia", u"Eugênia", "Eulália",
	u"Eunice", u"Eva", u"Fábia", u"Fabiana", u"Fátima", u"Fausta",
	u"Faustina", u"Felícia", u"Feliciana", u"Felismina", u"Fernanda",
	u"Fernandina", u"Filipa", "Filomena", u"Firmina", u"Flávia",
	u"Flora", u"Florbela", u"Florência", u"Florinda", u"Florípes",
	u"Francisca", u"Frederica", u"Gabriela", u"Genoveva",
	u"Georgette", u"Georgina", u"Geraldina", u"Germana", u"Gertrudes",
	"Gisela", u"Giselda", u"Gisele", u"Glória", u"Graça",
	u"Guilhermina", u"Helena", u"Hélia", u"Heloísa", "Henriqueta",
	u"Hermínia", u"Honorina", u"Inês", u"Inácia", u"Iolanda",
	u"Irene", u"Irina", u"Isabel", "Isaura", u"Isilda", u"Isulina",
	u"Iva", u"Ivete", u"Ivone", u"Jacinta", u"Janete", u"Joana",
	u"Joaquina", u"Jorgina", u"Josefa", u"Josefina", "Judite",
	u"Júlia", u"Juliana", u"Julieta", u"Justina", u"Juvina", u"Laila",
	u"Lara", u"Laura", u"Laurea", u"Laurel", u"Lauren", u"Laureana",
	u"Laurinda", u"Leandra", u"Leila", u"Leonor", u"Leonilde",
	u"Leopoldina", "Letícia", u"Lídia", u"Lígia", u"Lila", u"Lília",
	u"Lilian", u"Liliane", u"Lilih", u"Lívia", u"Liana", u"Liliana",
	u"Lina", u"Lourdes", "Lúcia", u"Luciana", u"Lucinda", u"Lucrécia",
	u"Ludovica", u"Ludovina", u"Luisa", u"Luiza", "Lurdes", u"Luzia",
	u"Luz", u"Madalena", u"Mafalda", u"Magali", u"Magda", u"Manuela",
	u"Manoela", "Márcia", u"Marcela", u"Marcelina", u"Margarida",
	"Maria", u"Maria Joãou", "Maria Joséu", "Mariana", u"Mariane",
	u"Marilda", u"Marília", u"Marina", u"Marisa", u"Marise", u"Marta",
	u"Maurícia", u"Máxima", u"Maximiliana", "Mercedes", u"Merciana",
	u"Micaela", u"Milene", u"Miquelina", u"Miriam", u"Mónica",
	u"Mônica", "Nádia", u"Natália", u"Natalina", "Natividade",
	u"Nicole", u"Octávia", u"Otávia", "Odete", u"Odília", "Olga",
	u"Olímpia", u"Olívia", u"Otília", u"Palmira", u"Pandora",
	u"Patrícia", u"Paula", u"Paulina", "Penélope", u"Piedade",
	u"Prantelhana", u"Priscila", u"Querubina", u"Quintiliana",
	"Quirina", u"Quitéria", u"Rafaela", u"Ramira", u"Raimunda",
	u"Raquel", u"Rebeca", u"Regina", u"Renata", u"Ricardina", u"Rita",
	"Roberta", u"Rosa", u"Rosália", u"Rosalina", u"Rosalinda",
	u"Rosana", u"Rosaura", u"Rute", u"Sabrina", u"Salomé", u"Sancha",
	"Sandra", u"Sara", u"Sebastiana", u"Selma", u"Serafina",
	u"Silvana", u"Silvéria", "Sílvia", u"Silvina", u"Simone",
	u"Sofia", u"Solange", u"Sónia", u"Sônia", "Susana", u"Tânia",
	u"Tatiana", u"Telma", u"Teodora", "Teresa", u"Thereza", "Tomásia",
	u"Umbelina", "Úrsula", u"Valentina", u"Valéria", u"Vanda",
	u"Vanésa", u"Vera", u"Verónica", u"Verônica", "", "Violeta",
	u"Virgília", u"Virgínia", u"Vitória", u"Viviana", u"Xénia",
	"Ximena", u"Zara", u"Zélia", u"Zelinda", u"Zilá", u"Zínia",
	u"Zita", "Zoraide", u"Zuleica", u"Zuleide", u"Zulina", u"Zulmira"
	]

PORTUGUESE_SURNAMES = [
	u"Abreu", u"Agostinho", u"Águas", u"Aguiar", u"Albuquerque",
	u"Alcantara", u"Almeida", u"Álvares", u"Alves", u"Alves da Silva",
	u"Alvim", u"Amaral", u"Amorim", u"Andrade", u"Andrade",
	u"Antunes", u"Araújo", u"Assunção", u"Ávila", u"Azevedo",
	u"Bandeira", u"Baptista", u"Barbosa", u"Barreto", u"Barros",
	u"Batata", u"Batista", u"Belasco", u"Bento", u"Bento Gonçalves",
	u"Bettencourt", u"Borges", u"Botelho", u"Braga", u"Branco",
	u"Brandão", u"Brito", u"Cabral", u"Câmara", u"Campos", u"Cardoso",
	u"Carneiro", u"Carreira", u"Carvalho", u"de Castro", u"Castro",
	u"Cavaco", u"Coelho", u"Coimbra", u"Colón", u"Conceição",
	u"Cordeiro", u"Correia", u"Corte-Real", u"Cortes", u"Corvo",
	u"Costa", u"Coutinho", u"Couto", u"Cruz", u"Cunha", u"Dantas",
	u"del Rosario", u"Delgado", u"Dias", u"Espinoza", u"Faria",
	u"Fernandes", u"Ferreira", u"Fidalgo", u"Fonseca", u"Freitas",
	u"Furtado", u"Gama", u"Garnier", u"Gomes", u"Gonsalves",
	u"Gonçalves", u"Gouveia", u"Gusmão", u"Góes", u"Henriques",
	u"Hernandes", u"Leite", u"Lima", u"Lobo", u"Lopes", u"Luz",
	u"Macedo", u"Machado", u"Maciel", u"Magalhães", u"Martins",
	u"Mascarenhas", u"Mata", u"Matos", u"Medeiros", u"Melo",
	u"Mendes", u"Mendonça", u"Menezes", u"Miranda", u"Moniz",
	u"Morais", u"Moreira", u"Moreno", u"Nascimento", u"Neves",
	u"Nogueira", u"Nunes", u"Nunez", u"Oliveira", u"Pacheco",
	u"Paiva", u"Pascoal", u"Pereira", u"Pereira da Silva", u"Peres",
	u"Pinto", u"Pires", u"Queiroz", u"Rebelo", u"Rego", u"Reis",
	u"Resendes", u"Ribeiro", u"Rodrigues", u"Rosa", u"Sá",
	u"Saldanha", u"Santos", u"Seixas", u"Serra", u"Silva",
	u"Silveira", u"Silvestre", u"Siqueira", u"Soares", u"Sousa",
	u"Tavares", u"Teixeira", u"Torres", u"Varela", u"Vasconcelos",
	u"Vaz", u"Vieira", u"Vila"
	]

GENERATOR_PORTUGUESE = Generator(M_FIRST_PORTUGUESE,
								 F_FIRST_PORTUGUESE,
								 M_FIRST_PORTUGUESE+PORTUGUESE_SURNAMES,
								 F_FIRST_PORTUGUESE+PORTUGUESE_SURNAMES,
								 PORTUGUESE_SURNAMES)

M_ROMAN_PRAENOMEN = [
	"Agrippa", "Amulius", "Ancus", "Appius", "Arruns",
	"Attius", "Aulus", "Caelus", "Caeso", "Camillus",
	"Canus", "Cossus", "Decimus", "Decius", "Drusus",
	"Faustus", "Flavius", "Gaius", "Gallus", "Gnaeus",
	"Herius", "Hostus", "Lucius", "Mamercus", "Manius",
	"Marcellus", "Marcus", "Marius", "Mettius", "Minatus",
	"Minius", "Nerius", "Nonus", "Novius", "Numa",
	"Numerius", "Octavianus", "Octavius", "Olus", "Opiter",
	"Oppius", "Ovius", "Paccius", "Paullus", "Pompo",
	"Postumius", "Postumus", "Potitus", "Primus", "Proculus",
	"Publius", "Quintus", "Salvius", "Secundus", "Seppius",
	"Septimus", "Sertor", "Servius", "Sextus", "Sisenna",
	"Spurius", "Statius", "Taurus", "Tertius", "Tiberius",
	"Titus", "Trebius", "Tullus", "Vettius", "Vibius",
	"Volesus", "Vopiscus"
	]

F_ROMAN_PRAENOMEN = [
	"Appia", "Aula", "Caesula", "Decima", "Fausta", "Gaia",
	"Gnaea", "Hosta", "Lucia", "Maio", "Mamerca", "Mania",
	"Marcia", "Maxima", "Mettia", "Mino", "Nona", "Numeria",
	"Octavia", "Paulla", "Postuma", "Prima", "Procula",
	"Publia", "Quarta", "Quinta", "Secunda", "Septima",
	"Servia", "Sexta", "Spuria", "Statia", "Tertia", "Titia",
	"Tiberia", "Tulla", "Vibia", "Volusa", "Vopisca"
	]

ROMAN_NOMEN = [
	"Abronia", "Aburia", "Accia", "Accoleia", "Acerronia",
	"Acilia", "Actoria", "Acutia", "Aebutia", "Aelia",
	"Aemilia", "Afrania", "Albia", "Albinia", "Albucia",
	"Alfena", "Alfia", "Aliena", "Amafinia", "Ampia",
	"Ancharia", "Anicia", "Annaea", "Anneia", "Annia",
	"Antia", "Antistia", "Antonia", "Aponia", "Appia",
	"Appuleia", "Apronia", "Apustia", "Aquillia", "Aquinia",
	"Arellia", "Arennia", "Arpineia", "Arria", "Arruntia",
	"Articuleia", "Asconia", "Asinia", "Ateia", "Aternia",
	"Atia", "Atilia", "Atinia", "Atria", "Attia", "Aufidia",
	"Aulia", "Aurelia", "Auria", "Aurunculeia", "Autronia",
	"Aviana", "Aviena", "Avidia", "Axia", "Baebia",
	"Balventia", "Bantia", "Barbatia", "Betiliena",
	"Betucia", "Blossia", "Bruttia", "Bucculeia", "Burriena",
	"Caecia", "Caecilia", "Caecina", "Caedicia", "Caelia",
	"Caeparia", "Caepasia", "Caerellia", "Caesennia",
	"Caesetia", "Caesia", "Caesonia", "Caesulena",
	"Caetronia", "Calavia", "Calidia", "Calpurnia",
	"Calvisia", "Cania", "Canidia", "Caninia", "Cantia",
	"Cantilia", "Canuleia", "Canutia", "Carfulena",
	"Carisia", "Carpinatia", "Carteia", "Carvilia", "Cassia",
	"Castricia", "Castrinia", "Catia", "Catiena", "Catilia",
	"Ceionia", "Centenia", "Cestia", "Cicereia", "Cilnia",
	"Cincia", "Cispia", "Claudia", "Cloelia", "Cluentia",
	"Cluvia", "Cocceia", "Cominia", "Consentia", "Considia",
	"Coponia", "Corfidia", "Cornelia", "Cornificia",
	"Coruncania", "Cosconia", "Cossinia", "Cossutia",
	"Cotia", "Cottia", "Crassitia", "Crepereia", "Critonia",
	"Cupiennia", "Curia", "Curiatia", "Curtia", "Curtilia",
	"Cuspia", "Decia", "Decimia", "Dellia", "Didia",
	"Digitia", "Domitia", "Duilia", "Durmia", "Duronia",
	"Egilia", "Egnatia", "Egnatuleia", "Ennia", "Epidia",
	"Eppia", "Equitia", "Erucia", "Fabia", "Fabricia",
	"Fadia", "Falcidia", "Fannia", "Farsuleia", "Faucia",
	"Fidiculania", "Flaminia", "Flavia", "Fonteia", "Foslia",
	"Fufia", "Fuficia", "Fufidia", "Fulcinia", "Fulvia",
	"Fundania", "Furia", "Furnia", "Gabinia", "Galeria",
	"Gallia", "Gargonia", "Gavia", "Gegania", "Gellia",
	"Geminia", "Genucia", "Gessia", "Grania", "Gratidia",
	"Hateria", "Heia", "Helvia", "Helvidia", "Herennia",
	"Herminia", "Hirria", "Hirtia", "Hirtuleia", "Horatia",
	"Hortensia", "Hosidia", "Hostilia", "Iccia", "Icilia",
	"Insteia", "Julia", "Junia", "Juventia", "Laberia",
	"Labiena", "Laceria", "Laelia", "Laenia", "Laetilia",
	"Laetoria", "Lafrenia", "Lamponia", "Laronia", "Lartia",
	"Latinia", "Lavinia", "Lecania", "Lentidia", "Licinia",
	"Ligaria", "Livia", "Lollia", "Lucceia", "Luciena",
	"Lucilia", "Lucretia", "Luria", "Luscia", "Lusia",
	"Lutatia", "Maecia", "Maecilia", "Maelia", "Maenia",
	"Maevia", "Magia", "Mallia", "Mamilia", "Manilia",
	"Manlia", "Marcia", "Maria", "Matia", "Matiena",
	"Matinia", "Matrinia", "Memmia", "Menenia", "Menia",
	"Mescinia", "Messia", "Metilia", "Mettia", "Mimesia",
	"Minatia", "Minicia", "Minidia", "Minucia", "Modia",
	"Mucia", "Mummia", "Munatia", "Mussidia", "Mustia",
	"Mutia", "Naevia", "Nasennia", "Nasidia", "Nasidiena",
	"Nautia", "Neratia", "Neria", "Ninnia", "Nonia",
	"Norbana", "Novellia", "Novia", "Numeria", "Numicia",
	"Numisia", "Numitoria", "Nummia", "Numonia", "Nymphidia",
	"Obellia", "Obultronia", "Occia", "Oclatia", "Oclatinia",
	"Octavena", "Octavia", "Ofania", "Ofilia", "Ogulnia",
	"Ollia", "Opellia", "Opetreia", "Opimia", "Opiternia",
	"Oppia", "Oppidia", "Opsia", "Opsidia", "Opsilia",
	"Orbia", "Orbicia", "Orbilia", "Orchia", "Orcivia",
	"Orfia", "Orfidia", "Oscia", "Ostoria", "Otacilia",
	"Ovidia", "Ovinia", "Paccia", "Pacidia", "Pacilia",
	"Paconia", "Pactumeia", "Pacuvia", "Palfuria",
	"Palpellia", "Pantuleia", "Papia", "Papinia", "Papiria",
	"Pasidia", "Pasidiena", "Passiena", "Patulcia",
	"Pedania", "Pedia", "Peducaea", "Percennia", "Perperna",
	"Persia", "Pescennia", "Petillia", "Petreia", "Petronia",
	"Pinaria", "Pompeia", "Pompilia", "Pomponia", "Poppaea",
	"Porcia", "Postumia", "Potitia", "Procilia", "Publicia",
	"Publilia", "Quinctia", "Quinctilia", "Rabiria",
	"Remmia", "Romilia", "Roscia", "Rutilia", "Salvia",
	"Scribonia", "Sedatia", "Sempronia", "Septimia",
	"Sergia", "Sertoria", "Servilia", "Sestia", "Sextia",
	"Sextilia", "Sicinia", "Sosia", "Stertinia", "Sulpicia",
	"Tarpeia", "Tarquinia", "Tarquitia", "Terentia",
	"Tineia", "Titia", "Tullia", "Ulpia", "Ummidia",
	"Valeria", "Velia", "Verginia", "Vettia", "Veturia",
	"Villia", "Viviana", "Vipsania", "Visellia", "Vitellia"
	]

M_ROMAN_COGNOMEN = [
	"Aculeo", "Agricola", "Agrippa", "Ahala", "Ahenobarbus",
	"Albinus", "Albus", "Ambustus", "Annalis", "Aquila",
	"Aquilinus", "Arvina", "Asellio", "Asina", "Atellus",
	"Avitus", "Balbus", "Barba", "Barbatus", "Bassus",
	"Bestia", "Bibaculus", "Bibulus", "Blaesus", "Brocchus",
	"Brutus", "Bubulcus", "Bucco", "Bulbus", "Buteo",
	"Caecus", "Caepio", "Caesar", "Calidus", "Calvinus",
	"Calvus", "Camillus", "Caninus", "Canus", "Capito",
	"Carbo", "Catilina", "Cato", "Catulus", "Celer",
	"Celsus", "Cethegus", "Cicero", "Cicurinus", "Cilo",
	"Cincinnatus", "Cinna", "Cordus", "Cornicen", "Cornutus",
	"Corvinus", "Corvus", "Cossus", "Costa", "Cotta",
	"Crassipes", "Crassus", "Crispinus", "Crispus", "Culleo",
	"Curio", "Cursor", "Curvus", "Dentatus", "Denter",
	"Dento", "Dives", "Dolabella", "Dorsuo", "Drusus",
	"Figulus", "Fimbria", "Flaccus", "Flavus", "Florus",
	"Fronto", "Fullo", "Fusus", "Galeo", "Gemellus",
	"Glabrio", "Gracchus", "Gurges", "Habitus", "Helva",
	"Imperiosus", "Iullus", "Labeo", "Lactuca", "Laenas",
	"Lanatus", "Laevinus", "Laterensis", "Lentulus",
	"Lepidus", "Libo", "Licinus", "Longus", "Lucullus",
	"Lupus", "Lurco", "Macer", "Macula", "Malleolus",
	"Mamercus", "Marcellus", "Maro", "Merenda", "Mergus",
	"Merula", "Messalla", "Metellus", "Murena", "Mus",
	"Musca", "Nasica", "Naso", "Natta", "Nepos", "Nero",
	"Nerva", "Niger", "Novellus", "Ocella", "Pacilus",
	"Paetus", "Pansa", "Papus", "Paterculus", "Paullus",
	"Pavo", "Pera", "Pictor", "Piso", "Plancus", "Plautus",
	"Poplicola", "Postumus", "Potitus", "Praeconinus",
	"Praetextatus", "Priscus", "Proculus", "Publicola",
	"Pulcher", "Pullus", "Pulvillus", "Purpureo",
	"Quadratus", "Ralla", "Regillus", "Regulus", "Rufus",
	"Ruga", "Rullus", "Rutilus", "Salinator", "Saturninus",
	"Scaeva", "Scaevola", "Scapula", "Scaurus", "Scipio",
	"Scrofa", "Seneca", "Severus", "Silanus", "Silo",
	"Silus", "Stolo", "Strabo", "Structus", "Sulla", "Sura",
	"Taurus", "Triarius", "Trigeminus", "Trio", "Tubero",
	"Tubertus", "Tubulus", "Tuditanus", "Tullus", "Turdus",
	"Varro", "Varus", "Vatia", "Verres", "Vespillo", "Vetus",
	"Vitulus", "Volusus"
	]

F_ROMAN_COGNOMEN = [
	"Aculeo", "Agricola", "Agrippa", "Ahala", "Ahenobarba",
	"Albina", "Alba", "Ambusta", "Annalis", "Aquila",
	"Aquilina", "Arvina", "Asellio", "Asina", "Atella",
	"Avita", "Balba", "Barba", "Barbata", "Bassa", "Bestia",
	"Bibacula", "Bibula", "Blaesa", "Broccha", "Bruta",
	"Bubulca", "Bucco", "Bulba", "Buteo", "Caeca", "Caepio",
	"Caesar", "Calida", "Calvina", "Calva", "Camilla",
	"Canina", "Cana", "Capito", "Carbo", "Catilina", "Cato",
	"Catula", "Celeris", "Celsa", "Cethega", "Cicero",
	"Cicurina", "Cilo", "Cincinnata", "Cinna", "Corda",
	"Cornicen", "Cornuta", "Corvina", "Corva", "Cossa",
	"Costa", "Cotta", "Crassipes", "Crassa", "Crispina",
	"Crispa", "Culleo", "Curio", "Cursor", "Curva",
	"Dentata", "Dentra", "Dento", "Dives", "Dolabella",
	"Dorsuo", "Drusa", "Figula", "Fimbria", "Flacca",
	"Flava", "Flora", "Fronto", "Fullo", "Fusa", "Galeo",
	"Gemella", "Glabrio", "Graccha", "Gurges", "Habita",
	"Helva", "Imperiosa", "Iulla", "Labeo", "Lactuca",
	"Laenas", "Lanata", "Laevina", "Laterensis", "Lentula",
	"Lepida", "Libo", "Licina", "Longa", "Luculla", "Lupa",
	"Lurco", "Macra", "Macula", "Malleola", "Mamerca",
	"Marcella", "Maro", "Merenda", "Merga", "Merula",
	"Messalla", "Metella", "Murena", "Mus", "Musca",
	"Nasica", "Naso", "Natta", "Nepos", "Nero", "Nerva",
	"Nigra", "Novella", "Ocella", "Pacila", "Paeta", "Pansa",
	"Papa", "Patercula", "Paulla", "Pavo", "Pera", "Pictrix",
	"Piso", "Planca", "Plauta", "Poplicola", "Postuma",
	"Potita", "Praeconina", "Praetextata", "Prisca",
	"Procula", "Publicola", "Pulchra", "Pulla", "Pulvilla",
	"Purpureo", "Quadrata", "Ralla", "Regilla", "Regula",
	"Rufa", "Ruga", "Rulla", "Rutila", "Salinatrix",
	"Saturnina", "Scaeva", "Scaevola", "Scapula", "Scaura",
	"Scipio", "Scrofa", "Seneca", "Severa", "Silana", "Silo",
	"Sila", "Stolo", "Strabo", "Structa", "Sulla", "Sura",
	"Taura", "Triaria", "Trigemina", "Trio", "Tubero",
	"Tuberta", "Tubula", "Tuditana", "Tulla", "Turda",
	"Varro", "Vara", "Vatia", "Verres", "Vespillo", "Vetus",
	"Vitula", "Volusa"
	]

class RomanGenerator(Generator):

	def __init__(self, mPraenomen, fPraenomen, nomen, mCognomen, fCognomen):
		super(RomanGenerator, self).__init__(mPraenomen, fPraenomen, mCognomen, fCognomen, nomen)

	def generate(self, pUnit, pCity, masculine):
		nomen = self.choice(self.surnames)
		if (masculine):
			praenomen = self.choice(self.masculineFirstNames)
			nomen = nomen[:-1]+"us"
			cognomen = self.choice(self.masculineMiddleNames)
		else:
			praenomen = self.choice(self.feminineFirstNames)
			cognomen = self.choice(self.feminineMiddleNames)
		result = nomen
		if (praenomen != nomen):
			result = praenomen + " " + result
		if (nomen != cognomen):
			result = result + " " + cognomen
		return result

GENERATOR_ROMAN = RomanGenerator(M_ROMAN_PRAENOMEN, F_ROMAN_PRAENOMEN, ROMAN_NOMEN, M_ROMAN_COGNOMEN, F_ROMAN_COGNOMEN)

M_FIRST_RUSSIAN = [
	"Afanasy", "Aleksandr", "Aleksey", "Almaz", "Alyosha", "Anastas",
	"Anatoly", "Andrey", "Anton", "Antoniy", "Arseny", "Artem",
	"Artemy", "Artur", "Boris", "Bryachislav", "Constantin", "Daniil",
	"Davyd", "Demyan", "Denis", "Dmitry", "Emanuel", "Evgeny",
	"Fedosiy", "Fedot", "Felix", "Feognost", "Feropont", "Fyodor",
	"Gavrila", "Gennady", "Georgy", "Germogen", "Gleb", "Grigory",
	"Iaroslav", "Ignatiy", "Igor", "Illarion", "Ilnur", "Ilya",
	"Ingvar", "Ioann", "Iosif", "Iov", "Ivan", "Iziaslav", "Kiril",
	"Klavdy", "Kuzma", "Leonid", "Leonty", "Lev", "Makariy",
	"Mikhail", "Mily", "Mstislav", "Nikita", "Nikolai", "Nil", "Oleg",
	"Orest", "Osip", "Paisiy", "Pakhomy", "Pavel", "Poluekt",
	"Prokhor", "Pyotr", "Rogvolod", "Roman", "Rostislav", "Rurik",
	"Savva", "Seraphim", "Sergei", "Simeon", "Stepan", "Sveneld",
	"Sviatopolk", "Sviatoslav", "Timofei", "Valentin", "Vasily",
	"Viacheslav", "Viktor", "Vissarion", "Vladimir", "Vladislav",
	"Volodar", "Vseslav", "Vsevolod", "Yakov", "Yaropolk", "Yefim",
	"Yemelyan", "Yerofey", "Yury", "Zakhar"
	]

M_PATRONYMIC_RUSSIAN = [
	"Adamovich", "Afanasyevich", "Akimovich", "Aleksandrovich",
	"Alekseyevich", "Anastasovich", "Anatolyevich", "Andreyevich",
	"Antonovich", "Apollonovich", "Arsenyevich", "Artamonovich",
	"Artemyevich", "Arturovich", "Augustinovich", "Azatovich",
	"Borisovich", "Bryachislavich", "Constantinovich", "Danilovich",
	"Davidovich", "Demyanovich", "Denisovich", "Dmitrievich",
	"Dorofeyevych", "Emilyevich", "Erikovich", "Fedorovich",
	"Felixovich", "Filippovich", "Fyodorovich", "Gavrilovich",
	"Gennadyevich", "Georgievich", "Glebovich", "Grigoryevich",
	"Ignatich", "Igorevich", "Illarionovich", "Ilyich", "Ilyinich",
	"Ioannovich", "Iosifovich", "Ivanovich", "Iziaslavich",
	"Karlovich", "Kirilovich", "Lavrentievich", "Leonardovich",
	"Leonidovich", "Leontyevich", "Lukich", "Lvovich", "Markovich",
	"Matveyevich", "Maximilianovich", "Mikailovich", "Mstislavich",
	"Nikiforovich", "Nikitich", "Nikolaevich", "Olegovich",
	"Onufriyevich", "Osipovich", "Patrikievich", "Pavlovich",
	"Petrovich", "Platonovich", "Poluektovich", "Prokhorovich",
	"Romanovich", "Rostislavich", "Rurikovich", "Savvich",
	"Sergeyevich", "Simeonovich", "Stanislovich", "Stepanovich",
	"Sveneldovich", "Sviatoslavich", "Tarasovich", "Tarasyevich",
	"Timofeyevich", "Ustinovich", "Valentinovich", "Valeryevich",
	"Vasilyevich", "Vasylkovych", "Viktorovich", "Vissarionovich",
	"Vladimirovich", "Vladislavovich", "Vseslavich", "Vsevolodovich",
	"Yakovlevich", "Yaroslavich", "Yefimovich", "Yevgenyevich",
	"Yuryevich", "Zakharovich"
	]

M_LAST_RUSSIAN = [
	"Alexseev", "Anikin", "Antropov", "Balakirev", "Basargin",
	"Basin", "Baykov", "Belyi", "Berdyaev", "Blok", "Bulgakov",
	"Chistyakov", "Chorikov", "Dolgorukov", "Donskoy", "Dostoyevsky",
	"Durasov", "Florensky", "Fradkov", "Gapon", "Godunov", "Golitsyn",
	"Gordiy", "Gorsky", "Herzen", "Iskander", "Ivanov", "Kalita",
	"Karamazov", "Kasyanov", "Kazakov", "Kikin", "Kiprensky",
	"Klyuchevsky", "Konovalov", "Korneichuk", "Korsakov", "Koshkin",
	"Kosoy", "Kramskoi", "Lebedev", "Lensky", "Levitsky", "Lomakin",
	"Lossky", "Lvov", "Makovsky", "Matveyev", "Medvedev", "Mendeleev",
	"Mamontov", "Menshikov", "Nabokov", "Naryshkin", "Nesterov",
	"Nevsky", "Ogarev", "Onegin", "Pavlov", "Peshtich", "Popov",
	"Prokudin", "Pushkin", "Putin", "Repin", "Riasanovsky", "Rimsky",
	"Romanov", "Romanovsky", "Shchukin", "Shein", "Shemyaka",
	"Sheremetiev", "Shuvalov", "Shuyskiy", "Silayev", "Skobelev",
	"Snitkin", "Sokolovsky", "Solovyov", "Strygin", "Tatishchev",
	"Tchaikovsky", "Tcherepnin", "Tolstoy", "Tretyakov", "Trubetskoy",
	"Vasnetsov", "Vyazemsky", "Vereshchagin", "Vernadsky", "Voronin",
	"Vrubel", "Vyazemsky", "Yaroshenko", "Yeltsin", "Yuriev",
	"Zakharyin", "Zavadovsky", "Zubkov"
	]

F_FIRST_RUSSIAN = [
	"Adelaida", "Agafya", "Agniya", "Agrafena", "Aleksandra", "Alena",
	"Alevtina", "Alia", "Alla", "Allogia", "Anastasia", "Anna",
	"Antonina", "Avdotya", "Dana", "Daria", "Dina", "Domna",
	"Ekaterina", "Elena", "Elizaveta", "Ella", "Elmira", "Elvira",
	"Emilia", "Evgenia", "Evdoksia", "Feodosia", "Feozva", "Fyokla",
	"Galina", "Gitlya", "Inna", "Ionna", "Irina", "Izabella",
	"Izolda", "Khristina", "Kira", "Kseniya", "Larisa", "Lidia",
	"Liuba", "Liya", "Liza", "Lucia", "Luiza", "Lydia", "Lyubov",
	"Lyudmila", "Malusha", "Marfa", "Maria", "Marianna", "Marina",
	"Marta", "Matryona", "Milica", "Nadedja", "Nadezhda", "Nadya",
	"Nailya", "Naina", "Natacha", "Natalya", "Nikita", "Nina",
	"Oksana", "Olga", "Paula", "Pelageya", "Perl", "Polina",
	"Polyxena", "Praskovia", "Predslava", "Raisa", "Rogneda", "Roza",
	"Rufina", "Solomonia", "Sophia", "Svetlana", "Tamara", "Tatiana",
	"Uliana", "Valentina", "Valeriya", "Valya", "Varvara", "Vasilisa",
	"Vera", "Veronika", "Victoria", "Vlatka", "Yana", "Yevdokia",
	"Yulia", "Zinaida", "Zoya"
	]

F_PATRONYMIC_RUSSIAN = [
	"Abdulbasirovna", "Adamovna", "Adolfovna", "Akhatovna",
	"Albertovna", "Aleksandrovna", "Alekseyevna", "Anatolyevna",
	"Andreyevna", "Andrianovna", "Anisimovna", "Antonovna",
	"Arkadyevna", "Bogdanovna", "Borisovna", "Bryachislavna",
	"Constantinovna", "Danilovna", "Davidovna", "Denisovna",
	"Dmitriyevna", "Edgarovna", "Emilyevna", "Erikovna", "Fargatovna",
	"Federovna", "Felixovna", "Filippovna", "Fyodorovna",
	"Gavrilovna", "Gennadyevna", "Georgievna", "Glebovna",
	"Grigoriyevna", "Gustavovna", "Igorevna", "Ilarionovna",
	"Ilyichna", "Ilyinichna", "Ioannovna", "Iosifovna", "Isaevna",
	"Ivanovna", "Iziaslavna", "Karlovna", "Kirilovna", "Korneyevna",
	"Lavrentievna", "Lazarevna", "Leonardovna", "Leonidovna",
	"Leontyevna", "Leopoldovna", "Livovna", "Luknichna", "Lukyanovna",
	"Lvovna", "Mariusovna", "Markovna", "Matveyevna",
	"Maximilianovna", "Maximovna", "Medzhidovna", "Meerovna",
	"Mikhailovna", "Mstislavna", "Nikitichna", "Nikolayevna",
	"Olegovna", "Onufriyevna", "Osipovna", "Patrikievna", "Pavlovna",
	"Petrovna", "Platonovna", "Rafailovna", "Romanovna",
	"Sakhipzadovna", "Samuilovna", "Savvichna", "Semyonovna",
	"Sergeyevna", "Shvarnovna", "Stepanovna", "Temryukovna",
	"Valentinovna", "Valerianovna", "Valeryevna", "Vasilievna",
	"Viktorovna", "Vitalyevna", "Vladimirovna", "Vladislavovna",
	"Yakovlevna", "Yaroslavna", "Yefremovna", "Yegorovna",
	"Yermolayevna", "Yuryevna", "Zinovievna"
	]

F_LAST_RUSSIAN = [
	"Akhmatova", "Alexandrova", "Apraksina", "Barbashina",
	"Basargina", "Bebutova", "Belskaya", "Brasova", "Buynosova",
	"Charskaya", "Chekhova", "Chelishcheva", "Churilova", "Danilova",
	"Dashkova", "Davidova", "Dolgorukova", "Dostoyevskaya",
	"Dubrovina", "Glinskaya", "Godunova", "Golovina", "Gorbataya",
	"Gorenko", "Granatova", "Grushtetskaya", "Istomina", "Izvitskaya",
	"Karatygina", "Karelina", "Kolosova", "Komissarzhevskaya",
	"Kositskaya", "Kovalyova", "Kusheleva", "Isaeva", "Larina",
	"Lescheva", "Lilina", "Linskaya", "Lopukhina", "Mandelstam",
	"Michurina", "Miloslavskaya", "Musina", "Nagaya", "Naryshkina",
	"Nikulina", "Paley", "Panaeva", "Perevostchikova", "Petipa",
	"Pistohlkors", "Podgorinova", "Popova", "Protazanova", "Pushkina",
	"Rakhmanova", "Rasputina", "Repnina", "Romanova", "Romanovskaya",
	"Rostovskaia", "Rukavishnikova", "Saburova", "Saltykova",
	"Samoilova", "Sandunova", "Semyonova", "Sheremeteva", "Shestova",
	"Shlykova", "Shuiskaya", "Simeonova", "Skavronskaya", "Skuratova",
	"Snitkina", "Strelkova", "Streshnyova", "Struskaya",
	"Surovshchikova", "Tarusskaya", "Tolstaya", "Tomanovskaya",
	"Uranova", "Velyaminova", "Viktorova", "Vinokurova", "Vorontzova",
	"Vyrubova", "Yermolova", "Yezhova", "Yurieva", "Yusupova",
	"Zaborovskaya", "Zakharyina", "Zhemchugova", "Zheverzheeva",
	"Zhukovskaya", "Ziller"
	]

class RussianGenerator(Generator):

	def __init__(self, mFirst, fFirst, mPatronymic, fPatronymic,
				 mLast, fLast):
		super(RussianGenerator, self).__init__(mFirst, fFirst,
				 mPatronymic, fPatronymic, [])
		self.masculineLastNames = mLast
		self.feminineLastNames = fLast

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			first = self.choice(self.masculineFirstNames)
			patronymic = self.choice(self.masculineMiddleNames)
			last = self.choice(self.masculineLastNames)
		else:
			first = self.choice(self.feminineFirstNames)
			patronymic = self.choice(self.feminineMiddleNames)
			last = self.choice(self.feminineLastNames)
		return first + " " + patronymic + " " + last

GENERATOR_RUSSIAN = RussianGenerator(M_FIRST_RUSSIAN,
									 F_FIRST_RUSSIAN,
									 M_PATRONYMIC_RUSSIAN,
									 F_PATRONYMIC_RUSSIAN,
									 M_LAST_RUSSIAN,
									 F_LAST_RUSSIAN)

M_FIRST_SPANISH = [
	u"Agustín", u"Alberto", u"Alejandro", u"Alfonso", u"Alfredo", u"Amadeo", u"Aniello", u"Antonio", u"Aquileo", u"Augusto", u"Bermudo", u"Bernardo", u"Bonifacio", u"Fidel", u"Carlos", u"César", u"Cipriano", u"Clímaco", u"Cristóbal", u"Diego", u"Domingo", u"Eduardo", u"Eleuterio", u"Elias", u"Eliseo", u"Emilio", u"Enrique", u"Estanislau", u"Eugenio", u"Eusebio", u"Eustorgio", u"Esteban", u"Ezequiel", u"Fabio", u"Fadrique", u"Federico", u"Felipe", u"Fernando", u"Francisco", u"Gabriel", u"Gonzalo", u"Gregorio", u"Guillermo", u"Gustavo", u"Héctor", u"Hernán", u"Ibon", u"Ignacio", u"Iñaki", u"Isidro", u"Jacinto", u"Januario", u"Javier", u"Joaquín", u"Jofré", u"Jorge", u"José", u"Juan", u"Julián", u"Justo ", u"Laureano", u"León", u"Luis", u"Manuel", u"Marcelo", u"Marco", u"Mariano", u"Martin", u"Miguel", u"Nel", u"Nepociano", u"Nicolás", u"Ordoño", u"Oscar", u"Pablo", u"Pascual", u"Paulino", u"Pedro", u"Pelayo", u"Pío", u"Rafael", u"Raimundo", u"Ramiro", u"Ramón", u"Ricardo", u"Rodrigo", u"Romà", u"Salvador", u"Sancho", u"Santiago", u"Santos", u"Saúl", u"Serafín", u"Silvestre", u"Telmo", u"Tomás", u"Valentín", u"Vicente", u"Víctor", u"Wenceslao"
	]

F_FIRST_SPANISH = [
	u"Adelaida", u"Aisha", u"Alaíde", u"Alejandrina", u"Alicia", u"Almudena", u"Amalia", u"Ana", u"Ángela", u"Anna", u"Annabel", u"Antonia", u"Aurora", u"Beatriz", u"Belén", u"Blanca", u"Borita", u"Carmen", u"Carolina", u"Catalina", u"Clara", u"Clementina", u"Concepción", u"Concha", u"Constanza", u"Conxita", u"Cristina", u"Dora", u"Dorotea", u"Dulce", u"Edith", u"Elena", u"Elina", u"Elisava", u"Eloísa", u"Elvira", u"Ende", u"Ernestina", u"Espido", u"Esther", u"Eva", u"Fátima", u"Federica", u"Felícia", u"Fernanda", u"Flavia", u"Francisca", u"Gabriela", u"Gemma", u"Gertrudis", u"Gloria", u"Goya", u"Hilda", u"Inés", u"Isabel", u"Josefa", u"Josefina", u"Juana", u"Julia", u"Laura", u"Leonor", u"Lourdes", u"Lucía", u"Lucrècia", u"Luisa", u"Lupe", u"Manuela", u"Margarita", u"Mari", u"María", u"Mariana", u"Matilda", u"Matilde", u"Mercè", u"Mercedes", u"Miriam", u"Natividad", u"Nuria", u"Olga", u"Olvido", u"Paloma", u"Patricia", u"Paula", u"Petrona", u"Pilar", u"Rosa", u"Rosalía", u"Rosana", u"Sancha", u"Silvia", u"Susana", u"Teresa", u"Urraca", u"Úrsula", u"Victoria", u"Xela", u"Yolanda", u"Zaida", u"Zenobia", u"Zulema"
	]

LAST_SPANISH = [
	u"Abad", u"Abadía", u"Abril", u"Acedo", u"Acosta", u"Agudo", u"Alcántara", u"Almodóvar", u"Altamirano", u"Amador", u"Amenábar", u"Ancízar", u"Ansaldo", u"Arboleda", u"Areso", u"Arrate", u"Arrondo", u"Artola", u"Aurtenechea", u"Azkuna", u"Bahamonde", u"Basora", u"Basterra", u"Belausteguigoitia", u"Bermúdez", u"Blasco", u"Borbón", u"Borja", u"Borrás", u"Bru", u"Brunet", u"Bullejos", u"Caballero", u"Cabanellas", u"Cajal", u"Calderón", u"Camilión", u"Cañizares", u"Cantos", u"Caro", u"Carou", u"Castillo", u"Castro", u"Ceán", u"Cerda", u"Cervantes", u"Comes", u"Concha", u"Córdoba", u"Cortés", u"Dalí", u"Dávila", u"Domènech", u"Domínguez", u"Doncel", u"Duhalde", u"Encinas", u"Enriquez", u"Esnaola", u"Faría", u"Fernández", u"Ferreira", u"Ferrer", u"Figueroa", u"Flórez", u"Fonseca", u"Forns", u"Franco", u"Freixas", u"Gaínza", u"Galarza", u"García", u"Garreta", u"Garrido", u"Gómez", u"González", u"Gonzalo", u"Goya", u"Grandes", u"Gutiérrez", u"Herrera", u"Holguín", u"Hurtado", u"Ibáñez", u"Iriondo", u"Jeanguenat", u"Joanes", u"Jordana", u"Labordeta", u"Lafora", u"Landaluce", u"Lanzol", u"Lara", u"Largacha", u"Leal", u"Lecumberri", u"Letamendía", u"Liñán", u"Lleras", u"López", u"Lorena", u"Lorente", u"Lorenzo", u"Lucientes", u"Madrazo", u"Maella", u"Maeztu", u"Mallarino", u"Manosalbas", u"Mariño", u"Marroquín", u"Martínez", u"Masip", u"Méndez", u"Mendiguren", u"Mendoza", u"Menem", u"Mérida", u"Moledo", u"Monroy", u"Montejo", u"Montero", u"Montoya", u"Morante", u"Moreno", u"Mosquera", u"Moure", u"Muñoz", u"Murillo", u"Navarro", u"Nó", u"Núñez", u"Olaya", u"Ortiz", u"Ospina", u"Otálora", u"Otero", u"Páez", u"Parra", u"Payán", u"Pérez", u"Pinilla", u"Pinto", u"Piquer", u"Pizarro", u"Portaña", u"Prieto", u"Pumarejo", u"Quintana", u"Racines", u"Raimúndez", u"Ramón", u"Restrepo", u"Revuelta", u"Reyes", u"Riascos", u"Ricaurte", u"Riestrá", u"Rivera", u"Rodriguez", u"Rojas", u"Rúa", u"Ruiz", u"Saá", u"Saavedra", u"Sacanell", u"Sagi", u"Salazar", u"Saldaña", u"Salgar", u"Sánchez", u"Sanclemente", u"Sanjurjo", u"Santos", u"Sanz", u"Serrano", u"Sousa", u"Suárez", u"Suñer", u"Tapia", u"Tobar", u"Toro", u"Tovar", u"Trilla", u"Trujillo", u"Urdaneta", u"Urreta", u"Valderrama", u"Valencia", u"Vallana", u"Vásquez", u"Vejarano", u"Velasco", u"Velázquez", u"Vicandi", u"Villanueva", u"Viola", u"Zaldúa", u"Zambudio", u"Zarraonandía",
	]

class SpanishGenerator(Generator):

	def __init__(self, mFirst, fFirst, family):
		super(SpanishGenerator, self).__init__(mFirst, fFirst,
				 [], [], family)
		self.prefixes = ["de ", "", "", "", "", "", "", "", ""]
		self.conjunctions = [" y de ", " y " , " y ", "-", "-", "-", "-", " ", " ", " ",
							 " ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
							 " ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
							 " ", " ", " ", " ", " ", " "]

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			first = self.choice(self.masculineFirstNames)
		else:
			first = self.choice(self.feminineFirstNames)
		paternal = self.choice(self.surnames)
		maternal = self.choice(self.surnames)
		prefix = self.choice(self.prefixes)
		conjunction = self.choice(self.conjunctions)
		return first + " " + prefix + paternal + conjunction + maternal

GENERATOR_SPANISH = SpanishGenerator(M_FIRST_SPANISH,
									 F_FIRST_SPANISH,
									 LAST_SPANISH)

SUMERIAN_MALE = [
	"Abu", "Abzu", "Adapa", "Aga", "Alalngar", "Alulim", "Amar-sin", "Anshar", "Anu", "Apilkin", "Asaruludu", "Bur-suen", "Dagon", "Dudu", "Dumuzid", "Eannatum", "Elulu", "Enbilulu", "Enki", "Enkidu", "Enkimdu", "Enlil", "Enlil-bani", "Enmebaragesi", "Enmengalana", "Enmenluana", "Enmerkar", "Ennuntarahana", "Enshakushanna", "Erra-imitti", "Gilgamesh", "Gudea", "Hablum", "Hadad", "Ibbi-sin", "Ibranum", "Iddin-dagan", "Igigi", "Ilulu", "Imi", "Irarum", "Ishbi-erra", "Ishme-dagan", "Isimud", "Iter-pisha", "Kingu", "La-ba'shum", "La-erabum", "Lahar", "Lahmu", "Lipit-enlil", "Lipit-ishtar", "Lugalanda", "Lugalannemundu", "Lugalbanda", "Lugal-irra", "Lugal-kitun", "Lugalzagesi", "Lulal", "Manishtushu", "Melem-ana", "Mesh-he", "Mesannepada", "Meskalamdug", "Mummu", "Nabu", "Nanum", "Naram-sin", "Nergal", "Ningishzida", "Nintulla", "Ninurta", "Papsukkal", "Puzer-mama", "Puzur-suen", "Rimush", "Sarru-ukin", "Shara", "Sharkalisharri", "Shu-ilishu", "Shulgi", "Shu-sin", "Shu-turul", "Sin", "Si'um", "Tammuz", "Tirigan", "Udul-kalama", "Ur-baba", "Urdukuga", "Ur-nammu", "Ur-nanshe", "Ur-ninurta", "Ur-nungal", "Ur-zababa", "Urukagina", "Utu", "Utu-hengal", "Yarlaganda", "Zambiya"
	]

SUMERIAN_FEMALE = [
	"Ahatiwaqrat", "Ahunatum", "Akkazu", "Ama-arhus", "Amasagnul", "Ashusikildigir", "Aya", "Azimua", "Baranamtarra", "Bau", "Belessunu", "Belet-seri", "Beletum", "Belit", "Bikku-lum", "Bittatum", "Daqqartum", "Ealamassi", "Enanatuma", "Enheduanna", "Ereshkigal", "Eshargamelat", "Gatumdag", "Geshtinanna", "Gula", "Habannatum", "Iltani", "Ilusha-hegal", "Inanna", "Ishtar-gamelat", "Ishtar-ibbi", "Ishtarabiat", "Kammani", "Ki", "Kishar", "Ku-aya", "Kubaba", "Lahamu", "Lamashtu", "Lilith", "Liwwir-esagil", "Ma", "Mamitu", "Manatum", "Manungal", "Nakurtum", "Nammu", "Nanaya", "Nanshe", "Negun", "Nidaba", "Nin", "Ninbanda", "Nin-dada", "Ninegal", "Ningal", "Ningikuga", "Ninhursag", "Nin-imma", "Nin-kagina", "Ninkasi", "Ninkurra", "Ninlil", "Ninmena", "Ninsar", "Ninshubur", "Ninsun", "Ninsutu", "Ninti", "Nunbarsegunu", "Nuratum", "Puabi", "Sapurtum", "Semiramis", "Shagshag", "Shala", "Shamhat", "Sharraitu", "Sharrat-sippar", "Shat-sin", "Shatu-murrim", "Shiptu", "Shub-ad", "Shulsaga", "Siduri", "Silili", "Sin-nada", "Sirara", "Siris", "Sirtir", "Summirat-ishtar", "Tabni-ishtar", "Takurtum", "Taram-uram", "Tashmet", "Tashultum", "Tiamat", "Ua-ildak", "Ummi-waqrat", "Yadidatum"
	]

GENERATOR_SUMERIAN = MarkovGenerator(SUMERIAN_MALE, SUMERIAN_FEMALE, SUMERIAN_MALE, SUMERIAN_FEMALE, SUMERIAN_MALE + SUMERIAN_FEMALE, 2, 15)

M_FIRST_VIKING = [
	u"Absalon", u"Adolph", u"Æmunðær", u"Alexander", u"Anders", u"Angantyr", u"Anton", u"Anund", u"Ari", u"Arnar", u"Arngrim", u"Arnórr", u"Asser", u"Auðunn", u"Axel", u"Baldur", u"Bengt", u"Bernt", u"Bjalfi", u"Bjarni", u"Carsten", u"Egill", u"Eilert", u"Einar", u"Eric", u"Erling", u"Eskil", u"Eugen", u"Eysteinn", u"Filip", u"Finnbogi", u"Folke", u"Fredrik", u"Gamli", u"Gissur", u"Godfred", u"Gormr", u"Grímr", u"Guðjón", u"Guðmundur", u"Gunnbjörn", u"Gustav", u"Hákon", u"Halfdanr", u"Hallbjorn", u"Hans", u"Harald", u"Hardeknud", u"Heiðrekr", u"Helgi", u"Hilding", u"Hjalmar", u"Hlöd", u"Hrøríkr", u"Hubertus", u"Ingi", u"Ingimar", u"Ísleifur", u"Ívarr", u"Johan", u"Jón", u"Karl", u"Ketill", u"Kissinger", u"Kjárr", u"Knútr", u"Kolbeinn", u"Kristófer", u"Kveldulf", u"Leifr", u"Lorens", u"Ludvig", u"Magnús", u"Maurits", u"Mikæl", u"Olaf", u"Ólafur", u"Örn ", u"Oscar", u"Páll", u"Per", u"Ring", u"Roger", u"Sigfred", u"Sigurðr", u"Sighvatr", u"Slagfiðr", u"Snorri", u"Stefan", u"Sveinn", u"Þórðr", u"Þorlákr", u"Þórr", u"Þorfinnr", u"Þorvaldr", u"Tryggvi", u"Ulf", u"Valdemar", u"Vigleik", u"Völundr"
	]

M_VIKING_PATRONYMIC = [
	u"Absalonsen", u"Aðalsteinsson", u"Adolphson", u"Alexandersson", u"Anderson", u"Angantyrsson", u"Antonsen", u"Anundsen", u"Arason", u"Arnarson", u"Ástríðarson", u"Baldursson", u"Benediktsson", u"Bengtson", u"Berntsen", u"Bjalfason", u"Björnsson", u"Carstensen", u"Edvardson", u"Egilsen", u"Eilertson", u"Einarson", u"Eiríksson", u"Eliasson", u"Erlingson", u"Eskildsen", u"Eugenson", u"Filipsen", u"Finnbogason", u"Folkeson", u"Fredrikson", u"Gissurarson", u"Godfredsen", u"Guðjónsson", u"Guðmundson", u"Grjótgarðsson", u"Gunnbjörnsson", u"Gustavsen", u"Gylfason", u"Hákonarson", u"Hallbjornsson", u"Halstensson", u"Hanssen", u"Haraldsson", u"Hardeknudsson", u"Hauksson", u"Heidreksson", u"Helgeson", u"Henriksson", u"Herjólfsson", u"Hildingson", u"Ingemarsson", u"Ingison", u"Ingimarsson", u"Jedvardsson", u"Johansen", u"Jónasson", u"Jónsson", u"Kárason", u"Karlson", u"Knútsson", u"Kolbeinsson", u"Kristjánsson", u"Kristóffersen", u"Kveldúlfsson", u"Larsen", u"Lorensen", u"Ludvigson", u"Magnússon", u"Mauritson", u"Mikælsen", u"Nilsson", u"Ögmundsson", u"Ólafsson", u"Oscarson", u"Pállson", u"Ragnarsson", u"Rogerson", u"Samúelsson", u"Sigfredsson", u"Sigurðarson", u"Snorrison", u"Skallagrímsson", u"Stefanson", u"Stenkilsson", u"Sturluson", u"Sverkersson", u"Teitsson", u"Þorbergsson", u"Þórðarson", u"Þorgilsson", u"Þórhallsson", u"Þorlákson", u"Þorvaldsson", u"Toresen", u"Tryggvason", u"Tumason", u"Ulfsson", u"Valdemarsøn", u"Völundarson"
	]

F_FIRST_VIKING = [
	u"Adalborj", u"Adis", u"Aila", u"Alfhild", u"Anna", u"Antje", u"Åsa", u"Aslaug", u"Astrid", u"Auðild", u"Auðr", u"Bergljot", u"Birna", u"Bjorg", u"Boedil", u"Brenda", u"Brynhild", u"Brynja", u"Cecilia", u"Christina", u"Elisa", u"Emilia", u"Emma", u"Estrid", u"Euphemia", u"Eva", u"Eyfura", u"Freda", u"Fredrica", u"Freydís", u"Freyja", u"Frida", u"Frigg", u"Fulla", u"Gefn", u"Gefjon", u"Gerd", u"Gersemi", u"Gná", u"Gudrun", u"Gullveig", u"Gunnhildr", u"Gunnr", u"Gunnvor", u"Gyda", u"Hallbera", u"Halldóra", u"Heiðr", u"Hel", u"Herfjötur", u"Herja", u"Hervor", u"Hildr", u"Hnoss", u"Hörn", u"Iðunn", u"Inger", u"Ingerid", u"Ingibjörg", u"Ingigerðr", u"Jörð", u"Lofn", u"Malmfred", u"Mardöll", u"María", u"Mö", u"Nanna", u"Nótt", u"Ölrún", u"Öndurguð", u"Ragna", u"Ragnheidr", u"Ragnhild", u"Róta", u"Sif", u"Sigríð", u"Sigrunn", u"Sigyn", u"Siv", u"Skaði", u"Skjálf", u"Skuld", u"Solveig", u"Svanhild", u"Þóra", u"Þröng", u"Þrúðr", u"Þrungva", u"Torhild", u"Torunn", u"Turid", u"Tyri", u"Ulrika", u"Unn", u"Urðr", u"Valkiria", u"Valfreyja", u"Vanadís", u"Vigdis", u"Yngvild"
	]

F_VIKING_PATRONYMIC = [
	u"Alexandersdottir", u"Andersdatter", u"Antonsdóttir", u"Anundsdotter", u"Arnarsdóttir", u"Arngrímsdóttir", u"Axelsdóttir", u"Baldursdóttir ", u"Baldursdóttir ", u"Benediktsdottir", u"Bengtsdotter ", u"Bergsdóttir", u"Bjarnsdottir", u"Björgvinsdóttir", u"Björnsdotter", u"Borgarhjortr", u"Edvardsdóttir", u"Egilsdóttir", u"Einarsdóttir", u"Eiriksdatter", u"Elíasdóttir", u"Erlingsdóttir", u"Eskilsdotter", u"Eysteinsdotter", u"Filipsdóttir", u"Finnbogadottir", u"Finnsdottir", u"Folkesdotter", u"Frederiksdatter", u"Frostadotter", u"Gandolfsdatter", u"Geirharðsdóttir", u"Gísladóttir", u"Gissurardóttir", u"Gormsdóttir", u"Gregoriusdotter", u"Grímsdóttir", u"Guðjónsdóttir", u"Gudmundsdottir", u"Gudnadottir", u"Gunnarsdóttir", u"Gunnbjörnsdóttir", u"Gunnlaugsdóttir", u"Gustavsdotter", u"Hákonardóttir", u"Halfdansdotter", u"Hallbjornsdottir", u"Halldórsdóttir", u"Hallgrímsdóttir", u"Hansdotter", u"Haraldsdatter", u"Hauksdóttir", u"Heidreksdatter", u"Helgesdatter", u"Herjólfsdóttir", u"Hilmarsdóttir", u"Hinriksdóttir", u"Hjálmarsdóttir", u"Ingesdotter", u"Ingimarsdottir", u"Ívarsdóttir", u"Jakobsdóttir", u"Jensdóttir", u"Johansdotter", u"Jökulsdóttir", u"Jonasdottir", u"Jónsdóttir", u"Karlsdotter", u"Ketilsdóttir", u"Knudsdatter", u"Kolbeinsdóttir", u"Kristjansdottir", u"Larsdatter", u"Leifsdottir", u"Ludvigsdatter", u"Magnusdottir", u"Nilsdotter", u"Ögmundsdóttir", u"Olafsdottir", u"Osvifrsdottir", u"Pálsdóttir", u"Pedersdatter", u"Ragnarsdóttir", u"Samúelsdóttir", u"Sigmundsdóttir", u"Sigurdardottir", u"Sigurdsdotter", u"Stefansdottir", u"Sveinsdóttir", u"Þórarinsdóttir", u"Þorgilsdottir", u"Þorhallsdottir", u"Þorisdotter", u"Þorlaksdottir", u"Þorvaldsdóttir", u"Toresdatter", u"Turgotsdotter", u"Ulfsdóttir", u"Valdemarsdatter", u"Vilhjálmsdóttir"
	]

class VikingGenerator(Generator):

	def __init__(self, mFirst, fFirst, mPatryonymic, fPatronymic):
		super(VikingGenerator, self).__init__(mFirst, fFirst, mFirst, fFirst, [])
		self.masculinePatronymic = mPatryonymic
		self.femininePatronymic = fPatronymic

	def generate(self, pUnit, pCity, masculine):
		if (masculine):
			return self.generateInternal(self.masculineFirstNames, self.masculineFirstNames, self.masculinePatronymic)
		else:
			return self.generateInternal(self.feminineFirstNames, self.feminineFirstNames, self.femininePatronymic)

GENERATOR_VIKING = VikingGenerator(M_FIRST_VIKING, F_FIRST_VIKING, M_VIKING_PATRONYMIC, F_VIKING_PATRONYMIC)

M_FIRST_ZULU = [
	"Afrika", "Ayanda", "Bambatha", "Bandise", "Bantu", "Baphethuxolo", "Bhambatha", "Bhekokwakhe", "Bhekuzulu", "Bongani", "Bonginkosi", "Bulelani", "Cetshwayo", "Chinezi", "Dabede", "Dingane", "Dingiswayo", "Dinuzulu", "Fikile", "Gcaleka", "Gumede", "Hintsa", "Hlomla", "Hlumelo", "Jama", "Josta", "Kagisho", "Kefentse", "Kgalema", "Khawuta", "Khomotso", "Langa", "Mabendle", "Mageba", "Makgatho", "Malandela", "Mangosuthu", "Maphangumzana", "Mduduzi", "Menzi", "Mnguni", "Mosibudi", "Motsoko", "Mpande", "Mpilo", "Mthunzi", "Mvume", "Mxolisi", "Nakedi", "Ndaba", "Ngangayezizwe", "Ngubengcuka", "Njongonkulu", "Nkosinathi", "Ngqeno", "Ntombela", "Ntsikelelo", "Nyaniso", "Phalo", "Phathakge", "Phiwayinkosi", "Phunga", "Potlako", "Ramopolo", "Rolihlahla", "Sakumzi", "Salukaphathwa", "Sandile", "Sarili", "Sekhukhune", "Sello", "Senzangakhona", "Senzeni", "Senzo", "Seshego", "Shaka", "Shipokosa", "Sibusiso", "Sigcawu", "Sigujana", "Sipho", "Sthembiso", "Tengo", "Thabang", "Thabo", "Thamsanqa", "Themba", "Thembelani", "Thembisile", "Tshiwo", "Tozama", "Tshidiso", "Umhlangana", "Vusumzi", "Vuyisile", "Xolani", "Zulu", "Zwelini", "Zwelihini", "Zwelivelile"
	]

F_FIRST_ZULU = [
	"Akhona", "Andile", "Ayabonga", "Babalwa", "Baleka", "Bongiwe", "Busisiwe", "Dikeledi", "Dineo", "Dlamini", "Hlengiwe", "Ischke", "Ithandile", "Katlego", "Kgomotso", "Khanyisile", "Kopana", "Kgothatso", "Lindiwe", "Lumka", "Lungisa", "Luntu", "Magogo", "Maite", "Makaziwe", "Mamela", "Mammule", "Mamphela", "Mandisa", "Mangwashi", "Mantithi", "Mapaseka", "Mapula", "Masabata", "Masoli", "Minenhle", "Mmabatho", "Mohale", "Mpho", "Muelwa", "Nalidi", "Nandi", "Nandipha", "Ngangezinye", "Nhlanhla", "Nkhensani", "Nkosazana", "Nokutela", "Nolubabalo", "Nomaindio", "Nomalizo", "Nomgcobo", "Nomkhosi", "Nompumelelo", "Nomsebenzi", "Nomzamo", "Nonhlanhla", "Nonkhululeko", "Nonkosi", "Nontando", "Nontsikelelo", "Nonyamezelo", "Nosipho", "Nosiviwe", "Nozipho", "Nozizwe", "Ntombizanele", "Pumeza", "Phumzile", "Pumla", "Raisibe", "Refilwe", "Sanah", "Seshee", "Sibilile", "Sibongile", "Sinalo", "Sindi", "Sinegugu", "Sisi", "Siyoli", "Sizakele", "Thandiwe", "Thokozile", "Thuli", "Thulisile", "Tsakane", "Tshegofatso", "Tsholofelo", "Tsoanelo", "Vuyisanani", "Zamandosi", "Zanele", "Zanyiwe", "Zenani", "Zenzile", "Zindsiswa", "Zintle", "Zukelwa", "Zukisa"
	]

LAST_ZULU = [
	"Bengu", "Biko", "Bopape", "Buthelezi", "Cele", "Chijoke", "Cwaba", "Dandala", "Danke", "Dhlomo", "Dikana", "Dikgacoi", "Dinkwanyane", "Dladla", "Dlamini", "Dlathu", "Dlwati", "Dube", "Dzedze", "Hani", "Hlomuka", "Hlongwane", "Itlhabanyeng", "Khumalo", "Jabavu", "Jafta", "Jele", "Jiba", "Khaka", "Khampepe", "Khumalo", "Kota", "Kubeka", "Leballo", "Mabalane", "Mabasa", "Mabeta", "Mabuse", "Mabuza", "Machaka", "Macozoma", "Madi", "Madikizela", "Madlala", "Madonsela", "Magagula", "Mahlangu", "Mahlo", "Makeba", "Makgoba", "Makhanya", "Makhene", "Makiwane", "Maku", "Makwetla", "Malema", "Manamela", "Manana", "Mandela", "Manganyi", "Mangena", "Mangisa", "Mapaila", "Mapisa", "Marawa", "Masekela", "Mashabane", "Mashatile", "Mashigo", "Matlwa", "Matshikiza", "Mazibuko", "Mbalula", "Mbeki", "Mbete", "Mbewe", "Mchunu", "Mdlalose", "Mfeketo", "Mhlantla", "Mkhwebane", "Mkhize", "Mlambo", "Mlungisi", "Mmaka", "Mndaweni", "Mntambo", "Modiselle", "Mollo", "Monakali", "Montjane", "Moropane", "Motlanthe", "Mpupha", "Msomi", "Mthethwa", "Mukasi", "Mushwana", "Mutsi", "Mxenge", "Ndleleni", "Ndodana", "Ndungane", "Ndzundzu", "Ngalo", "Ngcobo", "Ngcuka", "Nginza", "Ngubane", "Nhleko", "Nkabinde", "Nkoana", "Nkoane", "Nqakula", "Ntloko", "Ntozakhe", "Ntwanambi", "Nxasana", "Nxesi", "Nxumalo", "Nyamza", "Nyandeni", "Nyiki", "Nzimande", "Nzo", "Phahlane", "Phango", "Phiyega", "Pholo", "Phosa", "Pikoli", "Qequ", "Qoboza", "Ramagoshi", "Ramaphosa", "Ramphele", "Rankoe", "Seakgoe", "Selebi", "Senekal", "Shabalala", "Shenxane", "Sibande", "Sibeko", "Sibisi", "Simelane", "Sisulu", "Situ", "Thabethe", "Thipe", "Tlali", "Tshiqi", "Tsotsobe", "Tutu", "Veleko", "Yende", "Zokwana", "Zuma"
	]

GENERATOR_ZULU = Generator(M_FIRST_ZULU, F_FIRST_ZULU, M_FIRST_ZULU, F_FIRST_ZULU, LAST_ZULU)

class BarbarianGenerator(Generator):

	def __init__(self):
		super(BarbarianGenerator, self).__init__([], [], [], [], [])

	def generate(self, pUnit, pCity, masculine):
		active_generators = getDataValue("ACTIVE_GENERATORS") or {}
		civs = [civ for civ in GENERATORS.keys() if civ not in active_generators.keys()]
		civ = self.choice(civs)
		delegate = GENERATORS[civ]
		return delegate.generate(pUnit, pCity, masculine)

GENERATOR_BARBARIAN = BarbarianGenerator()

GENERATORS = {
	"CIVILIZATION_AMERICA": GENERATOR_AMERICAN,
	"CIVILIZATION_ARABIA": GENERATOR_ARABIAN,
	"CIVILIZATION_AZTEC": GENERATOR_AZTEC,
	"CIVILIZATION_BABYLON": GENERATOR_BABYLONIAN,
	"CIVILIZATION_BYZANTIUM": GENERATOR_BYZANTINE,
	"CIVILIZATION_CARTHAGE": GENERATOR_CARTHAGINIAN,
	"CIVILIZATION_CELT":  GENERATOR_CELTIC,
	"CIVILIZATION_CHINA": GENERATOR_CHINESE,
	"CIVILIZATION_EGYPT": GENERATOR_EGYPTIAN,
	"CIVILIZATION_ENGLAND": GENERATOR_ENGLISH,
	"CIVILIZATION_ETHIOPIA" : GENERATOR_ETHIOPIAN,
	"CIVILIZATION_FRANCE": GENERATOR_FRENCH,
	"CIVILIZATION_GERMANY": GENERATOR_GERMAN,
	"CIVILIZATION_GREECE": GENERATOR_GREEK,
	"CIVILIZATION_HOLY_ROMAN": GENERATOR_HOLY_ROMAN,
	"CIVILIZATION_INCA": GENERATOR_INCA,
	"CIVILIZATION_INDIA": GENERATOR_INDIAN,
	"CIVILIZATION_JAPAN": GENERATOR_JAPANESE,
	"CIVILIZATION_KHMER": GENERATOR_KHMER,
	"CIVILIZATION_KOREA": GENERATOR_KOREAN,
	"CIVILIZATION_MALI": GENERATOR_MALIAN,
	"CIVILIZATION_MAYA": GENERATOR_MAYAN,
	"CIVILIZATION_MONGOL": GENERATOR_MONGOLIAN,
	"CIVILIZATION_NATIVE_AMERICA": GENERATOR_NATIVE_AMERICAN,
	"CIVILIZATION_NETHERLANDS": GENERATOR_DUTCH,
	"CIVILIZATION_OTTOMAN": GENERATOR_OTTOMAN,
	"CIVILIZATION_PERSIA": GENERATOR_PERSIAN,
	"CIVILIZATION_PORTUGAL": GENERATOR_PORTUGUESE,
	"CIVILIZATION_ROME": GENERATOR_ROMAN,
	"CIVILIZATION_RUSSIA": GENERATOR_RUSSIAN,
	"CIVILIZATION_SPAIN": GENERATOR_SPANISH,
	"CIVILIZATION_SUMERIA": GENERATOR_SUMERIAN,
	"CIVILIZATION_VIKING": GENERATOR_VIKING,
	"CIVILIZATION_ZULU": GENERATOR_ZULU,
	"CIVILIZATION_BARBARIAN": GENERATOR_BARBARIAN
	}

# Lists of names have been generated using
# NameMage
# Version 1.02
# www.mapmage.com
# The really long list of first names.
firstNameList = ["Aalich","Aauwyr","Abadric","Abae","Abayth","Abeasean","Abeawin","Abeawyth","Aberi","Abilawin","Aboaseth","Abuch","Abuld","Acadan","Acarennor","Acarenwan","Acaresh","Acedon","Acela","Acendalath","Aceriwan","Aciannon","Acienn","Acilath","Aciold","Acoibaen","Acoretha","Acorev","Acy","Adaesh","Adaletrem","Adaof","Adeadfrid","Adendaloth","Adilitram","Adiramma","Adoewin","Adoreld","Adorevudd","Adorewyr","Adralemas","Adralid","Adraliwyr","Adraretram","Adrerild","Adriamar","Adrigo","Adrigom","Adroetrem","Adroewin","Adroinyth","Adwaebaen","Adwalegord","Adwaowin","Adwardomar","Adwareran","Adweacon","Adweawyth","Adwilinnor","Adwiredric","Adwoinwan","Aelalgrin","Aelanwan","Aeri","Afaesean","Afaol","Afe","Afeiw","Afera","Aferatlan","Afigowyr","Afinn","Afyli","Agraletrem","Agrardon","Agray","Agraywyr","Agreal","Agrerramond","Agried","Agrili","Agriowan","Agrirach","Agrirelin","Agriretha","Agroinidd","Agrymond","Aianidd","Aililath","Airaron","Alaebard","Alaennor","Alalimos","Alaocred","Alareth","Alilamar","Aloewin","Aloictred","Alylath","Alytlan","Aoann","Aoredric","Aosean","Aralinn","Aralinwan","Araomma","Arealgrin","Areder","Areractred","Arianyth","Arigonnor","Ariramond","Arirap","Aroanydd","Aroretha","Asalebaen","Asalewan","Asaubwyn","Asealin","Aselald","Aseli","Asiaron","Asienydd","Asioctred","Asiomond","Asirat","Asirawyth","Asoedan","Astalelgrin","Astalidric","Astaog","Astaymos","Astayran","Asteath","Astelat","Astelilin","Asteliv","Astiamar","Astirebwyn","Asytlan","Auth","Bardomond","Be","Beder","Belaldric","Belav","Belildan","Benda","Bilig","Boaw","Boedus","Boibaen","Boredric","Bralew","Braowyr","Bredus","Breildric","Breird","Breiwyr","Breli","Brelildric","Brelip","Breliran","Broeand","Broreldan","Cadaeseth","Cadalecon","Cadan","Cadauw","Cadean","Cadendamond","Cader","Cadera","Caderra","Cadierd","Cadilavudd","Cadionnon","Cadoedan","Cadoel","Cadoi","Cadorenad","Caeld","Caemos","Caeron","Caledus","Calis","Caloth","Cao","Caomas","Carewin","Caybaen","Caywyr","Ceaand","Ceav","Celabwyn","Celan","Celatlan","Celavudd","Celican","Celicon","Cendawyr","Cerilin","Chaleldric","Chalic","Chao","Chayd","Chealgrin","Chera","Cheratram","Cheriwan","Cherra","Cherraldan","Chew","Chigomar","Chinad","Chiomma","Chirali","Chop","Ci","Cie","Cietha","Cigogord","Cigowan","Cilig","Cilinn","Ciliv","Cio","Cioth","Ciraf","Cirelgrin","Cireloth","Ciwin","Coa","Coav","Coinad","Crales","Cralinidd","Crelilith","Creravudd","Crerracred","Cria","Crirebard","Crirevudd","Cro","Croanwan","Croeld","Croetram","Culdric","Cyloth","Cyr","Cyseth","Daenad","Daleli","Dali","Daligan","Daret","Deaf","Deamma","Deiwyn","Delawyn","Dendard","Dendatha","Deram","Diaa","Diet","Dilav","Doannor","Doelith","Doew","Drag","Drale","Dralimma","Dralith","Draogan","Draonnor","Dreiand","Dreratha","Dresh","Drev","Driadric","Drib","Driregan","Driw","Drocon","Druseth","Duw","Duwyn","Dwaw","Dwerali","Dwianyth","Dwiaw","Dwiodan","Dwiotlan","Dwoebwyn","Dwoenwan","Dwytram","Edalider","Edaylith","Edeath","Edelidric","Edenda","Ederinwan","Ediectred","Edigoth","Edildan","Ediotram","Ediramma","Edoebwyn","Edoeld","Edy","Edynnon","Elalit","Elardod","Elaynydd","Elea","Eleabaen","Eleild","Eleladus","Eleramas","Elerir","Eliannor","Eligoldan","Elios","Eliracon","Elorelgrin","Eluch","Eludus","Ely","Eowaemos","Eowaew","Eowardonydd","Eowarenydd","Eowaubard","Eowenad","Eowerinyth","Eowerrat","Eowieldric","Eowiemma","Eowilimas","Eowirald","Eowirawyn","Eowiwyr","Eowoith","Eowuc","Eowudon","Eowydfrid","Eowynn","Eradon","Eramond","Eraotha","Eraynnor","Ereanidd","Ereasean","Ererracred","Erewyth","Erigomar","Erilitrem","Erirann","Eriref","Eroali","Eroil","Eroitrem","Erosean","Etae","Ethaodan","Ethardob","Ethaydan","Etheaw","Etheawyth","Ethelicon","Ethie","Ethiecan","Ethios","Ethoamar","Etilgrin","Etirewin","Etoret","Faenydd","Faremas","Felimos","Fem","Fendar","Figowyn","Filiwyn","Fiotha","Firamos","Firannor","Foemas","Frare","Frawyn","Freinnon","Frerrabard","Frerrannon","Frilam","Friredfrid","Froewyr","Frowyr","Frydus","Fumma","Galalinn","Galardo","Galardobard","Galardoctred","Galeadric","Galeannon","Galerald","Galilanydd","Galilap","Galild","Galiowin","Galiralith","Galo","Galoegord","Galylath","Ge","Gelitram","Genn","Gera","Geradon","Gie","Gie","Giem","Glaewyr","Glalevudd","Glawyr","Glea","Glealoth","Gleliv","Gleramas","Gleriwin","Gliawin","Glinnon","Glioa","Glioli","Gliran","Glird","Gliregan","Gloremma","Glorewyn","Grardomos","Grayc","Graydfrid","Gredric","Grelictred","Grelidfrid","Grelinnor","Grendatlan","Greralath","Grialdan","Griw","Grog","Groilath","Grorech","Grorenidd","Grytram","Gwaemond","Gwaewan","Gweitram","Gweliwin","Gwenda","Gwigonn","Gwililgrin","Gwoennon","Gwydaew","Gwydalend","Gwydardord","Gwydeadan","Gwydelivudd","Gwydeliwyr","Gwyderraseth","Gwydieloth","Gwydiland","Gwydilitlan","Gwydiliwyr","Gwydoec","Gwydore","Gwydorem","Gwydyseth","Gywyn","Haa","Haaenwan","Haalebwyn","Haaonad","Haardoch","Haare","Haarecon","Haath","Haeabaen","Haelann","Haeraldric","Haerictred","Haerracon","Hailader","Hailar","Hairagord","Hairamar","Haith","Hale","Haoaloth","Haoaran","Haoeder","Harecan","Hay","Hayand","Haydan","Heric","Heridus","Herind","Hiecan","Hirawyn","Hoagan","Ibaegord","Ibardomas","Ibea","Ibeiv","Ibelabaen","Ibelith","Ibire","Ibiredus","Iboard","Iboiwin","Ibosh","Ibubard","Ibunidd","Jeraef","Jeraonwan","Jerardocan","Jerardoder","Jerare","Jerareder","Jerayder","Jerayloth","Jererrap","Jeriratrem","Jeriwyr","Jeroebard","Jerunydd","Kaaledfrid","Kaalewin","Kaalit","Kaarew","Kaayli","Kaeannon","Kaeilgrin","Kaeinad","Kaeli","Kaendaron","Kaeraldric","Kaerip","Kai","Kaie","Kailactred","Kalilith","Kaolath","Kauld","Kedaenad","Kedalev","Kedaoch","Kedaold","Kedauld","Kede","Kederagan","Kederrad","Kedilab","Kedilabwyn","Kediraldric","Kediralith","Kediratlan","Kedith","Kedoesh","Kedoicred","Kedon","Kedore","Kelith","Kerilath","Kerrald","Kiragan","Koregan","Kytha","Laep","Lalemma","Lalinydd","Laraeld","Laraletha","Laraoldric","Lararenydd","Laraudric","Lardomma","Lareli","Laremar","Larerrac","Larerradon","Larigowyn","Lariratrem","Laubard","Leat","Legalitlan","Legealoth","Legeawyn","Legelimos","Legeraand","Legigogan","Legilanyth","Legoitlan","Legorecan","Leguand","Lelaldan","Leli","Lerin","Liab","Lier","Loetrem","Loibaen","Lorebard","Lothali","Lothardocred","Lothareran","Lotharetrem","Lotheald","Lotheind","Lothendamar","Lothendawin","Lothiader","Lothigosean","Lothoadfrid","Lothoremond","Man","Maotrem","Mardomas","Mauch","Maut","Meam","Meath","Melard","Merasean","Merili","Merrawyr","Mewin","Mianidd","Miraedric","Miralelath","Miralimos","Mirawan","Mirayv","Mireactred","Mireann","Mireath","Mireawyth","Mirelaldric","Mireloth","Mirerish","Mirianyth","Mirilich","Mirirawin","Miroimas","Mivudd","Moildric","Naelin","Nale","Nardo","Naunydd","Neand","Neraseth","Niaron","Niewyn","Nila","Nilaf","Nilawyr","Nilildric","Nio","Noican","Noilith","Nydaliloth","Nydalis","Nydaynyth","Nydeamma","Nydeawin","Nydelanydd","Nyderibwyn","Nyderra","Nydia","Nydilad","Nydira","Nydo","Nydoard","Nydorevudd","Nyth","Nyvudd","Oca","Ocaolath","Ociradric","Ocoacon","Ocoig","Ocoish","Ocoiwyr","Olaennon","Olaer","Olalinydd","Olarelgrin","Olauwyr","Oleadric","Olealith","Olelird","Oleralin","Oligocred","Olilath","Onalath","Onaodric","Onelath","Onenwan","Oniannon","Onimond","Onirad","Oniraf","Oniratrem","Onirenad","Onoaldric","Onoea","Paennor","Pali","Palider","Pardold","Paredric","Peawin","Peican","Pilidan","Piol","Poali","Praeldric","Prale","Praotrem","Prauctred","Prea","Prerrald","Prigomos","Prilav","Prilawyn","Prili","Proadan","Proar","Proewyr","Pryvudd","Puctred","Raaemma","Raalemma","Raaylin","Raea","Raia","Railibaen","Ralenydd","Raoawyn","Raoenad","Reimos","Rend","Rendaa","Reramond","Rha","Rhaef","Rhaenwan","Rhaenydd","Rhaerd","Rhaewyth","Rhard","Rharend","Rharetha","Rhelawyth","Rhendaf","Rheraldan","Rherigan","Rhidus","Rhigoldric","Rhilildric","Rhio","Rhira","Rhirabaen","Rhirac","Rhiradan","Rhiradfrid","Rhirewin","Rhoetlan","Rhubard","Rhusean","Rhys","Rimas","Rirath","Rire","Rire","Rot","Saetha","Saligord","Salir","Saoldan","Saylgrin","Seanad","Seitlan","Selidus","Selilith","Seragan","Sevalenwan","Sevaotram","Sevaowyn","Sevardod","Sevaref","Seveach","Sevelatlan","Sevelawyth","Seven","Severabwyn","Severranidd","Seviotrem","Seviregord","Seviremond","Sevyldric","Sevys","Silanidd","Sinnon","Sior","Sira","Sirabard","Siratram","Sirawin","Sireld","Skadfrid","Skalibard","Skalinydd","Skardo","Skeasean","Skelar","Skelit","Skeramos","Skeriseth","Skerrali","Skilacan","Skio","Skirecon","Skoetram","Skybaen","Skyd","Soreb","Soredric","Tadan","Tael","Te","Tedon","Tela","Terald","Teraron","Thae","Thaegord","Thaemas","Thaleseth","Thalewan","Thaliand","Thalibaen","Thalir","Thanyth","Thauch","Thayldric","Theacred","Theal","Thealith","Thei","Thelalith","Theli","Thelip","Thendasean","Thilird","Thiliwyn","Thiold","Thirabaen","Thiret","Thirewyn","Thoe","Thoewin","Thoind","Thoredfrid","Thudfrid","Tili","Tinnor","Tiren","Toewyn","Toild","Traend","Trao","Traog","Trareg","Traremos","Traugan","Treas","Treisean","Trigow","Trigowyth","Trira","Troav","Troewyn","Vaeld","Valemma","Valig","Vaovudd","Vaytha","Veawyn","Veiwyn","Velilgrin","Velimas","Vemma","Vennor","Verawin","Verraand","Verratlan","Viab","Viabaen","Viremond","Voreron","Vuld","Waledric","Waomar","Waus","Wautrem","Wegord","Weig","Welamar","Welid","Werivudd","Werradfrid","Wiatrem","Wicare","Wicauwyn","Wiceawin","Wiceawin","Wicelat","Wicera","Wiceractred","Wiceri","Wici","Wicimos","Wicoa","Wicoilith","Wicuth","Wilacred","Wilildric","Wilinnon","Wind","Wirer","Wiresean","Woanidd","Woann","Woe","Woeloth","Woetrem","Woildan","Wuwyr","Wyli","Yaemond","Yalictred","Yaotha","Yardonidd","Yardovudd","Yays","Ybaemar","Ybarerd","Ybauctred","Ybauwyr","Ybearon","Ybecred","Ybeidon","Ybeli","Ybendaa","Yberaron","Ybia","Ybiat","Ybienydd","Ybilalath","Ybilinnon","Yboaw","Ybolgrin","Ybya","Yeald","Yeas","Yelagord","Yeradon","Yiadus","Yio","Yiodus","Yoctred","Yoider","Yulith","Zaretram","Zayc","Zeid","Zeiw","Zeraron","Ziaand","Ziamond","Zie","Zinad","Zinn","Zireth","Zoaloth","Zoinad","Aalegan","Aaoldan","Aayth","Ababwyn","Abaedfrid","Abareloth","Abarewyr","Abauron","Abawan","Abaycan","Abendatha","Aberiw","Abiratrem","Abire","Aboilgrin","Abyn","Acaes","Acarelith","Acarewyn","Acauli","Aciliwyn","Adaowin","Adayn","Adealgrin","Aderider","Aderimond","Adet","Adielith","Adigonwan","Adira","Adoar","Adodus","Adoedfrid","Adoinwan","Adoiwyn","Adorebard","Adraliwin","Adrarenydd","Adrelinnon","Adreliwyr","Adricon","Adrios","Adriradon","Adrirebaen","Adroa","Adroatram","Adrold","Adwaemar","Adwaoth","Adwar","Adwarebard","Adwau","Adweald","Adweamas","Adwela","Adwerralith","Adwiabaen","Adwiliwyth","Adwiold","Adwiracan","Adwoimond","Aelib","Aelild","Aendard","Aerimar","Aerrabaen","Aewan","Afaeran","Afalic","Afauwyn","Afenidd","Aferradon","Aferrath","Afie","Afiewan","Afiliwyn","Afiowin","Afirald","Afireldan","Afoemar","Agraedan","Agralewyr","Agralican","Agraosean","Agrardos","Agrardowin","Agreimma","Agreitha","Agrendaldan","Agrera","Agreragan","Agrigog","Agriracon","Agriramar","Agroam","Agroenwan","Agror","Aiewin","Ailiw","Airewyr","Alaliwyth","Alaomond","Alardonnon","Alarew","Alath","Alaycon","Alaym","Alelaron","Alendabard","Alilard","Alorenydd","Alowyn","Aoar","Araewyn","Arardotlan","Areann","Arigodric","Ariowyn","Aroa","Aroewin","Aronad","Arutrem","Asaleldan","Asaseth","Aseactred","Aseicred","Asendamos","Aserav","Asiemas","Asiev","Asiewin","Asoeseth","Astaer","Astaesh","Astaynidd","Astea","Astela","Astendaw","Astig","Astilit","Astiolath","Astiranydd","Astirawyr","Astiremma","Astitrem","Astoagan","Astoend","Astow","Asyron","Ayctred","Balemar","Balend","Baudus","Baugan","Beabaen","Beird","Belader","Belawyr","Bendawyn","Biawyn","Bied","Bionnon","Birali","Birewyn","Birewyth","Boanwan","Brali","Braobwyn","Brardomma","Brauth","Brauwin","Breilath","Brerraloth","Brider","Briomond","Briraand","Brirabwyn","Broedfrid","Brumma","Bryran","Cadalenad","Cadaur","Cadeab","Cadia","Cadiar","Cadilap","Cadilip","Cadiotrem","Cadiretram","Cadoan","Caegord","Caer","Cale","Calenyth","Caold","Caonnor","Caonyth","Caoron","Cardogord","Cardolgrin","Caydfrid","Cayli","Caysean","Ceamond","Cech","Ceith","Celaldric","Celild","Celild","Celinyth","Ceranad","Ceriv","Chaleld","Chalider","Chauldric","Chaywyr","Chenyth","Chiet","Chif","Chulath","Chuld","Ciali","Ciann","Ciewyth","Cigolgrin","Cilin","Cilin","Cilisean","Cilitlan","Coadfrid","Coag","Coish","Cores","Craon","Crarewyn","Craua","Craup","Creand","Crearan","Creath","Crebaen","Crendabard","Criladan","Crilamond","Crilanidd","Crilawyr","Crilir","Crirali","Crirann","Crirennon","Criretlan","Crirewyn","Croia","Cromos","Cry","Daebwyn","Daetha","Daleb","Darea","Dendactred","Dendawin","Digolith","Dinnor","Dira","Diradon","Diralgrin","Diramma","Dirawyn","Doaw","Draewyr","Dre","Dreamos","Drelamas","Drelin","Drendawin","Dreraa","Drerracred","Drilig","Driragord","Droalith","Droamar","Droisean","Drorelin","Duldric","Dwaemar","Dwalinnor","Dwalish","Dwardoder","Dwat","Dwealdan","Dweliron","Dwilildric","Dwoimas","Dworenyth","Dwudon","Dwuron","Dwymar","Dwymos","Edaemas","Edaenwan","Edalenad","Edardotram","Edardowan","Edarennor","Edarenydd","Ederaloth","Ederrath","Edinyth","Ediradric","Edoat","Edodan","Edoeldric","Edore","Edyg","Elaenad","Elalinnon","Elaretlan","Elau","Elaumar","Elauwyr","Eleanad","Eleavudd","Eleavudd","Elelic","Elelicon","Eli","Elin","Elioder","Elirabard","Elirer","Eloasean","Eloawyth","Elucan","Elyand","Elylgrin","Eowalimma","Eowalir","Eowardoder","Eoweabard","Eoweagord","Eowigold","Eowigos","Eowigotram","Eowoatrem","Eowynyth","Erae","Erae","Eraewan","Erales","Erardodric","Erarew","Ereath","Ereiwyr","Eroev","Erumos","Erysh","Etalilith","Etea","Etealath","Eteamar","Eteladric","Etendand","Eterralgrin","Ethali","Ethalimma","Ethardot","Ethardowin","Ethaudfrid","Ethendann","Etherraldric","Ethiamma","Ethiavudd","Ethigodon","Ethilimas","Ethire","Etiecan","Etielin","Etigo","Etirard","Etoat","Etoe","Etoith","Faeldric","Faeldric","Faeli","Fauron","Fauth","Fayctred","Feisean","Felidan","Fendacon","Fendactred","Fia","Fierd","Firaran","Firash","Fore","Fraegord","Fraeth","Frald","Frardomar","Frardowyn","Frarea","Frau","Freab","Freiwin","Frelibard","Friebwyn","Friewyn","Frigocan","Friralgrin","Frirawyn","Friwyn","Frorew","Frovudd","Fyc","Galali","Galaliwan","Galaobaen","Galaumas","Galelat","Galelawyth","Galilamar","Galith","Galoatram","Galolgrin","Galotrem","Galuldric","Galynnon","Gaonnor","Gausean","Gayran","Gea","Geald","Geic","Gelalith","Gelan","Gelawyth","Gendasean","Geriwyn","Gerrar","Ges","Giaran","Gilib","Giliran","Giralath","Glalel","Glaolgrin","Glaremar","Glaron","Glayb","Gleald","Gleinn","Glerradfrid","Glirel","Glireli","Gloan","Globwyn","Gloedric","Gloretha","Glytram","Gobwyn","Graeloth","Grardold","Grare","Graretram","Graylgrin","Grayr","Grendaron","Grietram","Grigo","Griocon","Grioth","Groreron","Gubard","Guder","Gunydd","Gwalith","Gwao","Gwareron","Gwealin","Gweannor","Gweat","Gwer","Gwerimos","Gwet","Gwiedan","Gwirewyn","Gworebwyn","Gwydardobard","Gwydardoran","Gwydaumos","Gwydeigord","Gwydeimas","Gwydeliron","Gwydilatram","Gwydoadric","Gwydoer","Gwydorenidd","Gwydurd","Haaowyr","Haaretrem","Haendar","Haerawyth","Haerramma","Haew","Haigov","Haiogan","Haoadon","Haodric","Haolith","Haud","Helacon","Helatha","Heliwin","Hennon","Heran","Hig","Hiladan","Hoar","Hoe","Hybard","Ibae","Ibaerd","Ibalimas","Ibaobard","Ibaold","Ibaond","Ibarerd","Ibaudric","Ibauvudd","Iberatlan","Iberiwin","Ibetlan","Ibield","Iborennon","Ibosh","Ibuldric","Ibunnor","Jera","Jeraetlan","Jerendaw","Jereranyth","Jererrabard","Jererrath","Jeria","Jeroand","Jeroregan","Kaalidus","Kaalinwan","Kaaotha","Kaeliloth","Kaes","Kaia","Kaiabwyn","Kaie","Kaigobard","Kailab","Kailas","Kailia","Kalerd","Kaoawyn","Kares","Keabwyn","Keanyth","Kedaeb","Kedaennor","Kedalend","Kedaor","Kedardosean","Kedaredan","Kedeand","Kedeavudd","Kedeig","Kedelagan","Kedeliwyn","Kedidan","Kerractred","Kerrald","Kewyr","Ki","Kialgrin","Kigowin","Kiow","Kirebwyn","Kirerd","Koa","Koibwyn","Kore","Kycon","Kyron","Laech","Laes","Larardon","Larerilath","Larerimma","Larerraldan","Laretram","Lari","Lariald","Larilaldan","Larilican","Lariraa","Laroab","Lauf","Laug","Leagan","Leas","Legabaen","Legaecred","Legaesean","Legalath","Legauldric","Legayb","Legelash","Legeradon","Legeriloth","Legerracon","Legerrannor","Legildric","Legioloth","Legirard","Legirawin","Legirawin","Legoetha","Legoreloth","Leli","Lelib","Lerannor","Lerranidd","Lilach","Lirew","Lothaer","Lothalild","Lotharec","Lothaydus","Lothenda","Lotherranidd","Lothidfrid","Lothigord","Lothiladfrid","Lothira","Lothoadfrid","Lothuwan","Maemos","Maenydd","Mayand","Mayp","Melitha","Mia","Miawyr","Miewan","Migotha","Miovudd","Miraectred","Miraledan","Miraliwyth","Mirardoand","Mirea","Mireildric","Mirelitram","Mirendamond","Mireral","Mirerradric","Mirigodric","Mirigogord","Miriowyn","Miriras","Mirirawin","Miriv","Miroaron","Miroemar","Miroider","Moar","Moi","Moredric","Na","Naowyn","Nardoa","Nas","Nawyn","Naynyth","Nendader","Neralin","Newin","Nigonyth","Noreand","Nowyr","Nydaem","Nydaup","Nydeatrem","Nydeavudd","Nydeawin","Nydendad","Nyderir","Nyderrabard","Nydiamar","Nydiawyr","Nydigon","Nydiosh","Nydiradfrid","Nydiratlan","Nydore","Nydu","Nydunydd","Nydus","Ocaeth","Ocaewan","Ocalinidd","Ocelitram","Ocerabaen","Ocerra","Ociader","Ocield","Ocigomar","Ocilavudd","Ociocan","Ociomas","Ocireloth","Ococ","Ocoiwan","Ocoremas","Olaewin","Olald","Olardo","Olasean","Olawan","Olelaand","Olelamas","Olenda","Olielith","Olievudd","Oliewyn","Olililith","Olira","Oliram","Olirav","Olireloth","Onaeld","Onaliwyn","Onautha","Onaytlan","Onaywin","Oneath","Onigodon","Oniremma","Onirewyn","Onoebwyn","Onoewan","Onud","Onunnon","Paowyth","Pau","Pean","Peanwan","Pelisean","Piavudd","Pilalith","Pionad","Pirabaen","Pirawin","Pralimma","Prardovudd","Praunwan","Praydan","Preagan","Prendap","Prerrannor","Prerratlan","Priamond","Prianydd","Priawyr","Prilatlan","Proep","Prorennor","Prorer","Prumma","Puran","Raadan","Raaunad","Raeld","Raelidric","Raeseth","Raiader","Raieand","Raio","Raionidd","Rairagan","Raoadfrid","Rauldric","Rauth","Rerind","Reriw","Rhag","Rhalewyn","Rhaowyr","Rhardow","Rhayld","Rheawyn","Rheip","Rherawin","Rherildan","Rhiaran","Rhira","Rhoavudd","Rhoawyr","Rhuld","Rhuwin","Riawan","Rigoseth","Rilawyth","Riomma","Rirabwyn","Roregord","Saonyth","Seladus","Selannon","Selgrin","Serictred","Sevae","Sevenda","Severamos","Severas","Sevibwyn","Sevilidfrid","Sevioa","Sevub","Sevuld","Siawyr","Sief","Silawan","Sirann","Skaoldric","Skardold","Skare","Skareran","Skeadan","Skeradon","Skerinn","Skeriwyr","Skiach","Skiec","Skigodon","Skilac","Skilimar","Skilind","Skiomond","Skirand","Skireseth","Skuldan","Skynnor","Skynnor","Soatrem","Soeron","Soimar","Soimma","Synnon","Tareld","Tarer","Tela","Tendactred","Teridan","Thale","Thalimar","Thalinnor","Thardonn","Theidfrid","Them","Theraldric","Therd","Theritlan","Therrar","Thia","Thireloth","Thireloth","Thirennon","Thoiseth","Thoiseth","Thu","Tia","Tilas","Tire","Toat","Toawyn","Toew","Toi","Toic","Toron","Traebaen","Traecan","Tralenydd","Tralind","Trareron","Treanydd","Trelach","Treladus","Trelatha","Trendacon","Trendadon","Treraran","Trerrawan","Triawyn","Trimar","Triranwan","Truld","Tunydd","Tut","Vae","Vaef","Vaenwan","Vaog","Vath","Vaygord","Vayldric","Veann","Veat","Veip","Verild","Vilinnon","Vuli","Vydfrid","Waecred","Waecred","Waeloth","Waeseth","Walebaen","Walil","Warelgrin","Wayth","Wayth","Weadric","Weid","Weiran","Welatha","Wendanydd","Wendas","Weradon","Weranad","Werird","Werramar","Werran","Werrannon","Wetrem","Wewan","Wicae","Wicaemos","Wicalic","Wiceath","Wicialdric","Wicilaldric","Wicionnon","Wicoibard","Wicoreth","Wigomos","Wio","Wiop","Wira","Wiras","Wirawyr","Wiredus","Woadfrid","Woash","Wocan","Wuld","Wuwan","Yalimas","Yardoran","Yareder","Yaremond","Yauch","Yaunad","Yay","Yban","Ybardowyr","Ybaunyth","Ybeash","Ybeliran","Ybendalgrin","Yberildan","Yberratha","Ybilawyth","Ybiregan","Yboanyth","Yboevudd","Yboin","Yeacred","Yeaseth","Yeiran","Yetha","Yinn","Yoannon","Yoenidd","Zaetram","Zardo","Zaudon","Zeawan","Zelidon","Zerith","Zorew","Aadus","Aaebard","Aalesean","Aaytha","Abalenyth","Abamar","Abardoloth","Abeadan","Abeawyth","Abeladan","Abendab","Aberradus","Abiath","Abieli","Abienad","Abigor","Abilimma","Abiliwyr","Abiratlan","Aboed","Abond","Aborelin","Abu","Acaedus","Acaletram","Acaliloth","Aceactred","Aceadan","Aceadon","Acelatram","Aceldric","Acenydd","Acerish","Acerra","Aciramar","Aciran","Acoeldan","Acorectred","Acored","Acuch","Acumma","Adaef","Adaemar","Adaer","Adaw","Adeiran","Aderralgrin","Adiawin","Adind","Adiretram","Adraleseth","Adreli","Adrilibard","Adriranidd","Adroa","Adroali","Adroiwyn","Adrorenydd","Adwaerd","Adwaeron","Adwalet","Adwaligord","Adwalitram","Adwaocred","Adwardoa","Adwardod","Adwardosean","Adweabwyn","Adweia","Adwenda","Adwerath","Adwioldric","Adwiowyth","Adwiralith","Adwiref","Adwirend","Adworelin","Adwynidd","Aeidfrid","Aeild","Aelalath","Aelavudd","Aendaloth","Aerrann","Afalennor","Afardo","Afardowyr","Afatram","Afauran","Afay","Afeap","Afeatlan","Afebard","Afeidus","Afeliand","Aferash","Aferradan","Afienn","Afieth","Afyr","Agraedric","Agrardop","Agraytlan","Agream","Agrec","Agredan","Agrelaa","Agrerrag","Agrilabwyn","Agroelith","Aimma","Airanad","Alalith","Alei","Alelidus","Aleliw","Alendav","Aleri","Alilaseth","Alildan","Aliotha","Aliraseth","Alirat","Alyth","Aoildan","Araem","Araeth","Araetram","Aralebaen","Aralibwyn","Arealin","Areidfrid","Arelaa","Arendam","Areri","Ariadfrid","Arilalath","Arilich","Arios","Arirash","Ariraw","Aroa","Aroewyr","Aroremond","Asauldric","Asei","Aseitlan","Aselitlan","Aselivudd","Asendagord","Asialgrin","Asicred","Asilard","Astaeloth","Astaenad","Astalecon","Astalidon","Astardodon","Astaretha","Astaunad","Asterich","Asterigan","Astirader","Astiran","Aua","Auch","Bardo","Barenwan","Barenydd","Beinnon","Belamos","Belilin","Belinwan","Benda","Bendash","Berrasean","Bianyth","Bigo","Bigomas","Bila","Biredan","Bireseth","Boa","Boremas","Boreth","Braucan","Brecred","Brelagan","Brendash","Brerawyr","Briralith","Briranydd","Buli","Bunn","Cactred","Cadaea","Cadalegan","Cadalith","Cadalitrem","Cadaumos","Cadaygord","Cadeat","Cadegord","Caderimar","Cadiawyth","Cadiotha","Cadirenidd","Cadoa","Caemar","Caemar","Cale","Caliand","Caliron","Cardoc","Caremas","Cayld","Cayp","Cayth","Cei","Cei","Ceidfrid","Celamma","Celatrem","Celimma","Cendard","Ceric","Cerracred","Chardodon","Charer","Cheald","Cheanydd","Cheawin","Cheldan","Chelimar","Chelip","Cherip","Cherrann","Chilawin","Chirawyn","Choa","Cie","Cigodfrid","Ciladon","Cilidan","Cirad","Cire","Ciwyn","Coamos","Coicon","Coiron","Coreg","Coreldan","Craegan","Crardoli","Crelam","Crelilith","Crerinad","Crerivudd","Cri","Crianwan","Crieand","Crilath","Criratha","Critram","Crum","Crunad","Crush","Cycred","Daeldric","Daledric","Dalenwan","Dardoth","Dea","Deap","Delacred","Delilith","Dendaa","Dendaf","Deranwan","Dian","Dilawin","Dili","Diranydd","Draeb","Draretram","Draugan","Drela","Drendawan","Dreran","Dreri","Driadfrid","Driomas","Drior","Driwan","Droamas","Dwabaen","Dwaedus","Dwaoli","Dweanyth","Dwedon","Dwelilith","Dwi","Dwilir","Dwirawan","Dwoesh","Dwoish","Edaewin","Edaldan","Edare","Edeap","Edelasean","Edendath","Ederrawyr","Edieder","Edienydd","Edioldric","Edirennor","Editha","Edoali","Edonad","Edubard","Edyand","Elaeb","Elaocan","Eleavudd","Elerildan","Eliemos","Eloitrem","Elysean","Eowaod","Eowardog","Eowaua","Eoweanyth","Eoweri","Eoweridfrid","Eoweriv","Eowif","Eowilactred","Eowilaseth","Eowili","Eowilis","Eowiowyn","Eowiratrem","Eowuth","Eraeron","Eralican","Erardonn","Erauc","Ererawan","Erigodus","Erilidan","Eriraa","Eroa","Etaerd","Etagord","Eteat","Etendat","Ethardodon","Ethea","Ethendatrem","Etherap","Ethilanad","Ethiland","Ethom","Ethorenad","Ethywyn","Etoann","Etoetrem","Etu","Etya","Etywyr","Faeth","Falewyr","Faold","Faumond","Faunydd","Ferith","Firamas","Firesean","Foabwyn","Fodric","Fraomond","Frard","Frayl","Fraylgrin","Fraytha","Freamond","Freand","Frerath","Friragan","Froilith","Frorea","Galaedric","Galalider","Galalir","Galalisean","Galea","Galeadus","Galenda","Galendald","Galerash","Galeratrem","Gali","Galireloth","Galoaand","Galoctred","Galoiwin","Galywyn","Gao","Garenn","Gaycan","Gaych","Gieth","Gigowin","Glamma","Glaot","Glaw","Glawyr","Glaytram","Gliand","Glilidon","Glilif","Glirecred","Gloenidd","Goresh","Gralend","Greagord","Grendap","Grerif","Grienyth","Griodan","Grirewyn","Groar","Groerd","Gryv","Gwadan","Gwaem","Gwalewyr","Gwayp","Gwelas","Gwendannon","Gwendasean","Gwerradfrid","Gwieli","Gwilash","Gwilin","Gwiomar","Gwiraand","Gwydabwyn","Gwydaeldan","Gwydardo","Gwydarennor","Gwydau","Gwydaylath","Gwydendaldan","Gwydia","Gwydiennor","Gwydiovudd","Gwydiraloth","Gwydiras","Gwydireli","Gwydoildan","Gwydoreldan","Gwydy","Gytlan","Haeann","Haendawyr","Haidan","Haionidd","Hairabwyn","Halimond","Haodan","Haoel","Haom","Hauth","Heanidd","Heath","Heilath","Hibard","Hidan","Hief","Ibaudfrid","Ibavudd","Ibayth","Ibea","Ibeamma","Ibeawyr","Iberi","Iberra","Ibilamas","Ibiond","Jeraemma","Jeraleloth","Jerauseth","Jeraygan","Jereader","Jerelacon","Jerelagan","Jereribaen","Jeriamas","Jerigoc","Jerilamas","Jerioldan","Jerire","Jeriseth","Jeroreand","Kaalimma","Kaarerd","Kae","Kae","Kaeidus","Kaeseth","Kaewyth","Kaidan","Kaiecred","Kaiosean","Kaira","Kali","Kaoic","Kaosean","Karedus","Kaynidd","Kea","Kedaetrem","Kedareld","Kedareldric","Kedarelgrin","Kedead","Kedearon","Kedeawyn","Kedeigan","Kedeith","Kedendatrem","Kedendawyth","Kedieron","Kedieth","Kedigonyth","Kedilanidd","Kediramar","Kedowyth","Kedym","Kedynnon","Kelaand","Kendabaen","Kendadan","Kendamar","Kendanad","Kerivudd","Kiland","Kiloth","Kiramma","Lald","Lalid","Lanad","Larea","Lareanwan","Larearon","Laremas","Larendalith","Larendamas","Lareramma","Larerimond","Lareriron","Lariv","Laroith","Laroldan","Larored","Lauw","Leadon","Leap","Legalem","Legaowin","Legardon","Legardonnor","Legeild","Legendawyn","Legerann","Legiedon","Legigotha","Legilatlan","Legiord","Legirebard","Legoaran","Legoredfrid","Legorewyn","Leinydd","Leriron","Liea","Lig","Lilidon","Lirelath","Lo","Loach","Loitrem","Loremar","Lothasean","Lothealgrin","Lothearan","Lothectred","Lothelatrem","Lothendad","Lotherinyth","Lothilalgrin","Lothiolath","Lothirenn","Lothoali","Lothomma","Lothorenn","Lur","Luth","Lyg","Malenyth","Malildan","Maos","Maow","Merrar","Mieron","Milili","Miobwyn","Miracred","Mirae","Miraemond","Miralewyth","Mirali","Mirard","Mirarewan","Mirawyth","Mireagan","Mireawyn","Mireawyn","Mireican","Mirerabwyn","Mireraran","Mirerild","Miretha","Mirigoc","Mirilawan","Miriot","Miriragord","Miruran","Mirydfrid","Moea","More","Morel","Naedan","Naemar","Naon","Naydan","Neatlan","Nelawin","Nelith","Nendal","Nerrar","Nerrawyr","Niebard","Nienn","Nirannor","No","Nulgrin","Nus","Nydardomma","Nydaul","Nyday","Nyderatram","Nyderradfrid","Nyderragan","Nydewyn","Nydien","Nydilat","Nydilider","Nydiratram","Nydoldric","Nyductred","Nywan","Ocaemos","Ocaenidd","Ocalin","Ocerath","Ocerrabard","Ocerradon","Ocili","Ocira","Ocirebard","Ocoabaen","Ocoren","Ocoretrem","Ocotha","Olacred","Olaelin","Olaewyn","Olalegord","Olareli","Oleadon","Oleliwyn","Oleritram","Oliabard","Olieand","Oligogan","Oliladon","Olilig","Olilith","Oliralith","Oluth","Onauth","Onayf","Onelard","Onelibaen","Onireb","Onith","Onosh","Paenwan","Paliloth","Paolin","Parenyth","Paumma","Pe","Pea","Pei","Pelilgrin","Perac","Peramar","Peramos","Perrawan","Pieran","Pinydd","Piomos","Pirannor","Piwin","Porenidd","Praer","Pramma","Prao","Preath","Prela","Prendawin","Preramos","Preran","Prerra","Priali","Priep","Prind","Priral","Proia","Proic","Pytlan","Raaldan","Raalimma","Raarenn","Raeinidd","Raeitlan","Raelinn","Raeri","Raerictred","Raerraand","Raili","Raond","Rardotrem","Rardowin","Rarebwyn","Rarep","Rauldric","Raumos","Raunydd","Reib","Renda","Rendalgrin","Reradus","Rerid","Rerrawin","Rhardowyn","Rheamar","Rheanyth","Rhemos","Rhendap","Rhianyth","Rhieldric","Rhif","Rhigowyr","Rictred","Rid","Riebard","Rigo","Rilidric","Riowin","Roemas","Runad","Rywyn","Salimas","Sardo","Saus","Saysh","Saywin","Seldric","Selildan","Serrabard","Sevaunwan","Sevendam","Sevenwan","Severamond","Seviedon","Sevilaran","Seviold","Sevire","Sevoadric","Sevoanad","Sevoegord","Sigosh","Silith","Sirath","Skaewyn","Skareder","Skaunyth","Skeatrem","Skelimar","Skelinyth","Skerit","Skiac","Skieg","Skilild","Skinydd","Skiovudd","Skoem","Skoitram","Soaron","Soitram","Sonydd","Sylath","Tae","Talew","Talibard","Tarenyth","Teiran","Thaeld","Thalecred","Thao","Thaogord","Theanyth","Thegord","Thelalgrin","Thelamos","Therd","Theribard","Therraa","Therrach","Thiadon","Thianydd","Thieloth","Thilatlan","Thilimas","Thoennon","Thoilin","Thymos","Tiaand","Tirectred","Tirem","Tiwyn","Toeld","Toibwyn","Traeron","Traum","Trauwin","Trauwin","Traytram","Trea","Treiwyn","Trendaldan","Trivudd","Trorend","Trutlan","Tuld","Valin","Vaoth","Vaoth","Vardow","Varewyn","Varewyr","Vea","Vealath","Veibard","Vid","Vienwan","Vigomas","Vilann","Voanidd","Vonnor","Voremas","Wae","Wae","Waeand","Waed","Waesean","Wagan","Waletrem","Was","Weaf","Wean","Weasean","Weimas","Weith","Welaw","Weli","Welidan","Weliwin","Wep","Werat","Weth","Wia","Wicadfrid","Wicalebwyn","Wicaow","Wicaowin","Wicardodan","Wicareloth","Wicaresean","Wicash","Wicaytram","Wiceannor","Wicelider","Wicendadus","Wiceracon","Wicerildric","Wiceriwan","Wicerrawan","Wiciawyn","Wicictred","Wicigowan","Wicilabwyn","Wicin","Wicoadric","Wicoreg","Wiemas","Wies","Wiev","Wiolgrin","Wiowyth","Wira","Wiracon","Wiradan","Wiraron","Wirebwyn","Wirectred","Woadon","Worea","Wudan","Wudric","Wuloth","Wy","Wycan","Wyld","Yaectred","Yaeseth","Yaleth","Yardocred","Yaywyr","Ybalif","Ybaold","Ybarecan","Ybea","Ybelas","Ybendacred","Ybiawyth","Ybigoctred","Ybilanyth","Ybilasean","Ybireand","Ybo","Yeand","Yei","Yelavudd","Yeldric","Yerraf","Yiamar","Yiewyn","Yigomma","Yilanwan","Yiowyth","Yiramos","Yiraron","Yirawyr","Yireder","Yoad","Yoeloth","Yorelgrin","Yu","Yusean","Zaev","Zald","Zardodus","Zardoli","Zardom","Zarewin","Zelald","Zelimma","Zewyn","Zilildan","Zirawan","Zoem","Zoilin","Zoremos","Aalidric","Aap","Aaremma","Aaynydd","Abalemma","Abaomond","Abeder","Abeimond","Abeladfrid","Abelimond","Aberim","Abetha","Abinad","Abiraldric","Aboimas","Abowyn","Acaobaen","Acarebaen","Acela","Acelgrin","Acerawyn","Aces","Aciad","Aciatram","Aciedus","Acier","Acigoth","Aciram","Acird","Acuwyn","Adalitha","Adaumas","Adaywin","Adaywyth","Adeitha","Aderralith","Adigowyn","Adilidan","Adiod","Adiradan","Adoacon","Adoeli","Adorer","Adralennon","Adrare","Adreanyth","Adreash","Adrech","Adrerach","Adrila","Adrilim","Adrilir","Adrirawyr","Adroit","Adrom","Adrores","Adwali","Adwalid","Adwalivudd","Adwalivudd","Adwaunydd","Adwec","Adwetha","Adwiamond","Adwira","Adwiracon","Adwirelin","Adwoild","Adworetrem","Adygan","Aeabwyn","Aebard","Aelacred","Aenda","Afaewan","Afaodon","Afardoli","Afardomond","Afaunyth","Afeadan","Afendadan","Aferratram","Afiebard","Afieth","Afigowan","Afilibard","Afilidfrid","Afoif","Afoip","Agraewyth","Agralewyth","Agraregan","Agraudon","Agraynnon","Agreab","Agrelanad","Agreritlan","Agreriwyn","Agrienad","Agrilanad","Agro","Agroreld","Aidric","Ainydd","Airab","Aired","Alaeth","Alalebwyn","Alalev","Alarewyn","Alecan","Alelanyth","Alendat","Alied","Aligosean","Aligosean","Alilamas","Alilaran","Aloaf","Alore","Alytram","Arae","Araeseth","Areicon","Arendaldric","Arewin","Ariald","Arigomond","Arinnon","Arirenad","Asali","Asaoch","Asaoctred","Asaunad","Asilin","Asoal","Asoemma","Asoitrem","Asorewin","Astaew","Astalith","Asteadus","Asteanydd","Asterrard","Astield","Astigonnor","Astiratram","Astirer","Astoamas","Astoawin","Astoeand","Astorenidd","Ayran","Ba","Baecred","Baubaen","Be","Belalith","Belif","Beliwin","Beridus","Bilal","Bilider","Birabwyn","Biredus","Birelath","Bore","Borelin","Botlan","Braemma","Brale","Brardol","Brardot","Braytha","Brerrac","Brerratlan","Brilawyr","Briramas","Briramos","Briranyth","Buwyth","Cadaenyth","Cadarewyn","Cadaubaen","Cadaumas","Cadaunn","Cadaymas","Cadayron","Cadeadfrid","Caderradan","Cadfrid","Cadidric","Cadyg","Caea","Caelith","Caeron","Caetrem","Caled","Cali","Caogord","Cardoctred","Caurd","Caut","Cay","Ceabaen","Ceal","Ceawyr","Ceder","Ceid","Ceigord","Cendabwyn","Cendag","Cendaseth","Cera","Ceravudd","Ceriron","Cerit","Cerra","Cerragord","Chaecred","Chaeli","Chaund","Chautha","Chayth","Chea","Chearon","Chictred","Chidfrid","Chigonnor","Chiowyr","Chirec","Choren","Chyt","Cic","Ciebard","Ciech","Cigod","Cilach","Ciladfrid","Ciogord","Ciotha","Cip","Cirath","Ciretlan","Coader","Codfrid","Coimas","Cowyth","Crare","Craua","Craysean","Creatram","Crei","Creiand","Crelinyth","Crelis","Crendath","Criab","Criamas","Criovudd","Criradon","Criratrem","Criredus","Cro","Croannor","Cryc","Cug","Cuw","Daewyth","Dale","Deawyn","Dera","Dielin","Dieloth","Dievudd","Dilar","Dirabwyn","Diratha","Doe","Draleder","Draliv","Dreawyn","Dreib","Dreitlan","Drelatha","Dreranyth","Driracan","Drirath","Driratha","Drire","Droemond","Droredan","Drorenwan","Drurd","Duwyr","Dwaemar","Dwaen","Dwaep","Dwaogan","Dwardonnon","Dwarewyr","Dwaulath","Dweawyr","Dweicred","Dwelawyr","Dwerradus","Dwerramond","Dwerran","Dwilaa","Dwilabaen","Dwiom","Dwioth","Dwira","Dydfrid","Edardomma","Edarelgrin","Ederraa","Edesh","Edionyth","Edirab","Edoawan","Edoi","Elaedfrid","Eleramas","Elicred","Elilalin","Elili","Eloawyn","Eluth","Eowalitlan","Eoweannon","Eowelican","Eowerravudd","Eowiawyr","Eowigonnon","Eowoanyth","Eraedan","Eraeron","Ereinn","Ereriwyr","Erionidd","Eroinad","Etalewyn","Eteawan","Eteawin","Etendawyth","Etenydd","Eterigan","Eterind","Ethae","Ethaeli","Ethaemond","Ethaeth","Ethalennon","Ethardodric","Ethaudon","Ethaudus","Etherawin","Ethiennor","Ethienyth","Ethila","Ethioth","Ethirach","Ethirannon","Ethod","Ethoiseth","Ethoivudd","Ethylin","Etibard","Etie","Etigon","Etoith","Etoiwyn","Etoreth","Etovudd","Etuc","Faeldan","Faemond","Falelin","Fardogord","Fauwyth","Faygord","Felatha","Felider","Feracan","Ferraloth","Figoth","Filach","Fililin","Fird","Fireth","Foaf","Fraenn","Fralitlan","Frarenydd","Freadfrid","Freatrem","Freramos","Frerrald","Friov","Friwin","Froalin","Froebard","Froild","Froit","Frorem","Froremma","Frytrem","Galaret","Galeat","Galelalgrin","Galeliwyth","Galendalath","Galetha","Galic","Galican","Galiractred","Galiravudd","Galoa","Gan","Garelgrin","Gaunyth","Geribwyn","Gerrawyn","Gias","Gietram","Gio","Glalevudd","Glaoloth","Glecon","Glelamos","Glelim","Glericon","Gleridric","Gliral","Gliraldric","Glirath","Gloimond","Gloiron","Glund","Goit","Gre","Greican","Grelav","Grila","Grilitram","Grosh","Guctred","Gwaeldric","Gwaeloth","Gwaleb","Gwaut","Gwelicred","Gwelicred","Gweloth","Gwilath","Gwilican","Gwiocon","Gwiral","Gwydaleron","Gwydardoder","Gwydauseth","Gwydeird","Gwydelath","Gwydendamond","Gwydigocon","Gwydilalath","Gwydiowyth","Gwydiracred","Gwydoawyr","Gwydoiwyr","Gwydum","Gwyl","Haaleldan","Haaom","Haarelith","Haaunad","Habard","Haeigord","Haelalin","Haelil","Haendadan","Haendaron","Haerracan","Haigoth","Hailacan","Haiowyr","Halinidd","Haomar","Hardowan","Harecred","Hautrem","Haya","Haywyth","Heacred","Hendaw","Herit","Hier","Hirald","Hiralin","Hoaand","Ibaleldric","Ibali","Ibau","Ibaulith","Ibaytha","Ibean","Ibelalin","Ibelawyr","Ibilaa","Ibilannor","Ibili","Ibiobwyn","Ibiradfrid","Ibiran","Iboadric","Iboannon","Iboiw","Jeraewyth","Jeraliwin","Jeraseth","Jereald","Jereatha","Jerelab","Jerelib","Jererag","Jereraron","Jererrawin","Jeriann","Jerieron","Jeriewin","Jerigowyn","Jerilibard","Jeroann","Kaaeb","Kaaymas","Kaeactred","Kaeagord","Kaelash","Kaelin","Kailidus","Kairannon","Kairevudd","Kali","Kaoewin","Kaoron","Kaylgrin","Kea","Kedareli","Kedayc","Kedayli","Kedeald","Kedelald","Kedelip","Kederamas","Kederrald","Kedietram","Kedilimond","Kedilith","Kedioli","Kedoider","Kedoreand","Keduth","Keiwyr","Keraldan","Keridric","Kiewyr","Kiewyr","Kilawin","Kililoth","Kirabard","Kiredan","Kiredric","Korev","Kua","Laledric","Laraemos","Laraubard","Laraugord","Laray","Laream","Larerictred","Lareseth","Larieb","Larigodric","Larigomond","Larirach","Larirawin","Laroawin","Latrem","Leap","Legare","Legarennon","Legaucon","Legeac","Legeadon","Legeagan","Legelar","Legiend","Legigowin","Legilaw","Legirenad","Legocred","Legoiwan","Legov","Leguwyth","Legyth","Lendawyn","Lerasean","Lerraseth","Liaseth","Lilann","Lireb","Locon","Loilin","Lotha","Lotha","Lothae","Lothau","Lotheinidd","Lotherasean","Lotheria","Lotheridus","Lothiedus","Lothoand","Lothonnor","Lothuc","Maerd","Malath","Malennon","Meidus","Melat","Melavudd","Melild","Miraemos","Miranad","Mirare","Mirareldric","Miraret","Miraush","Mire","Mirea","Mireg","Mireicred","Mirendach","Mirerracred","Mirisean","Miroili","Miroiwyr","Mirorelath","Mirug","Mis","Moinyth","Mynad","Natram","Naunn","Nea","Neilith","Niedfrid","Nilald","Nydaedon","Nydalecred","Nydalimar","Nydardoa","Nydardov","Nydarenad","Nydaumas","Nydeicred","Nydeip","Nydeit","Nydelinidd","Nydier","Nydigogord","Nydilactred","Nydilard","Nydiloth","Nydiratrem","Nydireldric","Nydoecan","Nydop","Ocae","Ocae","Ocanad","Ocardo","Ocardomma","Ocareldric","Ocas","Ocaulath","Ocenda","Oceran","Ocerraloth","Oceth","Ocigoder","Ocilild","Ociraloth","Ocoe","Ocoelith","Ocomma","Ocoredric","Ocumond","Ocyloth","Ocymma","Olaem","Olaemos","Olanyth","Oleash","Oleith","Olendac","Olerilgrin","Olili","Oliratrem","Oloa","Oloand","Olydric","Onagan","Onaret","Onel","Oneli","Onerinydd","Oniliw","Onionydd","Oniracon","Onoin","Onore","Palewyn","Pardoli","Paymas","Paysh","Piald","Pief","Piramma","Piw","Pobard","Praewin","Pralea","Prardonad","Praremos","Prau","Prelannon","Prerrabaen","Pri","Prief","Prilinad","Priliwin","Prira","Proer","Proreron","Pryli","Pulgrin","Puron","Puwin","Raaenyth","Raalidon","Raawin","Racred","Raeragan","Raiawyn","Railitrem","Raiotram","Raira","Raleron","Raw","Rayr","Reith","Rendadan","Rhaebard","Rharen","Rharetrem","Rhayran","Rheali","Rheraa","Rherath","Rherinnor","Rherith","Rhieloth","Rhigov","Rhira","Rhiraldric","Rhire","Rhoictred","Rhud","Rhycon","Riranidd","Roab","Roann","Roanwan","Saenidd","Saevudd","Salenad","Salivudd","Saod","Sar","Sardor","Sarewyn","Saywin","Selacon","Sevardoder","Sevarewin","Sevaywyr","Seveawin","Sevebwyn","Seveit","Seveiwan","Sevendald","Severrach","Sevich","Sevie","Seviratlan","Sevireand","Sevoawyn","Sevoennon","Sevoreron","Sevucred","Sevup","Sevyand","Siladfrid","Skaeg","Skarelith","Skaud","Skeanydd","Skeliwyn","Skig","Skilildric","Skioldric","Skirach","Skiwin","Skoicon","Skoiwyn","Sky","Soic","Tactred","Tadus","Taevudd","Talewyn","Tardoldan","Taunad","Teildric","Teilith","Teimas","Teitrem","Tendaloth","Terabaen","Teraloth","Thaed","Thardoch","Thareloth","Tharewyr","Thauseth","Thaydfrid","Theabwyn","Theach","Thedfrid","Thei","Thel","Thelilith","Thendanwan","Therrawyr","Thies","Thigobaen","Thio","Thira","Thoecred","Thoild","Thorep","Tirannon","Toedon","Toeldan","Trae","Traeld","Traenn","Traler","Trali","Traoa","Trardo","Trarenydd","Trelacon","Troewyn","Trore","Trowin","Tryand","Tua","Tybard","Tymas","Vaenn","Vaes","Vaetram","Vanad","Vaudan","Vaumond","Veand","Vef","Veiwyr","Velin","Verrard","Viap","Vietrem","Viracon","Viraf","Viranyth","Vireron","Voenn","Vorep","Wali","Waosean","Waybard","Waymond","Weadan","Weag","Weibard","Weip","Weli","Welilath","Wendabaen","Weriloth","Werra","Werrawin","Wetha","Wewin","Wicae","Wicaelath","Wicautlan","Wiceamma","Wiceitha","Wiceiv","Wicelamos","Wiceligord","Wicerican","Wicerinn","Wicietha","Wicigoran","Wiciralath","Wicoatha","Wicoid","Wicoth","Wigond","Wiod","Wira","Wira","Wirawin","Woalgrin","Woeder","Woemar","Woitha","Womma","Wunnor","Wuwyth","Wynn","Wysh","Yalenydd","Yalewyr","Yalildric","Yanydd","Yaund","Yawan","Ybaennor","Ybaes","Ybaev","Ybeim","Yberalith","Yberib","Yberip","Ybiraldric","Ybirelin","Yboir","Yboith","Ybomma","Yborelath","Ybuc","Ye","Yeab","Yeald","Yealdan","Yelatlan","Yerin","Yerrath","Yianad","Yiend","Yieth","Yigonnon","Yilawan","Yiretlan","Yoaldric","Yoith","Yotlan","Zaef","Zaemond","Zaub","Zauli","Zed","Zendalath","Zeral","Zeri","Zerra","Zilawin","Zilican","Ziowin","Ziremar","Zorerd","Zynn","Etaegord","Grilar","Lothendawyn","Yauf"]

# The really long list of middle names.
middleNameList = ["Aadfrid","Aaemar","Aaenn","Aalimos","Aaold","Aardocan","Aare","Abaomond","Abardodfrid","Abardoron","Aberic","Abigowyth","Abilich","Abiraloth","Abirawyth","Aboevudd","Aboigord","Aboreg","Acadus","Acaecon","Acaesean","Acaeseth","Acaetrem","Acarebwyn","Aceri","Acerit","Acilan","Acioseth","Acirawyn","Acirec","Acoalgrin","Acorenidd","Acuwin","Adaebaen","Adaelgrin","Adaetram","Adalidan","Adaos","Adaov","Adardonidd","Adei","Adeiwyn","Adelanad","Adiavudd","Adilaw","Adiradus","Adiranwan","Adoemond","Adoreloth","Adragan","Adrardogord","Adrardomar","Adrath","Adreamar","Adreig","Adrelamos","Adrera","Adrerimma","Adrerivudd","Adriewan","Adrinidd","Adrucon","Adrum","Aduwan","Adwalicon","Adweacred","Adweactred","Adweinnor","Adwelawyr","Adwienidd","Adwigogord","Adwilaw","Adwilawin","Adwilildan","Adwoenwan","Aelib","Aelim","Aeribwyn","Afacon","Afae","Afaecan","Afalennon","Afaocred","Afared","Afeawyr","Afeland","Afendath","Afialath","Afiliron","Afiowyr","Afiranyth","Afireder","Afirenwan","Afodon","Afoet","Agramar","Agraretlan","Agrelannon","Agrirasean","Agroath","Agroesh","Agroip","Agrore","Aiemos","Aiomma","Alaletram","Alaotram","Alarenyth","Alaudfrid","Aliald","Aliatlan","Aliracred","Alirewyn","Alomond","Alorel","Aoanydd","Aoar","Araemma","Araligord","Araliwan","Arendal","Ariagan","Ariatram","Arilabwyn","Arilit","Arirabard","Ariracred","Ariradfrid","Arirat","Aroinydd","Aroldan","Aroregord","Arorep","Asaetlan","Asaod","Asaum","Asaurd","Aselali","Aseli","Aselictred","Aseraseth","Asigoc","Asilatram","Asilich","Asilin","Asiraseth","Asiseth","Aso","Astaeg","Astaulgrin","Astea","Astea","Astei","Asteictred","Astelawyr","Astelinydd","Asteragan","Asterann","Asteri","Asterimond","Asterinydd","Astilat","Astilawyn","Astiodon","Astoli","Asubaen","Au","Aunnor","Bauwan","Belad","Belawin","Bendamma","Bendanwan","Berib","Berrann","Berratrem","Bigord","Bilidric","Braedus","Braennor","Bralewin","Bralinad","Braynnon","Brelalath","Briagord","Brilidfrid","Brilird","Brirawyn","Broeb","Broish","Brulith","Cadae","Cadaoldric","Cadau","Cadioseth","Cadiraand","Cadireldric","Cadoald","Cadoeth","Cadon","Caecan","Caewin","Cali","Caliwan","Caonn","Caonn","Cardo","Cardoli","Cat","Catha","Caurd","Cauwin","Cay","Caybwyn","Caynnor","Cear","Ceidric","Celawin","Celider","Celinydd","Cenda","Cendadan","Cerap","Cerasean","Ceridfrid","Ceritram","Cerrawyn","Chaelath","Chaes","Chaewyr","Chalemos","Chalibaen","Chardogan","Chardonidd","Chaydon","Cheath","Cheatha","Cheriseth","Chil","Chilannon","Chilis","Chiomond","Chired","Choac","Choew","Chorev","Chyctred","Chyw","Ciald","Ciat","Ciavudd","Cievudd","Ciewin","Cigob","Cigolath","Cila","Cilia","Cilird","Cio","Ciobard","Ciradon","Ciratrem","Cireron","Coelgrin","Coicon","Coind","Cois","Con","Corelin","Craef","Crannor","Craumond","Crayld","Creaf","Creath","Creravudd","Crerit","Crievudd","Criolin","Cro","Croadon","Croew","Cubard","Cyran","Daen","Daevudd","Daler","Daobaen","Dennor","Derralith","Diard","Diewyr","Digowan","Dilamma","Dira","Doremond","Drae","Drebaen","Drelaron","Drelith","Drigonwan","Drililin","Drilin","Drireseth","Droican","Drorerd","Dwaes","Dwaold","Dwaregan","Dweawyth","Dweinidd","Dwerrach","Dwiebwyn","Dwiowin","Dwoimma","Dwoit","Dworew","Edaes","Edaliloth","Edaretram","Edelicon","Edilican","Edirald","Edoelgrin","Edoewin","Edoiwyn","Edytrem","Elaectred","Elalerd","Elaogord","Elaugord","Elayn","Eleald","Eleicon","Elelildric","Elenda","Elieder","Eligon","Elilia","Elirabard","Eliratram","Elireran","Eloiwin","Elygan","Eowaegord","Eowaemas","Eowaesh","Eowalidon","Eowardolin","Eowardoran","Eowarend","Eowaynn","Eowecan","Eoweith","Eowelann","Eowia","Eowilili","Eowilind","Eowiretram","Eowoebwyn","Eowoin","Ereagan","Erelac","Erendactred","Erendadan","Ereramond","Ereril","Erigoder","Erilannor","Eriwyn","Erowin","Etalip","Etaubwyn","Etaymond","Etayth","Etelider","Eteligan","Eterimma","Ethaelgrin","Ethaowyr","Ethaum","Ethauth","Etheiwan","Ethilidfrid","Ethilinyth","Ethiraron","Ethireran","Ethirev","Ethoawin","Ethold","Ethonidd","Ethoreldan","Etiamos","Etiew","Etigowin","Etila","Etio","Etiom","Etirach","Etoib","Etynyth","Faetlan","Falenyth","Fath","Feanidd","Fearon","Feiv","Feriwyn","Ferrabwyn","Ferrand","Fianidd","Figotha","Fiodan","Fraomos","Frarennor","Freann","Freawan","Frei","Freitrem","Frerildan","Frerran","Fribwyn","Frira","Friracred","Frirec","Froiwyr","Frorend","Frynnor","Fryr","Fut","Gaeseth","Galeind","Galeliwyth","Galendamos","Galeridfrid","Galiawyth","Galieder","Galiladan","Galilath","Galiliv","Galiremar","Galoerd","Gare","Geaseth","Gelid","Geradfrid","Gerawyn","Gia","Gilgrin","Glaeld","Glaoa","Glareder","Gleratlan","Gliand","Gligov","Glilidus","Glirar","Gloasean","Gloedfrid","Glytha","Goalin","Goecred","Gore","Gralewyth","Graobaen","Graysean","Grearon","Greip","Greron","Griew","Grigowyr","Griocred","Groacan","Groish","Gruli","Gunwan","Gwach","Gwaesh","Gwalidric","Gwarennon","Gwelilith","Gwelin","Gwerath","Gwiewin","Gwigoran","Gwilash","Gwiratrem","Gwoawan","Gwut","Gwydarelgrin","Gwydaub","Gwydaum","Gwydaund","Gwydeawyn","Gwyderrach","Gwyderrannor","Gwydevudd","Gwydewan","Gwydiredus","Gwydoalin","Gwydoewyr","Gwydond","Gwydybwyn","Haaa","Haaoctred","Haaof","Haelach","Haeloth","Haemas","Haionn","Haire","Haoi","Harec","Haregord","Haywyth","Heand","Heder","Hew","Hilamond","Hiran","Hiraw","Hoac","Hoe","Hoeth","Hyvudd","Ibaedus","Ibalectred","Ibalith","Ibareldric","Ibaubaen","Ibaugan","Ibeatrem","Ibeladon","Ibeladric","Iberacon","Iberiw","Ibiatram","Ibilactred","Ibilasean","Ibiodus","Ibiranwan","Ibiretha","Iboe","Iboiwan","Iburan","Jeraewyr","Jerale","Jeralel","Jeralim","Jeraonad","Jereactred","Jerear","Jerelawin","Jerelicred","Jerelidus","Jerelitlan","Jeria","Jerilawyn","Jeriliwyn","Jerirader","Jerirep","Jeroamma","Jeroeand","Jerolgrin","Kaaesean","Kaaowyr","Kaaudric","Kaaunnor","Kae","Kaeag","Kaeimas","Kaelasean","Kaeld","Kaelimma","Kaendav","Kaerrag","Kaialdan","Kaield","Kaigoloth","Kainnor","Kaivudd","Kaoerd","Kaoiwyr","Kayth","Kedaenidd","Kedalicred","Kedare","Kedauw","Kedawyr","Kedeam","Kedeamond","Kedeamos","Kederabard","Kederimas","Kedi","Kedigod","Kedilin","Kediliwyth","Kedionyth","Kediow","Kelac","Kendabard","Kerraran","Kirath","Kirawyn","Koa","Koecon","Larae","Laraowyr","Larardor","Lareacred","Laredan","Larelaw","Lariralgrin","Lea","Leath","Legaev","Legalef","Legalewan","Legalimond","Legar","Legardonidd","Legeadfrid","Legeis","Legeliw","Legerra","Legerrath","Legieand","Legiemond","Legiomos","Legoiseth","Legot","Legyth","Legywin","Leidon","Leit","Lelac","Leladric","Lelinydd","Lendasean","Lennor","Lerranad","Loem","Lothaotrem","Lothardodric","Lothaulgrin","Lotheamar","Lothendard","Lotherras","Lothiat","Lothigo","Lothilawyn","Lothoaldan","Lothoivudd","Lothorem","Lothyr","Luch","Maedan","Malenad","Mardonidd","Maynyth","Maytha","Melili","Meraa","Mericon","Milap","Miradan","Miraolith","Miraonwan","Mirayb","Mireawyr","Mireic","Mireitrem","Mirelilgrin","Mirendatha","Mirendatlan","Mirerir","Mireriwan","Mirielin","Miriocan","Mirioron","Miroab","Miroan","Mirolath","Moremar","Nae","Naemond","Naotlan","Nelatha","Nerrat","Niald","Nigob","Niladfrid","Niosh","Nubaen","Nydaedan","Nydaem","Nydaen","Nydaoseth","Nydareron","Nydaua","Nyday","Nydeiv","Nydelac","Nydendadon","Nydendag","Nyderawin","Nyderildric","Nyderrat","Nydiecon","Nydigoth","Nydiold","Nydoesh","Nydubaen","Ocaeldan","Ocalili","Ocardow","Ocaycon","Oceamond","Oceib","Ociamas","Ocigog","Ociregord","Ocirelath","Ocirerd","Ocoinidd","Olaup","Olendash","Oleran","Oliannor","Oligog","Oligowan","Oliramma","Oliratha","Oloaw","Oloenidd","Olonnon","Oluctred","Onaecon","Onayseth","Oneli","Onili","Oniond","Oniragan","Oniratrem","Onoiseth","Ononyth","Onyt","Paleron","Palilith","Palimos","Palinnon","Pannon","Pe","Peamos","Peand","Peatram","Peawin","Pegord","Peish","Piamond","Pie","Piectred","Piliron","Pobaen","Praef","Praew","Prei","Prerral","Prilidfrid","Pryld","Raaog","Raeamar","Raeamas","Raelam","Raeliseth","Raeracon","Raeras","Raeriwyr","Raerraseth","Raialoth","Raietrem","Raigos","Rairemas","Ralig","Rand","Raoatha","Raoiwan","Raos","Relagord","Relal","Rhaom","Rhaomma","Rhardomas","Rharend","Rhaur","Rhay","Rheanwan","Rheif","Rhelidon","Rhilith","Riev","Rilac","Rilider","Riowyr","Rirawyth","Roa","Roildric","Sae","Saewyr","Saewyth","Sayt","Seildan","Seir","Sela","Sevae","Sevale","Sevalebaen","Sevaledon","Sevaow","Sevardoa","Sevaudus","Sevay","Sevelicon","Sevilimos","Sevirar","Sevoal","Sevoican","Si","Siracan","Siralath","Skaesean","Skeracon","Skerannor","Skinwan","Skioch","Skiravudd","Soawyn","Soecan","Soeldric","Soidric","Sunnon","Sush","Tash","Tayb","Teim","Telawin","Terrawin","Tewyn","Thaemar","Thaet","Thaylath","Thaymma","Thea","Thea","Theagord","Thiebaen","Thiedan","Thirash","Thoi","Thoredric","Thoron","Thotlan","Thulith","Thygord","Thywyn","Tilabwyn","Tiladfrid","Tiotlan","Todon","Toinad","Toinnon","Toish","Towyth","Traemos","Trao","Traucred","Trawyn","Trealdan","Trerrali","Triatha","Triegord","Trigoldan","Trila","Trilanad","Trilib","Trilidan","Trilinwan","Triogord","Trirabwyn","Troea","Troiwyn","Va","Vaegan","Vaow","Vardolath","Veictred","Velamos","Velanwan","Vendaf","Vider","Vigop","Vild","Voibwyn","Vum","Waew","Walennon","Walevudd","Wardof","Wardold","Waubaen","Wauwyn","Waynnon","Wayseth","Weacan","Wealdric","Weiloth","Weim","Weliand","Weliwin","Wia","Wiagan","Wiamond","Wicae","Wicaewyr","Wicald","Wicalen","Wicalinnor","Wicas","Wicautha","Wicaynd","Wiceic","Wiceigord","Wicelird","Wiceliwyn","Wiceran","Wiciawan","Wicilit","Wicof","Wiemar","Wigold","Wilinad","Wira","Woedon","Woiwyn","Won","Worech","Wotha","Wuloth","Wycon","Yal","Yald","Yamma","Yardowyr","Yarewyn","Yba","Ybaewyth","Ybayld","Ybeavudd","Ybendamos","Yberas","Yberiran","Ybigold","Ybilavudd","Ybilibard","Ybilif","Ybira","Ybiraw","Yboamma","Year","Yeladus","Yeligord","Yerard","Yerimos","Yesh","Yewyn","Yiracan","Yirash","Yirebaen","Yirewyn","Yiw","Yoal","Yoalgrin","Yob","Zaech","Zarech","Zareder","Ze","Zelanydd","Zemar","Zendawyn","Zerranwan","Ziof","Zirebaen","Zoewin","Zoia","Zoinyth","Zu","Zumas","Aawin","Aayt","Abaeb","Abalildric","Abareseth","Abaydric","Abeand","Abeawyr","Abelinyth","Aberadan","Abeth","Abiegord","Abilish","Acarewin","Acayd","Aceanad","Acelabaen","Aceli","Aci","Acietrem","Acilat","Aciov","Acoatram","Acoesh","Adaedric","Adaemma","Adaleron","Adaliwyn","Adaonnor","Adauwyth","Adaymma","Adeawan","Adigom","Ado","Adoevudd","Adralibard","Adraocred","Adraonyth","Adreribwyn","Adrerrawin","Adridon","Adrigocan","Adriomond","Adriowyn","Adrira","Adroi","Adroreld","Adrowan","Adrowyn","Adwardodus","Adwaunad","Adwelimond","Adwerilgrin","Adwigog","Adwoild","Adwuwyn","Aeitrem","Aelalin","Aerimma","Aetrem","Afaevudd","Afalelith","Afaoc","Afardolath","Afareldric","Afelamas","Afendanydd","Aferrath","Aferratha","Afilali","Afocon","Aforech","Agreatrem","Agreractred","Agrerralith","Agrilimond","Agroecan","Agroerd","Agronwan","Agroremma","Agrumas","Agrynwan","Aiab","Aig","Alaremas","Alegord","Alenda","Alendath","Aleramas","Alor","Aluloth","Aoawin","Arae","Araliwan","Arareseth","Araynad","Areidfrid","Areidric","Areild","Areind","Ariotlan","Arirea","Aroannon","Asaectred","Asaeth","Asalibard","Asaosean","Asareth","Asaya","Aseac","Asenda","Aseseth","Asi","Asilider","Asiomma","Asira","Asiratha","Asiratrem","Asoiwyr","Asoreand","Astalich","Astaliw","Astaord","Astealgrin","Asteicred","Astigotrem","Astiotram","Astiracon","Astiratlan","Astiremar","Asyran","Ayg","Bardob","Beaa","Beadus","Bei","Biawyr","Bilaloth","Biland","Biobard","Birawin","Birebard","Boren","Bralem","Brardom","Braybard","Braytram","Brendatha","Brilimma","Brioldan","Brirewin","Broasean","Broemond","Brorel","Brylith","Bub","Cadalewyn","Cadalimond","Cadareand","Cadauder","Cadauwyr","Cadeider","Cadelad","Cadelind","Caderar","Caderiv","Cadie","Cadilidon","Cadilimos","Cadiowyr","Cadirag","Cadiratram","Cadirennor","Cadit","Cadoasean","Cadorerd","Cadores","Cadybwyn","Cadynyth","Caef","Caetha","Calea","Calebwyn","Can","Caovudd","Cardoc","Cardon","Care","Carelin","Catrem","Caucan","Caycan","Ceacon","Cealoth","Cendaldric","Cendalin","Cendar","Cenwan","Ceramas","Cerra","Chaliwyr","Chardobwyn","Chelaf","Cherranad","Chiegord","Chirannor","Chiremas","Choalith","Choewyth","Chore","Cialith","Cigoand","Cigowyr","Cilannor","Cilasean","Cionnon","Cirewyth","Ciwin","Coannor","Coe","Coeand","Coegord","Coewyn","Coildric","Coitrem","Colgrin","Corecan","Cowyr","Crag","Craynnon","Craynwan","Cre","Creildric","Crerider","Creritlan","Criratram","Crorebard","Croremas","Cud","Daew","Dalidric","Daliran","Dardol","Dardoron","Dare","Darennor","Daymond","Deav","Deliron","Dendanad","Dennon","Deribwyn","Dialath","Digop","Dioron","Diraron","Direwyr","Draen","Dralebwyn","Drardowin","Draywyr","Dri","Drierd","Drilamond","Driog","Drire","Drirewyn","Droetrem","Droiwin","Drucan","Dwaed","Dwaedan","Dwalig","Dwardold","Dwennor","Dwerrath","Dwidon","Dwiliand","Dwiras","Dwiratlan","Dwoev","Dwotram","Dwunnon","Edaewin","Edalev","Edaonad","Edardoloth","Edaud","Edi","Edielath","Edigodon","Edigosean","Edilitrem","Ediobard","Ediremas","Edoewin","Edos","Edunyth","Elae","Elaoctred","Elaonnon","Elauv","Ele","Elea","Elealath","Elelanydd","Elerradric","Elerramos","Elerranyth","Elerrawyn","Elilacan","Elilam","Elilinnon","Elop","Eloreron","Elunidd","Elyrd","Eowalitrem","Eowardoseth","Eowares","Eowaumas","Eowaya","Eowayran","Eoweap","Eoweicon","Eowelabwyn","Eowelanidd","Eowoald","Eowoinydd","Eowyldric","Eraodric","Erareb","Eraudon","Ereatlan","Erief","Erilinnor","Erirard","Erirelgrin","Eroia","Eroiwyth","Eroldric","Erotha","Erunn","Eryseth","Etaetrem","Etaligan","Etardold","Etarep","Etarewyr","Etea","Etend","Eterralith","Ethaywyr","Ethe","Etheann","Ethendal","Etherath","Ethilaldric","Ethiras","Ethirec","Ethoitrem","Ethore","Ethorenydd","Ethurd","Ethuw","Eti","Etira","Etu","Etusean","Etyand","Faleg","Faop","Faumond","Fayli","Feladric","Fendac","Fendar","Ferrath","Ferrawin","Filis","Fio","Fodfrid","Fraletlan","Fraresh","Freabard","Frelinad","Frend","Frerard","Frilam","Frobaen","Froemond","Fyp","Fytram","Gaenwan","Galae","Galaodfrid","Galaonwan","Galare","Galareand","Galeder","Galeld","Galendatlan","Galioa","Galiramos","Galireand","Galoamas","Galoemar","Geit","Geiwyth","Gelilith","Genda","Gerawyn","Gietlan","Gigo","Gilinydd","Giliran","Gireran","Glaedus","Glaeron","Glaleldan","Glawin","Gleatha","Gleawan","Glep","Glerap","Gliranwan","Gloimar","Glorev","Graed","Grardos","Gref","Greigan","Gremos","Grerald","Grerrash","Griech","Grilicred","Grilimos","Griragan","Grirawin","Grirawyn","Grirecon","Groa","Groald","Groidfrid","Groiloth","Groitrem","Gwae","Gwaesean","Gwamar","Gwaosean","Gwaywyn","Gwei","Gwelican","Gwenda","Gwendash","Gwerind","Gwiawyn","Gwiewyn","Gwilam","Gwili","Gwiragord","Gwirann","Gwoawyr","Gwoidus","Gwydaeli","Gwydedfrid","Gwydendat","Gwyderrach","Gwydiatrem","Gwydiowin","Gwydirabaen","Gwydiraron","Gwydirewyr","Gwydoith","Gwydow","Gwydyrd","Haald","Haaleth","Haalilgrin","Haeiwyr","Haenwan","Haireseth","Haleg","Halelin","Halip","Haoadan","Haoan","Haoiran","Haoreldan","Hauld","Hauvudd","Hay","Haytha","Heannon","Helalgrin","Heridan","Herrac","Hiamos","Hiawyn","Hilacon","Hilam","Hilatlan","Hirali","Hiraw","Hirawan","Hire","Hirec","Hoe","Honyth","Horelgrin","Hylath","Iband","Ibaredan","Ibeaseth","Iberatram","Ibialin","Ibibard","Ibieder","Iboiwyn","Ibore","Iborelgrin","Ibyt","Jeraenad","Jeraenwan","Jeraov","Jeredric","Jereimma","Jereitram","Jerilavudd","Jerirav","Jeroader","Jerobard","Jerodan","Jery","Kaalennor","Kaaonidd","Kaardodfrid","Kaaywyth","Kaeawin","Kaerawin","Kaeriand","Kaif","Kaigoli","Kailider","Kaira","Kairaldric","Kalib","Kardonwan","Kauf","Kaumma","Kauwyn","Kea","Keda","Kedae","Kedalecred","Kedarelith","Kedauwan","Kedean","Kedearan","Kedelisean","Kedi","Kedilamas","Kedilannon","Kedirann","Kedirath","Kedoadric","Kedoi","Keil","Kiegan","Kilabard","Kilav","Kydon","Laleld","Lalicon","Laoli","Laraem","Laraewyth","Larale","Laralew","Larardobwyn","Lare","Larendatha","Lareriwyth","Larilac","Larirann","Larorea","Legaesean","Legalisean","Legaoand","Legealith","Legelit","Legendasean","Legerawin","Legiac","Legiactred","Legigoder","Leginn","Legiond","Legirelin","Legorewyn","Lelacon","Lelilgrin","Lerralin","Lialoth","Lienad","Ligoth","Lirann","Lirenad","Loan","Loedric","Loind","Lomma","Lothacan","Lothae","Lothael","Lothaodus","Lothaonad","Lothardocan","Lotharebwyn","Lotheavudd","Lothec","Lotheralin","Lotheraloth","Lothewyth","Lothilali","Lothorech","Lothorewyn","Lothutha","Lowyn","Lymos","Mae","Maenydd","Mardomma","Maydon","Meaa","Meawan","Mendawyth","Miemar","Milidus","Mira","Mirader","Miraecon","Mirawyr","Mirayv","Mireasean","Mirelind","Mireliwan","Mirerild","Mirieb","Miriewin","Mirigo","Mirilavudd","Miriragord","Miroavudd","Miroea","Mirorea","Moibard","Moreg","Munwan","Naecan","Naes","Nalewyr","Nardolin","Nedon","Nelanydd","Nydaebaen","Nydale","Nydaoloth","Nydardowin","Nydarep","Nydaymos","Nydaytlan","Nydeim","Nydelild","Nyderrali","Nydiectred","Nydili","Nydiraloth","Nydirenn","Nydiw","Nydoelath","Nydoig","Nydu","Nydytrem","Ocaelin","Ocaevudd","Ocali","Ocaoran","Ocauw","Oceabard","Ocean","Ocelaa","Ocendagord","Ocerannor","Oceri","Ocerican","Ocerralgrin","Ociom","Ocira","Ocoacon","Ocorennor","Ocynidd","Ola","Olaeld","Olaenad","Olaeron","Olaledan","Olayctred","Oleir","Olela","Olenda","Oliatram","Olicred","Oliech","Oliecred","Oloannor","Oloef","Olold","Onach","Onalia","Onaold","Onaotram","Onauld","Oneand","Onearan","Oneis","Onelannon","Onendanad","Oneribwyn","Onerraa","Onerraldric","Oniedus","Onilamar","Onu","Onudric","Onunidd","Onyr","Onyrd","Paelgrin","Paod","Parebard","Paucon","Payseth","Payth","Paywyn","Pe","Pear","Pendadan","Peraand","Perinad","Perrawan","Pien","Piladan","Piocred","Piragord","Pith","Praectred","Praenyth","Praus","Premos","Prendalin","Priand","Prider","Prig","Proe","Proenn","Prywyth","Puwyn","Pywyn","Raauwyn","Raendawyr","Raendawyth","Raeridfrid","Raira","Ralecon","Raoegord","Raorech","Relap","Relimond","Rerra","Rhaem","Rhaled","Rhanad","Rhau","Rheann","Rheash","Rheiand","Rhein","Rherrader","Rhiab","Rhiach","Rhiliw","Rhiowyn","Rhiram","Rhoemar","Rhumos","Rhyl","Rigowyth","Rilanidd","Rinn","Riobwyn","Rocred","Roitrem","Rub","Rub","Saulath","Selann","Semos","Serimma","Serradfrid","Sevalenydd","Sevaoloth","Sevat","Seveamma","Sevelasean","Sevendash","Severil","Severiwyn","Seviend","Sevienidd","Sevilanwan","Sevireldan","Sevoiwin","Sialdan","Silib","Sirabaen","Sirac","Skaegord","Skauwyn","Skelamos","Sker","Skieloth","Skioldan","Skiron","Skoas","Skoawin","Soawyr","Socon","Sodric","Subaen","Taewin","Taoder","Tardolath","Taretram","Teatlan","Telinad","Thaecon","Thaeldan","Thalin","Thaunydd","Thauron","Thawan","Thaybwyn","Thea","Thendath","Thep","Theron","Therra","Therracred","Thielgrin","Thieth","Thigo","Thigol","Thigold","Thilili","Thimma","Thinyth","Thirewyr","Thiwyth","Thoas","Thoeg","Thoenidd","Thoinydd","Thoremos","Thunnor","Tiralath","Tirash","Toiv","Toredus","Toref","Traemma","Tralec","Trali","Tralig","Trayldan","Trelalgrin","Trelath","Trem","Trendactred","Trerraf","Trider","Trie","Trigogord","Troawyr","Troiran","Trolgrin","Varewyth","Vau","Vaubard","Vay","Vaycan","Veaf","Vela","Verra","Verrasean","Vilard","Vio","Vocred","Vycan","Vymos","Vytram","Waedan","Waeldric","Walild","Waregord","Waym","Wea","Weaw","Weild","Wel","Welanyth","Welit","Weliw","Werictred","Werig","Wevudd","Wicaliwan","Wicarend","Wicaup","Wicayand","Wicaywyn","Wiceidus","Wiceinydd","Wicelanidd","Wicendath","Wicendavudd","Wici","Wiciewyn","Wicoilath","Wicoili","Wicoinad","Wicywyn","Wielath","Wigonad","Wigowyth","Wirabwyn","Wiradan","Wirag","Wiratram","Wiref","Wireron","Wo","Woenydd","Woigan","Worebard","Worel","Worennor","Worevudd","Woseth","Wu","Wulgrin","Wya","Wyran","Yaa","Yaeb","Yaen","Yalia","Ybaoch","Ybared","Ybeavudd","Ybeli","Ybelildan","Yberawyr","Yberratlan","Yberratrem","Ybeseth","Ybiwyr","Yboav","Ybogord","Yboinidd","Yboresean","Yborewin","Yean","Yelidfrid","Yie","Yirand","Yiraseth","Yoald","Yoif","Zares","Zeawyth","Zebaen","Zelagord","Zen","Zendacon","Zira","Zoem","Zoron","Aaeg","Aaeran","Aalit","Aaydfrid","Aaymar","Aayv","Abaydus","Abaywyth","Abeabard","Abio","Abionn","Acalenidd","Acaysean","Ace","Aceanidd","Acelactred","Acelalith","Acet","Acilinyth","Acirelath","Acoiron","Acorevudd","Adawyn","Adeath","Adeladus","Adelith","Adiov","Adoldric","Adorend","Adraes","Adralild","Adrareloth","Adrauld","Adrauloth","Adraunwan","Adreit","Adrelictred","Adrendat","Adreranidd","Adrerinyth","Adres","Adriresean","Adroewyth","Adrygan","Adunn","Adwaletram","Adwalimond","Adwardonnor","Adweidan","Adwelith","Adwerra","Adwerralith","Adwerranyth","Adwoe","Adwoel","Adwoib","Adwosh","Aerrach","Afaedfrid","Afaliwyr","Afaolgrin","Afeabard","Afeld","Afelith","Afemar","Aferiw","Aferiw","Aferiwyn","Afiratrem","Afireld","Afiwin","Afoawin","Agraesean","Agraewan","Agraonydd","Agraredon","Agraresh","Agraudric","Agrawyn","Agraywyth","Agrean","Agreid","Agrelalath","Agreli","Agreratlan","Agrerimos","Agrerrag","Agrerrann","Agriap","Agrigobaen","Agroreran","Agrud","Ailald","Ailanydd","Ailiwyn","Airalin","Airath","Alaelith","Alaewan","Alalea","Alaled","Alalenydd","Alalenydd","Alamas","Alaos","Alerramar","Alerrat","Aliewyn","Alilanyth","Aliliwyth","Aliralath","Aliratrem","Aoaran","Aoec","Aoredon","Aosh","Araegord","Araerd","Aralia","Arardoc","Arare","Araum","Aray","Areadric","Areinn","Arelinyth","Areraloth","Areriwyr","Arerrav","Ari","Ariecred","Arielith","Arigolgrin","Arilac","Arili","Arilig","Arirend","Aroactred","Aroia","Arorech","Aryld","Aryvudd","Asaeran","Asalinyth","Asaliwyn","Asaumar","Asauwin","Asaydan","Asayrd","Asea","Aseav","Aselamma","Aselimma","Asendabwyn","Asendand","Asera","Aserratha","Asoidon","Asoremma","Astaelgrin","Astaeth","Astalemma","Astaredon","Astaydan","Asteitram","Asteradan","Asterald","Astienydd","Astiramond","Astoe","Astoldric","Astudan","Astydan","Ayc","Ba","Bardolath","Bareldan","Baseth","Beiwyth","Berald","Birabard","Bitlan","Bord","Braebwyn","Braennon","Braes","Braewyr","Bralen","Bralind","Braliwan","Braold","Breaw","Breibaen","Breris","Brerrawin","Brerrawyr","Briacon","Brigond","Brilaf","Brilanad","Brilird","Briravudd","Briwyr","Brydan","Butram","Bymma","Bysh","Cadadus","Cadaecan","Cadalectred","Cadalildric","Cadalith","Cadearan","Cadeawyth","Cadeinidd","Cademas","Cadilaa","Cadiowyn","Cadiraloth","Caditha","Cadubwyn","Caedfrid","Caegord","Caesean","Caledfrid","Calelgrin","Calir","Canydd","Cao","Caolgrin","Cardolith","Cardom","Cas","Cauldan","Cauldric","Cayc","Caynidd","Caynydd","Cea","Ceald","Ceatlan","Celdric","Cendabard","Chabwyn","Chae","Chaet","Chaytha","Cheath","Cheria","Chiraloth","Choecred","Choegan","Choreder","Ciadan","Cie","Ciewin","Cigow","Cilannon","Cililith","Ciliwyr","Cimos","Ciolith","Coilin","Craemma","Crawin","Creab","Creadfrid","Creinyth","Crelim","Crerib","Criawin","Criebard","Crigobard","Criratrem","Crirend","Crireth","Crug","Crur","Cynnon","Daemar","Dalidus","Daowyth","Dardomma","Deidus","Delas","Delin","Derabard","Dirad","Dirard","Dirasean","Diratlan","Direth","Doevudd","Draliwyn","Drardowin","Dreacred","Drelider","Drigoder","Drigomos","Driom","Driomos","Droildan","Drorecred","Drosh","Dwaocon","Dwaywyth","Dwelap","Dwelatha","Dwelidon","Dwiand","Dwigo","Dwigo","Dwili","Dwilith","Dwoer","Edalildric","Edardov","Edaygan","Edield","Edigo","Edild","Ediomond","Edioron","Ediranyth","Edy","Edyc","Elalis","Elaoth","Eleabard","Elelich","Elendas","Elerash","Elerinwan","Elerra","Elirad","Eliret","Eloecan","Elold","Elorelith","Eowa","Eowaud","Eowaulin","Eowautrem","Eowea","Eoweach","Eoweamos","Eowearan","Eowendaa","Eranydd","Eraonyth","Eraoth","Erardomar","Erea","Ereith","Erendawyn","Ereranidd","Ererrath","Erigan","Eroic","Eroiwan","Eryc","Eryseth","Etab","Etadus","Etae","Etaliron","Etareldric","Eteran","Ethaeron","Ethaletha","Ethalibard","Ethatram","Ethaunidd","Ethaynnor","Ethea","Etheash","Ethelannon","Ethendaf","Etherrawin","Ethigon","Ethilawyr","Ethilawyr","Ethiwyn","Ethoibard","Ethow","Etiac","Etiamos","Etic","Etigolgrin","Etiratram","Etoald","Etoetlan","Etoibwyn","Etoir","Etyseth","Faem","Faleand","Faliv","Faowyr","Fardoa","Fardowan","Feamond","Felannon","Feridus","Ferraand","Ferralin","Frae","Fralelith","Frardolith","Freacan","Freivudd","Frelip","Frerraran","Friann","Frurd","Gag","Galalew","Galanwan","Galeand","Galeritlan","Galiawin","Galilabaen","Gaog","Gaov","Garetrem","Garetrem","Geamma","Gelannor","Geritha","Gerragan","Gerralin","Gilictred","Giliwyr","Giotlan","Gire","Gireli","Glalitha","Glardoctred","Glareli","Glaul","Gleanad","Gleracan","Gleraw","Glerimas","Glilatlan","Gliowyn","Gloidric","Gloitlan","Glucon","Gly","Graydfrid","Grays","Gre","Grelamma","Grilabaen","Grioli","Griragan","Griras","Griratram","Grith","Gro","Groamma","Groreth","Guder","Gwaudfrid","Gwea","Gweic","Gweilin","Gweland","Gwen","Gwendatrem","Gwias","Gwigobaen","Gwilit","Gwoe","Gwoigord","Gwydaeb","Gwydaennor","Gwydalectred","Gwydeilith","Gwydelader","Gwydelip","Gwydelitha","Gwydigoron","Gwydilaw","Gwydirel","Gwydoann","Gwydoi","Gwyduron","Haaedric","Haaedus","Haaeld","Haand","Haardobaen","Haarech","Haatrem","Haawyr","Haea","Haeabwyn","Haearan","Haeildan","Haelimond","Haialdric","Haiebaen","Haietlan","Hailash","Hainad","Haio","Hairat","Haireth","Haoactred","Haoadfrid","Haoea","Haof","Harenidd","Hauvudd","Hendatrem","Herictred","Higow","Hiladfrid","Hili","Hiralin","Hoad","Hoadus","Hoic","Hoil","Hois","Ibaledric","Ibamas","Ibaocon","Ibardonnon","Ibeawyr","Ibelawyth","Iberidon","Ibi","Ibiadfrid","Ibienn","Ibilasean","Ibiliwyr","Ibiliwyth","Ibirawyth","Iboasean","Iboelin","Ibonn","Iboreb","Ibynn","Ibynn","Ibynwan","Jerauwyn","Jeray","Jereannon","Jereir","Jerelar","Jereramond","Jererin","Jererradon","Jeriabard","Jerirash","Jeriv","Jerymas","Kaaeldric","Kaalilin","Kaaren","Kaaua","Kaealgrin","Kaelib","Kaer","Kaerider","Kaerind","Kaigobwyn","Kaioli","Kaiowyr","Kairadon","Kairanyth","Kaoreand","Kaoreb","Kardod","Kaurd","Keatrem","Kedaedan","Kedaet","Kedardocon","Kedarev","Kedelader","Kedendacon","Kedendalath","Kederar","Kederraf","Kediamos","Kedigo","Kedigosh","Kedirag","Kedoatlan","Keduldric","Ketrem","Kiodfrid","Kivudd","Koam","Lagord","Lalidfrid","Laraewan","Lardold","Lardoli","Larelidric","Lariacon","Larigod","Larigotrem","Laroaseth","Laryt","Lau","Legaligord","Legaomma","Legelac","Legeraf","Legeriwyn","Legiag","Legialgrin","Legich","Legienwan","Legiliwyn","Legirald","Legiramond","Legirannor","Legiremond","Legoennon","Legyg","Lelanidd","Lelawyn","Lendan","Liatlan","Lioldan","Lion","Liowan","Lir","Liraand","Lirabaen","Loebard","Loidan","Loregord","Lothaet","Lothale","Lothardoctred","Lothardot","Lothaydan","Lothela","Lotheliwyth","Lotheralith","Lotheriseth","Lothewyr","Lothiranidd","Lothiratrem","Lothoadfrid","Lothobard","Lothof","Lothorenad","Lothund","Lothywyn","Lulith","Maet","Maudus","Maumar","Maup","Maymar","Maysh","Mela","Melamma","Mendam","Mendanydd","Miat","Migan","Milip","Miraleb","Mirannor","Miraup","Mirea","Mirel","Mirelader","Mirendaran","Mireragord","Mirerragan","Mirialdan","Miriawan","Miricon","Miriliwin","Mirirawin","Mirynydd","Naebard","Naunnor","Naydric","Nelald","Nelibard","Neragan","Nianwan","Nigop","Nirav","Nobwyn","Noewyr","Noibaen","Nord","Nydardog","Nydardoth","Nydeitha","Nydelannor","Nydelawyr","Nyderrach","Nydilaron","Nydioli","Nydoennon","Nydoewin","Ocaewyr","Ocardon","Ocarelith","Ocaymar","Ocea","Oceabwyn","Oceid","Oceidan","Oceridric","Ocerrawyth","Ocidon","Ocilaa","Ocinad","Ocoa","Ocuder","Ocuvudd","Olalewyn","Olalider","Olanydd","Olaoron","Oleadfrid","Olenda","Olerimma","Oliadus","Oliap","Oligold","Olilanad","Oloeth","Oly","Olynd","Onale","Onaoch","Onaycon","Oneach","Oneand","Oneladfrid","Onilasean","Onilawin","Oniraldric","Onoem","Onoinnor","Onorebwyn","Onuwin","Paoc","Pare","Peabard","Pendavudd","Peridus","Perind","Perrat","Piab","Pigodric","Pio","Pionydd","Piram","Piw","Pold","Praedric","Prap","Prar","Prarewin","Prea","Preanyth","Preatram","Preavudd","Prelagan","Prerald","Prerawin","Preriwyr","Prira","Priratrem","Procon","Prorer","Raalea","Raann","Raardoa","Raeawin","Raela","Raeladan","Raerd","Raiebard","Rairab","Raiwin","Raoewin","Raoiand","Raoild","Raowan","Raywan","Redric","Rendacan","Rerra","Resean","Rhamar","Rharemond","Rharennor","Rhay","Rheanyth","Rheild","Rheilin","Rheiseth","Rhelali","Rherraloth","Rhigobard","Rhiland","Rhirelgrin","Rhirelin","Rhoedan","Rigoron","Rirecred","Roewan","Roiwyn","Roreld","Roret","Ru","Ruloth","Saobwyn","Sarerd","Sendadon","Sendard","Seron","Sevaliand","Sevalilith","Sevealgrin","Sevebwyn","Sevilaand","Sevilider","Seviov","Seviracred","Sevoath","Sevodon","Sevyc","Sialin","Sield","Sigolath","Siliron","Siregord","Sirenn","Skaremas","Skeatram","Skelawyn","Skerildan","Skinidd","Skire","Skoebaen","Skoewyr","So","Soadon","Soeld","Soi","Soinn","Sorem","Sy","Tay","Tea","Teliv","Tendalath","Thanyth","Thaor","Thaotlan","Tharet","Thea","Thean","Theasean","Theif","Theinwan","Thelinn","Thenydd","Thera","Theriron","Therraa","Therrar","Thigolith","Thigonyth","Thilinydd","Thioseth","Thoemas","Thoemma","Thoildric","Thuv","Tigoron","Tiradric","Tomond","Traled","Traubaen","Trauld","Trelinnor","Trelip","Trerann","Trerili","Trerraf","Trilanwan","Trilinad","Triranwan","Troaand","Trolith","Va","Vaecred","Vardowyn","Varedon","Veivudd","Veld","Veri","Viatrem","Vilach","Vilaf","Vira","Viracon","Viwyr","Voed","Vores","Waenyth","Waet","Wales","Waonnon","Wardodon","Wareder","Warel","Waumond","Wayth","We","Weabard","Weibard","Wela","Welil","Welith","Werawan","Wia","Wiand","Wicaegord","Wicaleldan","Wicauth","Wiceaf","Wiceasean","Wiced","Wicendabaen","Wicerilgrin","Wicilaron","Wiciod","Wiciwyn","Wicoeloth","Wicoenad","Wicoesh","Wicoet","Wicoibard","Wicorelith","Wicywan","Wiecan","Wilaldric","Wilamas","Wilan","Wilird","Wiliwyr","Wiracan","Wiratha","Wireder","Wocan","Wodus","Womma","Woreg","Wutrem","Wydus","Wygord","Wywyn","Yaewin","Ybalebard","Ybalild","Ybardos","Ybarenad","Ybeawyn","Ybendaseth","Ybiath","Yboanyth","Yboeld","Ybyp","Yeaseth","Yelib","Yendawyr","Yigoldric","Yoadus","Yynydd","Zare","Zaycred","Zaywin","Zaywyr","Zeach","Zeanyth","Zilild","Ziratrem","Zorewan","Zuvudd","Aaea","Aaeth","Aalimos","Aardomos","Abaetlan","Abalgrin","Abeach","Abenda","Abire","Abiredus","Acaeloth","Acaled","Acardocan","Acelilith","Acelimma","Acendal","Aciliwyr","Aciobwyn","Acoali","Acoath","Acoav","Acoid","Acorecan","Acu","Adaeand","Adeard","Adeawyr","Adendaa","Adendaldric","Aderawyr","Aderragord","Aderrap","Adiladus","Adiold","Adiradfrid","Adiran","Adoaldan","Adoremma","Adorerd","Adraowin","Adraredric","Adreiwin","Adrerrap","Adrerratlan","Adrerrawyn","Adrigan","Adrira","Adroetram","Adroitrem","Adromas","Adwac","Adwaletrem","Adwaodric","Adwareb","Adwaunn","Adweac","Adwelgrin","Adwelibwyn","Adwendacan","Adwerican","Adwerrabard","Adwiomond","Adwiras","Adwish","Adwobwyn","Adwoigan","Adworeth","Adwyli","Aeadfrid","Aeland","Aelat","Aendag","Aerigan","Aerranad","Afalif","Afauli","Afawan","Afaymma","Afelacon","Afelictred","Aferabard","Afericred","Afiacred","Afili","Afireld","Afoat","Afobaen","Aforenyth","Agraeth","Agralim","Agraof","Agrardod","Agrau","Agrauf","Agrauran","Agrelavudd","Agreraloth","Agrerawyr","Agridus","Agrilitlan","Agrio","Agrioctred","Agrioldan","Agriran","Agruran","Aiactred","Aield","Ailabwyn","Ailalgrin","Ailawin","Ailit","Airech","Alaeg","Alaem","Alard","Alaynnon","Aleanad","Aleath","Alelabard","Aleriwan","Alerracred","Alerral","Aliand","Alilaldan","Alioran","Alira","Aliraand","Aloibaen","Alugord","Aoin","Araegord","Aralech","Arelab","Arerilith","Arerrawyn","Arilaf","Arionnor","Ariotlan","Arorenidd","Aru","Aru","Aruwan","Asacan","Asaleldan","Asaowin","Asaydon","Aseriran","Asilag","Asilican","Asilind","Asir","Asiramma","Asiramos","Asiratrem","Asiwin","Asoav","Asoimas","Asoreron","Astaelgrin","Astaeseth","Astaewyth","Astalimma","Astay","Astelimar","Astenad","Asterrawyth","Astiacred","Astililoth","Astilith","Astirawyn","Astoec","Astorerd","Astyldric","Astynidd","Balivudd","Beadric","Berash","Betlan","Birennon","Boacred","Bore","Bralet","Bralild","Brannor","Brei","Brelican","Breradan","Briowin","Briraldan","Broredan","Bru","Bych","Ca","Cadaewyn","Cadalewin","Cadalild","Cadaolgrin","Cadaop","Cadardogan","Cadaynwan","Cadelild","Caderar","Cadfrid","Cadieseth","Cadigoli","Cadilavudd","Cadioctred","Cadiracred","Cadireld","Cadoidus","Cadywyn","Cae","Caedus","Caeldan","Caelgrin","Caerd","Caet","Caewyn","Calemond","Calidfrid","Calig","Calimma","Caliwyn","Caod","Caolath","Caotlan","Cauder","Cay","Caylath","Caylath","Cebard","Ceder","Ceidon","Ceimas","Ceinyth","Ceiwyth","Celav","Celimar","Celiran","Cendav","Cerracan","Cetrem","Chalilith","Chamar","Chaof","Chardosean","Chaunwan","Chauseth","Chav","Cheaand","Cheacan","Ched","Chelannor","Cherand","Cherilin","Chictred","Chigowyth","Chilar","Chilicred","Chinyth","Chiol","Chireli","Chires","Choenydd","Choreld","Chutram","Ciemma","Ciet","Ciewyr","Cilas","Ciowin","Cirawan","Cirebaen","Ciremond","Citram","Coag","Coand","Coav","Cor","Core","Coretrem","Craetlan","Cralea","Cralibwyn","Crardo","Crardodric","Crauvudd","Cray","Craycred","Crelird","Crendatrem","Creracan","Crerrannor","Criaw","Crich","Criradfrid","Crirecon","Cronnon","Croremos","Cutrem","Daedon","Deatha","Desean","Diadan","Dilanidd","Diligord","Dion","Dorennor","Drardomond","Drauw","Draylath","Dreimma","Drelin","Dreradan","Driev","Drirecred","Droe","Droe","Drord","Drudric","Duwyn","Dwaoldan","Dwelaand","Dwerav","Dwerramas","Dwewan","Dwiet","Dwiewan","Dwila","Dwirasean","Dwiseth","Dwoelith","Dwow","Dwumas","Dwuwan","Dwyb","Edaewyn","Edear","Edelit","Edie","Edielith","Edionad","Edoad","Edoe","Elaelath","Elaeseth","Elali","Elaolith","Elaresean","Elea","Elerigan","Eliop","Eliracan","Eloaa","Eloenyth","Elowyr","Elubwyn","Eowa","Eowales","Eowao","Eowealath","Eowerralin","Eowilaa","Eowilitrem","Eowirabard","Eowiragord","Eowotrem","Eraleldric","Erardor","Erayldric","Erealath","Erelamos","Ereritram","Eriravudd","Eroep","Etalecred","Etalimar","Etarec","Etaubwyn","Eteith","Ethae","Ethale","Ethaoldric","Ethaond","Ethaov","Ethardobard","Etheig","Etheild","Ethelannor","Ethelilith","Ethirew","Ethoadon","Ethoe","Ethore","Etiraloth","Etirand","Etoaw","Faliwyr","Faoctred","Faomos","Faudfrid","Fealin","Feiron","Fendalith","Ferald","Feratlan","Ferd","Fiabaen","Filacon","Fild","Filin","Fionidd","Fiosh","Fra","Fraedon","Fraetha","Fralewyr","Fralild","Fraliseth","Fraowyth","Frealith","Frerad","Frerraldric","Friebaen","Friewin","Friradan","Froiwyn","Frore","Frubaen","Fubard","Fup","Fynnor","Galae","Galaem","Galaletrem","Galalinad","Galardoctred","Galaysean","Galelap","Galelibard","Galerawyth","Galerraron","Galigod","Galilach","Galoewin","Galorenyth","Geader","Gelin","Gienad","Gigold","Gigonwan","Gilamas","Giliseth","Giop","Gioth","Giramma","Glacon","Glaesean","Glarewyr","Gleand","Gleibaen","Glendalath","Glerral","Glianwan","Gload","Gluseth","Glynad","Goigord","Goreg","Graec","Graeld","Graeseth","Graevudd","Grardomos","Graya","Grea","Greican","Greinyth","Grela","Grelam","Grirader","Griwyn","Groech","Groreli","Gwaeli","Gwaennor","Gwalenydd","Gwaoth","Gwares","Gweanad","Gwiamma","Gwie","Gwilitram","Gwiovudd","Gwirald","Gwiremos","Gwiv","Gwu","Gwun","Gwydaebwyn","Gwydaebwyn","Gwydalinydd","Gwydardotlan","Gwydaynd","Gwydea","Gwyderaron","Gwydirawyr","Gwydirawyth","Gwydoctred","Gwydoelin","Gwydond","Gwydubwyn","Gwydynnon","Gwygord","Haardov","Haaylgrin","Haeavudd","Haiodric","Haireran","Halegan","Hao","Haug","Haunwan","Haymma","Hililin","Hilimar","Hilish","Hiratha","Ibaewyr","Ibareld","Ibayw","Ibeanad","Ibeip","Ibendald","Iberinn","Ibiranidd","Ibirannor","Ibirerd","Iboinyth","Iboiwyth","Jeraledan","Jeraliwan","Jerarewyr","Jereadus","Jereat","Jeriawin","Jerilidon","Jeriobwyn","Jerira","Jerirash","Jeroiwyth","Jerunyth","Jeruwin","Kaaenidd","Kaalild","Kaalin","Kaelacon","Kaelacon","Kaerawyr","Kaerimma","Kaeriron","Kain","Kairaldan","Kairawyr","Kairec","Kairedfrid","Kaireloth","Kaoif","Kaoreder","Kaorelith","Kayl","Kaymas","Kaynydd","Kedaldric","Kedalemos","Kedare","Kedaydfrid","Kedelanyth","Kederaran","Kedigonwan","Kedireth","Kedov","Keild","Kinyth","Kiovudd","Koaron","Kom","Koredan","Laraleldric","Laraonn","Larardosh","Larawan","Laraynyth","Lareawyn","Lareli","Larendawan","Lareriseth","Larigobwyn","Larigop","Lariradan","Larirawyn","Larirecan","Larirecred","Larirelin","Larirennor","Laroef","Laroremma","Larygord","Lauseth","Leal","Leatram","Legae","Legareand","Legaywyr","Legeisean","Legelagan","Legenwan","Legerish","Legerraand","Legigom","Legilibwyn","Legilith","Legio","Legiowyth","Legira","Legomos","Legorebard","Legywyr","Leraldan","Leriand","Liewin","Lilanidd","Lilip","Liresh","Loath","Loid","Loinad","Loip","Lotha","Lothaevudd","Lothardomond","Lotharelath","Lothauc","Lotheand","Lotheicred","Lotheil","Lothider","Lothiow","Lothoat","Lothumma","Mardob","Marecred","Maredan","Mautram","Meibwyn","Melip","Merrav","Mira","Miralemas","Mirarenwan","Mirelag","Mirelildan","Mirendamos","Mirilannor","Miriocan","Miriramond","Miroacred","Miroeldric","Mirymma","Mirymond","Mitram","Moe","Naemos","Nalebaen","Naold","Nayn","Neamar","Nelaldric","Nelig","Nerralith","Nias","Nilaldan","Nio","Noeg","Nun","Nydaebaen","Nydalath","Nydalegan","Nydardof","Nydauc","Nydaumond","Nydaush","Nydayld","Nydealdric","Nydeawyth","Nydech","Nydeia","Nydeig","Nydendamma","Nydendath","Nyderraldan","Nydili","Nydilitram","Nydim","Nydiraron","Nydoa","Nydoaron","Nydoidfrid","Nydoretram","Ocalith","Oceal","Oceanidd","Ocelawyth","Ocelin","Oci","Ocieb","Ocila","Ociranydd","Ocoilith","Ocyd","Olaem","Olaosean","Olarea","Oleadon","Oleasean","Oleragord","Olerivudd","Oliligord","Olilimma","Olilisean","Olires","Oloamar","Oloreldric","Olycred","Onactred","Oneiwin","Onelac","Oneractred","Oniraf","Onoard","Onosean","Onun","Paecred","Paer","Paeseth","Paoli","Parewyr","Paucan","Paulith","Payv","Peia","Pein","Pigom","Pili","Piraran","Poreth","Praeld","Praligan","Prelibaen","Prelitlan","Prendalith","Prilal","Prilip","Priran","Priranwan","Prith","Proatrem","Prytrem","Raaenyth","Raeat","Raiaand","Raib","Raiebard","Raigosean","Railamos","Railas","Railid","Rairald","Rairamond","Raoa","Raoanyth","Rardobwyn","Raunnor","Reawin","Rela","Relanydd","Relilath","Reliwyr","Reradan","Rerawyr","Rhaea","Rhaoloth","Rheat","Rhelamas","Rhemma","Rheradus","Rherap","Rhila","Rhilimos","Rhirap","Rhoith","Rhoiwin","Rhy","Rila","Riladon","Rilicred","Rira","Rirald","Riratlan","Riseth","Rorenydd","Rorevudd","Rorewyr","Rud","Saecan","Sali","Salidric","Seidan","Sevalimma","Sevaud","Sevautlan","Seveawyn","Sevilawyr","Seviotlan","Sevyrd","Siecan","Siemas","Siocon","Skaewyth","Skalidfrid","Skardol","Skardom","Skat","Skaus","Skeamond","Skech","Skeird","Skelacred","Skeland","Skerrach","Skien","Skilag","Skiraf","Skoawyn","Skoiv","Skynn","Skysh","Sytram","Taoder","Taretram","Teadan","Telann","Telin","Terralath","Tha","Thaledric","Thaledus","Thardowyth","Tharenydd","Thea","Theinnor","Theip","Theliron","Thelivudd","Thenyth","Thetram","Thie","Thieth","Thigolith","Thilad","Thilalath","Thilil","Thililoth","Thinn","Thirac","Thiresean","Tho","Thoadan","Thoe","Thoinyth","Tholoth","Thu","Thunidd","Tiannor","Tigowyr","Tiliseth","Tioth","Tira","Toch","Toican","Tonwan","Torewan","Traliwyr","Trau","Treadus","Treider","Treliran","Trendalgrin","Triadric","Troedon","Tryand","Trynnor","Tygan","Vali","Vaoldan","Vareloth","Vayn","Vendadan","Vigomond","Viractred","Virawyth","Vith","Viwyth","Voawyn","Vorewin","Waedus","Waeld","Waend","Waenidd","Waerd","Wagan","Wardoder","Wardolgrin","Wardoth","Warewan","Warewyn","Way","Weab","Weabaen","Wealath","Wiar","Wiawan","Wicectred","Wicend","Wicerand","Wicerraldric","Wicerrav","Wicigovudd","Wiciretrem","Wiconnon","Wicore","Wicygord","Wiewyth","Wilawyr","Wili","Wiliron","Wio","Wiralgrin","Woacon","Woanyth","Woewyr","Woild","Worelin","Worem","Wowan","Yale","Yalecred","Yare","Yaug","Yaulath","Ybael","Ybaew","Ybarecan","Ybaron","Ybayder","Ybeard","Ybeas","Ybeican","Ybelimma","Ybila","Ybilic","Ybioloth","Ybira","Ybirawin","Ybivudd","Yboer","Yeanad","Yeig","Yelald","Yerraand","Yiwyr","Yoelgrin","Yore","Yoren","Zaet","Zalesean","Zaligord","Zardoand","Zardoctred","Zayran","Zeadus","Zeanad","Zendactred","Zerader","Zigoa","Zirabwyn","Zoann","Zoenwan","Zumar","Carem","Dyseth","Ferra","Sevolith"]

# The really long list of last names.
lastNamesList = ["Aaliv","Abauvudd","Abay","Aberacan","Aberinyth","Abi","Abiac","Abialgrin","Abiatlan","Abicon","Abilinyth","Aboe","Aboer","Abyder","Abyrd","Acalia","Acardodric","Acardowin","Acaymos","Acayrd","Acelac","Acelach","Acelitrem","Acerisean","Acerracan","Acerrach","Acerrav","Acerraw","Acili","Acob","Acu","Ada","Adalith","Adardol","Adaycan","Aderan","Aderash","Adewyr","Adilim","Adimma","Adiob","Adiracred","Adire","Adiremond","Adoanwan","Adoelgrin","Adoisean","Adoren","Adra","Adreavudd","Adrerram","Adridan","Adrienyth","Adrigowyn","Adrirac","Adrirasean","Adrirath","Adronwan","Adroregan","Adrutrem","Aduld","Adwao","Adwarerd","Adway","Adweacred","Adwean","Adweinad","Adwiragord","Adwoc","Adwoeldric","Aeanydd","Aeit","Aelawin","Afaleth","Afeilin","Afidon","Afilatlan","Afirerd","Afiwyn","Afoabard","Afynidd","Afyv","Agralel","Agrales","Agrawyn","Agrayran","Agraysh","Agrea","Agrerand","Agrigonnon","Agrio","Agriralath","Agroennon","Agroish","Agroitrem","Agrorectred","Agroref","Aie","Aiech","Ailig","Airanidd","Airelith","Airesean","Alaemma","Alaetrem","Alalim","Alaowyr","Alarecred","Alarew","Alauwin","Alawyth","Alayg","Alayr","Alaywin","Aleamas","Aleratrem","Aliamar","Aligogord","Aligoseth","Aliliwyn","Alio","Alirebaen","Alirewyth","Aloedfrid","Aoetha","Aralenn","Araliwan","Arardord","Aratha","Areagord","Arelawan","Arerra","Arerratram","Arewan","Ariawyn","Ariemos","Arind","Aroald","Aroald","Aroia","Arorelgrin","Asaonidd","Asaunnon","Aseiwyn","Aseliwyr","Asia","Asietram","Asigosean","Asilinn","Asiotha","Asiov","Asoe","Asteaand","Astelitram","Astendab","Astewyn","Astiel","Astilaloth","Astioth","Astira","Astiralith","Astirawyr","Astirenad","Astorenwan","Asuron","Asuth","Asylith","Bardoldan","Bardoloth","Barenydd","Bat","Baynidd","Bebaen","Beia","Berabard","Beranwan","Beratlan","Bilawyr","Bilic","Bioctred","Boeloth","Boi","Braelgrin","Braudan","Brawyn","Breawyr","Brelab","Brera","Brerili","Brerish","Breriwan","Brilap","Briodon","Brirabwyn","Brirand","Brire","Broacan","Brodric","Brolgrin","Cab","Cadaesean","Cadaref","Cadeatlan","Cadera","Cadioand","Cadior","Cadiradan","Cadirag","Cadireld","Caeb","Caedric","Caesh","Cale","Cale","Caleloth","Caletlan","Caliwan","Caoch","Caodric","Cardonnon","Cardov","Caredus","Careli","Carenad","Carewin","Cat","Cayb","Ceac","Ceacan","Cealath","Ceand","Ceanyth","Ceav","Ceif","Ceith","Celdan","Celicon","Celictred","Celilith","Cendam","Cendaran","Cenwan","Ceragan","Cerinnon","Chaesh","Chaomar","Chardog","Chardowyr","Chauand","Cheanidd","Chelinwan","Cheriron","Chiadus","Chigoand","Chua","Chyn","Cider","Cieloth","Cienad","Cienwan","Cirach","Cirali","Coeand","Coiwyn","Cowyn","Craeb","Cranad","Crardond","Craret","Crela","Cri","Crirannon","Criretrem","Croenn","Cudfrid","Cyl","Cyran","Cyran","Dalili","Daulath","Delip","Deriwyr","Derrann","Derrannon","Dilal","Dore","Dorennon","Drae","Drayseth","Dreadfrid","Dreav","Dreld","Dreramas","Dreri","Drerralgrin","Drilard","Drilat","Drirawin","Dromas","Drush","Drycon","Dwaeg","Dwaeloth","Dwaewan","Dwalelin","Dwaobard","Dwardowin","Dweasean","Dwes","Dwigolgrin","Dwilimos","Dwiodric","Dwireldan","Dwireldric","Dwoa","Dwoagord","Dwonwan","Dydfrid","Dynn","Edaedon","Edaesean","Edaeseth","Edawyr","Edeaf","Ederawyn","Ederrann","Edilamar","Edilibard","Edilic","Ediramma","Edoa","Edul","Elaowin","Elardotram","Elaynnon","Eleald","Eleanwan","Eleid","Elelat","Elendadfrid","Elerisean","Elialoth","Elie","Eliem","Elioron","Eowae","Eowaem","Eowaleldan","Eowaunwan","Eowaym","Eoweat","Eowegord","Eoweish","Eowelatha","Eoweravudd","Eowerrard","Eowevudd","Eowiewyr","Eowilamond","Eowoild","Eoworedus","Eoworep","Erardoli","Erardond","Eraunwan","Ereinidd","Ereitha","Erelic","Erend","Ereratha","Ererinn","Eribwyn","Eriladfrid","Eroidfrid","Erolgrin","Eta","Etardom","Etaya","Eterild","Ethaecon","Ethaen","Ethaenydd","Ethaer","Ethalel","Etharelin","Ethialgrin","Ethibard","Ethigodon","Ethirawyn","Ethoannon","Ethoend","Ethoetrem","Ethorewin","Ethulath","Ethylgrin","Etiradfrid","Etirasean","Etiw","Etoadric","Etymma","Etyvudd","Faennon","Falinnor","Faup","Feannon","Fec","Fei","Felasean","Feran","Ferrab","Ferrann","Fiabard","Filic","Firadric","Firemond","Fow","Fraech","Fraleb","Fraligord","Fraref","Frarelgrin","Freac","Frealdan","Frerra","Frerragan","Frigor","Frorebwyn","Frusean","Frut","Galale","Galalewin","Galares","Galaut","Galeatram","Galebwyn","Galenda","Galerimas","Galerimma","Gales","Galie","Galim","Galimond","Galoilath","Galoili","Galudan","Galuli","Gaogan","Gayloth","Geanwan","Gelip","Gendavudd","Geri","Giatrem","Giewin","Gilawyn","Giosean","Glaowyn","Gleamas","Gleder","Glilil","Gliotrem","Glirawan","Gloav","Goan","Graesean","Grale","Graleb","Gralebaen","Gralitlan","Graywyn","Grela","Grelaran","Grendac","Greraldric","Grerratrem","Grerrawyn","Griawyn","Grilacred","Griog","Griol","Groremas","Gruand","Gwae","Gwaumas","Gwayc","Gweamma","Gweannon","Gweivudd","Gwennor","Gwerich","Gweriwin","Gwiovudd","Gwirecan","Gwydalemos","Gwydaymos","Gwydeinad","Gwydeinwan","Gwydera","Gwydevudd","Gwydigof","Gwydilalgrin","Gwydirab","Gwyditlan","Gwydoali","Gwydoeder","Gwydyron","Gwydyseth","Haali","Haalimar","Haalith","Haead","Haeral","Hai","Haiaa","Hailiwyr","Hairadan","Halef","Haodric","Hardobard","Haumma","Haunwan","Haus","Hauv","Hauwyr","Hauwyr","Hayth","Helaseth","Hief","Hirap","Hirewyth","Ibaech","Ibaevudd","Ibaloth","Ibaoder","Ibardobaen","Ibaywan","Ibeac","Ibeap","Ibecon","Ibeiwin","Ibeligord","Iberinidd","Iberra","Ibieloth","Ibigos","Ibilaldric","Ibilav","Ibith","Iboimma","Iboith","Jeraesean","Jerardolith","Jereabard","Jereiwyn","Jerelil","Jereraran","Jerewin","Jerila","Jerilawyr","Jeriliwyn","Jeriramos","Jeroewin","Jerorevudd","Kaei","Kaelad","Kaem","Kaew","Kaigotlan","Kailili","Kailiwan","Kaioand","Kand","Kaoebard","Kaoidric","Kaoldan","Kaomma","Kardonn","Kardotram","Keagord","Kedadan","Kedalecan","Kedardoch","Kedealgrin","Kedenn","Kedenyth","Kederaran","Kederranad","Kedieldric","Kedigos","Kedilawin","Kedilind","Kediomma","Kediralin","Kediranyth","Kedow","Keduwin","Kelilgrin","Kendas","Kerilin","Kerraldric","Kigocred","Kirash","Koavudd","Korewyr","La","Laem","Laraeran","Laraond","Larareder","Lared","Larelider","Laremas","Lariegan","Larigold","Larigoth","Larun","Larywin","Legacan","Legaelith","Legalemond","Legalewyth","Legalildric","Legeivudd","Legeril","Legeriloth","Legiaseth","Legionad","Legoawin","Legoidus","Legoiwyn","Legunn","Leridfrid","Lev","Lilawin","Liliwan","Liragord","Lirawin","Loa","Loacred","Lothadfrid","Lothaeth","Lotharemar","Lothawyth","Lothaydon","Lothendagord","Lothieder","Lothigoder","Lothira","Lothiradon","Lothirev","Lothoali","Lothore","Lothoreth","Lygord","Maewyn","Maleloth","Malia","Mardoc","Mardoc","Maus","May","Meimas","Merrawin","Milav","Mimma","Mioseth","Miradus","Miralibwyn","Miraliwyr","Miraodon","Miraron","Miraron","Mirelil","Mirew","Miriec","Miriwyn","Miroewan","Mirored","Moiwin","Moretha","Mubaen","Muwyr","Naebwyn","Nael","Naerd","Naetram","Nayc","Neadan","Neannor","Nelam","Nelawyn","Neraldric","Nerra","Nilar","Nirald","Noader","Noaf","Nyda","Nydaer","Nydao","Nydardord","Nydaudus","Nydauldan","Nydauwyr","Nydaydus","Nydilatlan","Nydiresean","Nymma","Ocalewyn","Ocaum","Oceil","Ocelinyth","Oceriw","Ocerran","Ociand","Ocigogan","Ocigotram","Ociord","Ociowan","Ocoagan","Ocoidus","Ocuwyn","Olalif","Olam","Olare","Oleabaen","Olerradon","Olia","Oliamond","Olican","Oligowan","Olilatram","Olilil","Olirea","Oliremar","Oloabaen","Oloadus","Olotram","Oly","Onaot","Onaretrem","Oneth","Onirald","Onirenidd","Onuctred","Pabard","Pabwyn","Paelin","Palibard","Parec","Pei","Pela","Pendanwan","Periwyr","Pied","Pield","Pigoldan","Pigowyn","Pio","Ponnon","Poredon","Praen","Praf","Praowyth","Prau","Prau","Prendagan","Prera","Preradon","Prerrag","Priracon","Prirad","Proawyr","Proew","Pruch","Pywyn","Ra","Raath","Raaunwan","Raayd","Raeacan","Raeamma","Railin","Rairan","Raocon","Raoep","Raonydd","Raywyr","Rerrann","Rerrasean","Rhael","Rhaevudd","Rhale","Rhaleloth","Rhalip","Rhalith","Rhardowyth","Rharew","Rheanydd","Rheider","Rheli","Rhendawan","Rherim","Rhiath","Rhilibwyn","Rhiligan","Rhiramma","Rhoimond","Rhoinyth","Rilacred","Rilith","Rired","Roaw","Roemma","Rum","Rymma","Sauder","Sea","Seris","Sevaerd","Sevardoctred","Sevardow","Severamma","Severiwyr","Severra","Seviacon","Seviar","Sevilatha","Sevilit","Seviwan","Sevoanidd","Sevof","Sevoidan","Sevor","Sevywyn","Siab","Sian","Sigotram","Siranwan","Sireldan","Skalesh","Skamos","Skaonad","Skaug","Skeaseth","Skerigan","Skeritha","Skerrash","Skiann","Skicon","Skigoc","Skigomos","Skilimas","Skoaw","Skoind","Taea","Taebwyn","Talemma","Talenn","Taoctred","Taredan","Tealin","Teard","Teritha","Tharewyth","Thauwan","Theac","Theam","Theamma","Theamond","Theas","Thelird","Thendalath","Thendawyn","Therath","Theril","Theriwyn","Therrawyth","Thierd","Thilanad","Thilictred","Thiracan","Thiralin","Thiralin","Thish","Thoaloth","Thoegan","Thoen","Thoiwyr","Thol","Tidric","Tilan","Tilawyn","Tirash","Toloth","Toreldan","Traeran","Tralelgrin","Traliwin","Trardomar","Trayldric","Treanyth","Trendadon","Trendaron","Trerimar","Triewyn","Trilish","Trirabard","Tro","Troab","Troald","Tronyth","Trunnon","Valith","Vardowyn","Varon","Veladon","Verawin","Vioc","Viseth","Voim","Voremond","Walecred","Walin","Wao","Watlan","Waunnon","Wawyn","We","Weadan","Wean","Weath","Weiloth","Welam","Welawyn","Welimma","Welin","Werimma","Werinyth","Werraf","Werraldric","Werrawyr","Wicaedus","Wicauld","Wiceith","Wicela","Wicelaron","Wicendab","Wicennon","Wicira","Wiciranyth","Wicobaen","Wicoeld","Wicoilin","Wicold","Wicoreld","Wicudric","Wietram","Wilinwan","Woech","Woidon","Wudric","Yaesh","Yaoldric","Yaylith","Ybalinnon","Ybardoc","Ybardosean","Ybardoseth","Ybardotlan","Ybauwyn","Ybayand","Ybea","Ybeac","Ybiaand","Ybireder","Ybiredon","Ybo","Yean","Yelinydd","Yigo","Yililoth","Yiram","Yoremma","Zaledon","Zaliwyr","Zaomos","Zaremos","Zaycred","Zaycred","Zelinn","Zerab","Zigoldan","Zigovudd","Zionyth","Ziord","Ziramma","Zoilath","Zup","Aalig","Aaliwyn","Aarewyr","Aayld","Abardodus","Abarend","Abay","Abe","Abend","Aberrab","Abigoand","Abilach","Abytha","Acaemma","Acaytram","Aceis","Aceralath","Acilat","Acili","Acywyn","Adadon","Adaecan","Adaenad","Adaybwyn","Adeactred","Adendasean","Adigolgrin","Adiomma","Adirald","Adoreloth","Adraeran","Adrale","Adrarenyth","Adreldric","Adrelicred","Adrelin","Adremos","Adreris","Adrerrad","Adrigoch","Adrigom","Adrigop","Adriradfrid","Adrirann","Adrirectred","Adroenwan","Adroiron","Aduwyr","Adwaegan","Adwalewyn","Adwalewyr","Adwaligord","Adwalild","Adwardowyn","Adwaynad","Adwerach","Adwim","Adwirebard","Adwirelgrin","Adwoamar","Adwoeron","Adwoitrem","Aeild","Aeind","Aelag","Aelan","Aendasean","Aerranyth","Aerrawyn","Aev","Afalerd","Afaoa","Afeald","Afeatram","Afeiand","Aferatram","Aferi","Aferraldric","Aferranidd","Afiadon","Afier","Afieran","Afiobard","Afiotram","Afireg","Afo","Afogan","Afotlan","Afub","Afugord","Agra","Agralili","Agraretrem","Agrauwan","Agreish","Agreith","Agrerildan","Agreritrem","Agriranad","Agrirawan","Agroivudd","Agroredfrid","Agrudus","Ailash","Airaa","Alamma","Alaoseth","Alardoder","Alautlan","Aleanyth","Alerratrem","Aliamond","Aliawyr","Aligond","Aligonydd","Aloedfrid","Aloib","Alylath","Aoef","Aoredus","Araet","Arar","Aray","Araycon","Areamond","Arelitrem","Arerrali","Arigo","Ariras","Aroam","Aroe","Aroeldric","Asaenad","Asaogord","Asaresean","Asauand","Asawan","Aseabard","Aseagan","Asearon","Aseliv","Asia","Asigoctred","Asigowin","Asin","Asoewyr","Astalea","Astendal","Asterrader","Astiratha","Astoaa","Astoldan","Astoreth","Astuder","Asysh","Asyt","Aydan","Badus","Baech","Barewin","Beliwin","Beliwyr","Bendawyr","Berrawyn","Biactred","Biawyr","Biecon","Bird","Boaron","Brabard","Bradfrid","Braed","Braetha","Braletrem","Braowyn","Breamos","Breilath","Brendadon","Brerimond","Briawin","Brigovudd","Brilamos","Briralith","Broalith","Broemma","Broenad","Brorennon","Brudon","Brup","Caand","Cadaem","Cadalennor","Cadaog","Cadardomas","Cadeader","Cadeal","Cadelamma","Cadelan","Caderrawyr","Cadiligord","Cadilinad","Cadiocon","Cadiord","Cadios","Cadoap","Cadoas","Cadoid","Cadoili","Cadoran","Cadud","Cae","Caea","Caegan","Calecon","Calider","Calili","Calinidd","Caoc","Cardoron","Carecan","Carewyth","Cea","Cealdric","Ceatram","Celidric","Celili","Ceri","Ceriand","Cerif","Cerildan","Cerildan","Cerimas","Cerragord","Cewyr","Chaedric","Chalilgrin","Chaliw","Chardonwan","Cheawyn","Chemar","Chemond","Cheth","Chiadric","Chiland","Chiligord","Chirawyth","Chyth","Ciath","Cierd","Cionidd","Cirav","Coeth","Coild","Craom","Crardotrem","Creaseth","Creatrem","Crelicon","Crerader","Criald","Crilith","Croadon","Croedric","Crorebaen","Cua","Culoth","Cydon","Daelgrin","Daobwyn","Dauand","Deap","Deif","Delab","Derawin","Die","Dild","Dom","Dra","Draliand","Draotlan","Drap","Drarelith","Drera","Drewin","Driabaen","Drigodan","Drirash","Drireldan","Driremas","Du","Duloth","Dwaedfrid","Dwalewan","Dwalith","Dwaregan","Dweird","Dwemar","Dwendanidd","Dwiabwyn","Dwicon","Dwigodric","Dwiliran","Dwirad","Dwire","Dwoatlan","Dwoemma","Dworewyr","Eda","Edaygan","Edealath","Edeanad","Edeavudd","Edeim","Edelatha","Edelinidd","Ediaron","Edidan","Edierd","Ediliv","Edird","Edoinnon","Edolith","Elaemos","Elaregord","Elealdric","Eleann","Eleild","Eleli","Elendab","Elialath","Eligoch","Elinnor","Elirader","Elirath","Elorec","Elus","Elygord","Eowaelin","Eowaem","Eowela","Eoweri","Eowield","Eowigowin","Eowiland","Eowoecan","Eraenad","Erarenwan","Erea","Ereli","Erelildric","Ereridric","Ererraw","Eridus","Erirannor","Eroav","Eroreth","Erya","Eryctred","Etaledan","Etanwan","Etaob","Etaov","Etarewyth","Eteamas","Eteli","Eteligan","Etendad","Etendaldan","Ethaelith","Ethalenyth","Ethaomma","Ethareth","Ethaytram","Etheli","Etheridric","Etherramas","Ethilac","Ethiligord","Ethilil","Ethilip","Ethiold","Ethoeand","Ethorebwyn","Ethoreld","Ethov","Etiann","Etilitrem","Etirecan","Etoerd","Etoibwyn","Etoinnor","Etorecon","Faecon","Faer","Falennor","Fardolath","Fardow","Faren","Fareth","Feria","Ferran","Fi","Fiemar","Figoth","Filic","Filitha","Fiogord","Firec","Fodan","Foeli","Frarebaen","Frau","Frealath","Frei","Frilaa","Frirand","Froesean","Froitlan","Froitrem","Fromar","Froremos","Fruvudd","Fryseth","Fusean","Gaeldan","Galaegan","Galalelin","Galayran","Galeamma","Galeanydd","Galerald","Galerilin","Galerrabwyn","Galerraldric","Galigo","Galigonidd","Galiotlan","Galoev","Galoiw","Galulin","Garem","Gaw","Geider","Gelawyn","Gelidus","Geradus","Gerradon","Giamma","Giral","Gireldan","Girenyth","Glalecan","Glaliwan","Glaom","Glarenad","Glelawin","Glelimond","Glelis","Glerab","Gligobwyn","Gligonad","Glilacan","Gliliron","Gliw","Gloavudd","Glocan","Gluder","Gluf","Goawin","Graeron","Graewyr","Grelab","Grie","Griebwyn","Grigobaen","Grynnon","Grysh","Gwaleb","Gwalith","Gwenad","Gwendatram","Gwerimond","Gwiewyn","Gwigoli","Gwigowan","Gwydalectred","Gwydardoder","Gwydauwyr","Gwydays","Gwydeard","Gwydeatlan","Gwyderap","Gwyderrann","Gwydieand","Gwydiladus","Gwydira","Gwydoes","Gwydorewyr","Gwyducan","Gyseth","Haaelith","Haaliw","Haep","Haietlan","Hailabard","Haili","Haionwan","Hairawyr","Haireldric","Haish","Haleli","Haliwyr","Haoan","Haobaen","Hare","Heican","Helabwyn","Helatha","Hiramond","Hoawyn","Hoinad","Horeran","Hylgrin","Ibalenad","Ibardolath","Ibarewyr","Ibau","Ibeaa","Ibelard","Iberitram","Ibiractred","Ibiraseth","Ibocred","Iboelith","Iboemar","Iboewan","Iboiwyr","Jeraeth","Jeraren","Jerautha","Jeredfrid","Jerelid","Jereliron","Jererawyn","Jererratram","Jerien","Jerilinyth","Jerio","Jerirawin","Jerirep","Kaaectred","Kaaliw","Kaann","Kaardowyr","Kaaret","Kaaywyn","Kaedus","Kaeiand","Kaeiwyr","Kaendawan","Kaeracon","Kaerimond","Kailasean","Kamas","Kaoiv","Karelgrin","Karelith","Kean","Kedach","Kedal","Kedardo","Kedarerd","Kedawin","Kedawyth","Kederap","Kederican","Kederratlan","Kedigog","Kedigor","Kedigoth","Kedoesean","Kedoiloth","Kelinn","Kerinn","Keriwyr","Kian","Kianidd","Kilidon","Koin","Kore","Kud","Lalebard","Lalem","Lalewan","Lali","Lalit","Laliv","Laralibaen","Larardodan","Lardodon","Lareradan","Lareraldric","Larerican","Larerrabaen","Lareseth","Lariratrem","Larut","Lau","Leap","Legacred","Legaecon","Legalewyn","Legalidan","Legardosh","Legerali","Legieli","Legigonydd","Legiracred","Legireg","Lendadan","Lenyth","Lerad","Lerra","Lerra","Liad","Liav","Liebard","Lilatrem","Lior","Lir","Lirel","Loas","Loregan","Lothaleran","Lothebard","Lothidric","Lothigop","Lothilaldan","Lothiraw","Lothomma","Lothulin","Mare","Mau","Me","Meaa","Meildan","Melin","Merra","Merrald","Miliwyr","Mirab","Mirae","Miralin","Miraynnon","Mirecan","Mirelgrin","Mireradon","Mirerand","Mirian","Miriliw","Miriranydd","Miroebaen","Miroewin","Mirurd","Moreand","Nae","Naew","Nean","Nedon","Nela","Nelig","Niamar","Nier","Nilawin","Niobwyn","Noamos","Nydaectred","Nydaoran","Nydardotrem","Nydarenn","Nydaytram","Nydeawan","Nyderitha","Nydi","Nydiald","Nydieldric","Nydilidus","Nydirawyth","Nydoch","Nydoibard","Nydul","Ocaen","Ocarecan","Ocealoth","Oceiwyn","Ociald","Ocialdric","Ocigoand","Ocilicred","Ocoath","Ocod","Olalenidd","Olardo","Olardosh","Olarea","Olaudfrid","Oleidric","Oleiw","Olendamar","Oloemos","Oloetrem","Olos","Oluvudd","Onadfrid","Onaedon","Onaeldan","Onaliwyr","Onardonidd","Onarebaen","Onaymas","Onerim","Onigosh","Onilibaen","Oniowan","Oniradon","Onoawyr","Onof","Onu","Onynnon","Paleth","Palith","Parech","Peadfrid","Pendannor","Pendaran","Peracon","Perawin","Piaa","Pilisean","Pirawin","Pith","Poiand","Pomos","Ponad","Praowyn","Prea","Preinydd","Prelaron","Prelif","Prendatha","Priath","Priavudd","Pricred","Prila","Prira","Priradon","Prirath","Prirav","Prit","Progan","Prorebwyn","Prydan","Raaewyr","Raalerd","Raalig","Raan","Rabwyn","Raea","Raeth","Raianwan","Raicred","Raierd","Raigodan","Raocred","Raoegord","Rardom","Raylin","Raywin","Relawyn","Rhalimond","Rhardo","Rharewin","Rhay","Rhelild","Rheramond","Rheritrem","Rhiewyr","Rhoa","Rhoawyn","Rhoinydd","Rhyn","Rieloth","Riem","Rieth","Riliwan","Roag","Roanidd","Ry","Rysean","Saedan","Saleran","Saleran","Saol","Seabwyn","Seanyth","Seavudd","Selath","Serasean","Seriron","Serragan","Sevaemond","Sevaolath","Sevaot","Sevardo","Sevardord","Sevaynyth","Seveactred","Sevendad","Severan","Seviactred","Sevirar","Sevytlan","Siewin","Sigoldan","Siraw","Skaemar","Skawin","Skelacon","Skeralgrin","Skicred","Skiladan","Skilanyth","Skirawin","Skirenyth","Skiwin","Skunnor","Soedan","Soinwan","Sylath","Sytram","Taebwyn","Taectred","Taer","Taret","Teidus","Teri","Teriwyn","Thael","Thaemos","Thaewin","Thalel","Thalemma","Thaotlan","Thardonn","Tharedon","Thaugord","Thaulin","Thaylith","Thaytha","Theav","Theawyn","Theiwan","Thelacan","Thelil","Thendan","Thendatrem","Therand","Theri","Therra","Thia","Thigob","Thigomos","Thigowin","Thilar","Thiotrem","Thirag","Thoach","Thoenydd","Thog","Thoiloth","Thoinn","Thyn","Tilawin","Tilinidd","Tilit","Tiol","Titrem","Toaw","Torewyn","Traucon","Treamond","Treidon","Trelagan","Treliand","Triawyr","Trilag","Troemar","Truwyth","Vaedon","Valewyn","Vaubwyn","Vayg","Veliwin","Verawyn","Via","Vigo","Virabwyn","Viracon","Voa","Vynyth","Wader","Wadfrid","Waev","Wale","Wale","Walilith","Waliwin","Wardotlan","Wardov","Waylath","Waytha","Weitlan","Welinnor","Wemma","Weracred","Weratrem","Werrash","Wi","Wiaa","Wicalitha","Wicaregan","Wicaylin","Wicea","Wiceadric","Wiceilith","Wicilat","Wicilican","Wicuron","Wiliran","Wirat","Wireron","Woelith","Woreli","Wyld","Yaennon","Yaunnon","Yayldric","Ybaleli","Ybaobwyn","Ybaonnor","Ybeilith","Ybelilath","Yberadon","Ybianyth","Ybiatrem","Ybioldric","Ybirac","Ybiradric","Ybirar","Yboer","Yboeran","Yeanad","Yela","Yelash","Yendanwan","Yerrac","Yiadfrid","Yirash","Yiref","Yiw","Yiwyth","Yoaf","Yoannon","Yoawyn","Yoewan","Yorew","Yulin","Yyand","Yydric","Yyv","Zadfrid","Zalea","Zamas","Zeamond","Zean","Zeladon","Zerader","Zeribaen","Zeridus","Ziend","Zilamar","Zilgrin","Zili","Zio","Zior","Ziraand","Ziralin","Zof","Zoican","Aaef","Aaem","Aardocan","Aardotrem","Abalit","Abalith","Abeach","Abean","Abelider","Aberabaen","Aberaloth","Abiolin","Abiracan","Abiraran","Aboibaen","Acalith","Acardowyth","Acarem","Acaycan","Aceladric","Acerrar","Acia","Acoiwin","Acowin","Acuv","Adaewin","Adaleron","Adalim","Adeaf","Aderon","Aderrap","Adilash","Adiredan","Adoal","Adoali","Adoanydd","Adraedon","Adralird","Adraodan","Adrenda","Adrigonyth","Adriracan","Adriracon","Adrirenad","Adroanyth","Adroemma","Adrutrem","Adwaebaen","Adwardoctred","Adwardonidd","Adwaynnon","Adwendab","Adwiemas","Adwietram","Adwigodus","Adwiocred","Adwiredon","Adwirennon","Adwoenn","Adwuld","Aeanad","Aeladfrid","Aeritha","Aerramar","Aerranidd","Afaenidd","Afaoch","Afardowyn","Afei","Afelaf","Afireg","Afirewyn","Afu","Agraer","Agraudric","Agrayldan","Agreanwan","Agreramond","Agrieli","Agru","Agruwin","Agrywin","Ailach","Ailif","Ailiwyn","Airag","Airesh","Aliemond","Aliraldric","Aloildric","Aloiwyr","Alomma","Aoeseth","Aoid","Aoith","Aoredon","Arardodfrid","Areilith","Arelgrin","Arendabard","Areramar","Ariol","Ariowyth","Arirawin","Arireseth","Aroadus","Aroremond","Arowyth","Asaotlan","Asardodus","Asaunidd","Aseadus","Aseliv","Aserrawyth","Asianad","Asildric","Asinnon","Asiraran","Asoeli","Astae","Astaedfrid","Astarelith","Asteatrem","Astei","Asteiwyth","Asterabard","Asterild","Astilanidd","Astiramma","Astitlan","Astorec","Astoreder","Astoredfrid","Astuwyr","Asuldan","Aumos","Ayl","Baomma","Bath","Beamar","Beitram","Bi","Bia","Bigov","Bilam","Birawyr","Birewyth","Bolath","Braenydd","Braleld","Brardon","Brelamas","Briesh","Broenidd","Broiw","Bryld","Bynd","Cadalelath","Cadaoseth","Cadarev","Cadauld","Cadaygord","Caderi","Caderir","Cadiogord","Cadireseth","Cadoaseth","Cadoinad","Cadoremma","Cadumar","Cadysean","Caeth","Cali","Calidon","Cam","Caof","Cardodon","Cardotrem","Cau","Cau","Cay","Cay","Caydus","Caysh","Ceaand","Ceamond","Ceaseth","Ceig","Celaa","Celi","Cerath","Cerinyth","Cerraa","Cerrannor","Chaenad","Chaewyn","Chaleb","Chaus","Chaydus","Cheligord","Chendath","Chigotrem","Chilib","Chiowyn","Chirath","Chirenwan","Chiwin","Choabaen","Choren","Chyth","Ciash","Ciawin","Cigob","Cilacan","Cilacred","Cirac","Ciran","Cirath","Cire","Cirewan","Coanad","Coatrem","Coe","Crao","Craredus","Crelaw","Crerasean","Crilidric","Crireli","Croamma","Croewan","Cywin","Cywin","Dardoth","Daresh","Delaand","Derannon","Derractred","Dibard","Digop","Dilic","Diram","Doanydd","Doel","Doildric","Doiv","Draen","Dralennor","Dralicon","Drardowin","Dreili","Dreiwin","Drericred","Droasean","Dru","Drul","Drynad","Drysh","Du","Dund","Duw","Dwaetlan","Dwalebard","Dwaleseth","Dwalimos","Dwayd","Dweamos","Dwelabwyn","Dwerap","Dwerild","Dwerrac","Dwev","Dwilimas","Dwoiseth","Dwold","Dwolith","Dworenidd","Dwuwin","Dwyldric","Edaegan","Edaemma","Edaledric","Edalemma","Edeild","Edelider","Edera","Edila","Edilith","Ediramond","Edoannon","Eduf","Elalidus","Elarev","Elauwyr","Elelidric","Elelip","Elendaa","Elerican","Elieb","Elila","Eliol","Eliralith","Elirav","Eloabwyn","Elodus","Elonyth","Eluf","Eowaer","Eowardo","Eowarenydd","Eowauld","Eowelir","Eowerradus","Eowesean","Eowiamond","Eowich","Eowieth","Eowildan","Eowiremar","Eowo","Eowoalgrin","Eowug","Erae","Eraea","Eralgrin","Eralich","Erardodric","Eraredan","Erarem","Eraynnon","Ereinidd","Ereliwyr","Erendannor","Ererrawyn","Eria","Eriev","Erigoc","Erilaldan","Erirath","Erocred","Etaebaen","Etaew","Etarebard","Etareld","Etat","Etelildric","Eterawin","Etha","Ethaesh","Ethaev","Ethalecon","Ethalinnon","Etheabaen","Etheawyth","Ethelidfrid","Ethemas","Ethendath","Ethie","Ethiraf","Ethiramas","Ethoia","Ethold","Ethoregan","Etilicon","Etirenidd","Etoamond","Etoemas","Etoretrem","Etu","Ety","Falegord","Fardotlan","Fardowyn","Favudd","Feaand","Feisean","Fendawyr","Ferrabard","Foash","Forea","Foregan","Freawan","Frerildan","Friali","Friaseth","Friew","Frilimas","Frionnon","Frirabwyn","Frirath","Frireg","Froawyn","Froiron","Gae","Galaelin","Galalinidd","Galaolgrin","Galaolin","Galarebwyn","Galaynnon","Galed","Galianwan","Galibwyn","Galicon","Galiodon","Galirag","Galoab","Galoidric","Galoli","Galowyn","Galus","Gardoc","Gardoth","Gareseth","Gau","Gausean","Gauwyr","Geanyth","Gelildan","Gendach","Geramar","Giosh","Girewyr","Glaesh","Glauseth","Glayron","Gleacon","Gleadus","Gleand","Gleif","Glera","Glerar","Gliawyn","Glirenyth","Gloeand","Gloeld","Gloelin","Gloind","Gloretha","Glynnor","Goe","Graelath","Grali","Graoc","Graumond","Grawyth","Graydon","Gre","Greard","Grieldric","Grilanwan","Grinwan","Groewyn","Gru","Grywyn","Guwyth","Gwag","Gwareldric","Gwath","Gwaylin","Gwelan","Gwelath","Gweliand","Gweliv","Gwendadfrid","Gwior","Gwiralin","Gwirannon","Gwoader","Gwoamond","Gwoevudd","Gwomar","Gwydae","Gwydaeder","Gwydalenad","Gwydao","Gwydaowyr","Gwydeasean","Gwydeb","Gwydew","Gwydili","Gwydilitrem","Gwydirawyr","Gymar","Haaewyn","Haaun","Haegan","Haelanwan","Haerad","Haetrem","Hales","Haligord","Haliwyth","Haoatram","Haoilgrin","Haowyth","Haulath","Hayw","Heagord","Heat","Hedus","Helann","Herabaen","Heractred","Heramas","Hiag","Hiold","Hireldan","Hirem","Hoadan","Hoech","Hoiron","Hoith","Horeg","Hubwyn","Hunnor","Huth","Iba","Ibaelith","Ibale","Ibaomond","Ibeam","Ibeannor","Ibeinidd","Ibelagord","Ibeliseth","Iberaf","Ibigolath","Ibila","Ibilacon","Ibilild","Ibinnon","Ibirald","Ibireand","Iboi","Iboitrem","Ibowyr","Jeraliwyth","Jeraoch","Jerealoth","Jeriegan","Jerilan","Jeriodric","Jeriremma","Jeroeb","Jeroretlan","Jerudric","Jeryn","Kaawyr","Kaeaa","Kaegan","Kaeilgrin","Kaerild","Kaerrawin","Kaiawyth","Kaili","Kain","Kaind","Kairamas","Kardowin","Kauctred","Kaynwan","Kaywyn","Kedaen","Kedalebard","Kedaord","Kedardolin","Kedeadus","Kedeagan","Kederrawin","Kedialith","Kediranidd","Kediregan","Kedoem","Kedoidfrid","Kedorewin","Keican","Keiseth","Keriwin","Korelith","Kybard","Lad","Lalenn","Lalesean","Laow","Laraliw","Lareabaen","Lareamos","Lareawyn","Larebard","Lareinnor","Larietram","Larilimos","Lariodan","Laromos","Laruch","Laumar","Legae","Legaedon","Legalicon","Legear","Legelavudd","Legendaloth","Legieb","Legiowyn","Legiras","Legireld","Legoectred","Legoinwan","Legycon","Lendaloth","Lias","Liev","Liliwyn","Loidus","Lotham","Lothaoand","Lothau","Lothelinnon","Lothenidd","Lothera","Lotherannor","Lotheratrem","Lotherawin","Lothias","Lothilali","Lothilath","Lothimond","Lothirann","Lothorewyr","Lothyv","Lu","Maeder","Maelith","Malildan","Mauwyn","Mays","Meatlan","Merild","Merrard","Miedan","Migowyth","Milacred","Miop","Miraecon","Miraoch","Mirardolith","Miriolin","Miriraf","Miroeld","Miroictred","Mirorep","Miruc","Mobard","Moim","Morectred","Muld","Mutlan","Nardonad","Nauwyr","Neadan","Nealath","Nigowyn","Niliran","Nish","Noal","Noand","Nydae","Nydaeand","Nydalebwyn","Nydali","Nydardoran","Nydareron","Nydaunwan","Nydaw","Nydeab","Nydeald","Nydeib","Nydelap","Nydeld","Nydenda","Nydiader","Nydiem","Nydieran","Nydilali","Nydiocan","Nydira","Oca","Ocaemar","Ocalinwan","Ocardowyn","Ocarenn","Ocienyth","Ociliv","Ocirann","Ociras","Ociren","Ocirennor","Ocirenwan","Ocoemond","Ocoenidd","Ocow","Oculi","Ocuwan","Olaemar","Olaeth","Olalewyn","Olalil","Olardo","Olaretha","Olauth","Olear","Olerinn","Oliemar","Oligold","Oliligan","Olilimas","Oloder","Oloiwyr","Olowin","Onaemar","Onaemos","Onalewin","Onaoron","Onardonwan","Onead","Onei","Onelawyth","Onia","Oniawyn","Onieth","Onilacan","Onio","Oniosh","Onoawan","Onodric","Onoeth","Pa","Paogord","Paolath","Pardowyth","Paremond","Paylin","Peralath","Perrald","Perrawyth","Pilaron","Pio","Piocred","Pirann","Piravudd","Poacon","Poebard","Prae","Pralinnon","Pralip","Praunidd","Preamond","Preif","Prem","Prendawyn","Preramar","Prerraf","Prierd","Priesean","Prigoand","Prilgrin","Prionydd","Prirannor","Prirawyth","Prish","Proel","Prop","Puwyn","Pynwan","Raardomos","Raenydd","Raerader","Raiawyn","Raimas","Rairawan","Ralew","Raocon","Raore","Rardowin","Rarecan","Rarewyn","Rash","Raydan","Rera","Rhaunydd","Rhawan","Rhayctred","Rheadan","Rheawyn","Rhemma","Rhendanad","Rherath","Rherrard","Rhiadon","Rhilanwan","Rhiobard","Rhior","Rhirash","Rhoinn","Rhoivudd","Riath","Rigodon","Rilamas","Riliseth","Roawan","Roremma","Rywyr","Saewan","Saum","Saymma","Selath","Serraseth","Sevaon","Sevare","Sevareand","Sevauldric","Sevaynad","Sevelinnor","Severalith","Sevib","Sevili","Sevilildric","Seviomos","Seviranydd","Seviraseth","Sevireth","Sevirevudd","Sevoagord","Sevoenad","Sevoimar","Siem","Sieron","Silanad","Silild","Siralith","Sirev","Sirewyr","Skald","Skaleand","Skarep","Skaycred","Skerawan","Skeriwyn","Skiacon","Skiel","Skiev","Skiraldan","Skirewyth","Skoe","Tach","Talidus","Tardo","Tayth","Teis","Telinad","Tendabwyn","Teramas","Terramond","Thaem","Thalenad","Thalep","Thalili","Thardotha","Thareth","Tharewin","Thea","Thea","Thead","Thearon","Theawyn","Theictred","Theili","Thelap","Thendan","Thendatram","Therican","Therid","Thictred","Thilan","Thilanidd","Thiliwan","Thiodfrid","Thirawin","Thiwyr","Tho","Thuwan","Towin","Trae","Tralenwan","Trardold","Trardowyth","Trelab","Trelicon","Treriwyr","Trerraldric","Trerranwan","Triatlan","Trililith","Trirawin","Trireli","Troedric","Tron","Vaes","Valennor","Varewyn","Vaya","Venad","Voelath","Vol","Vorenwan","Wae","Waea","Waectred","Walemond","Walind","Walisean","Wardom","Wea","Weicred","Weliwan","Wendagord","Wendaldan","Wendaldric","Werav","Weritha","Weriwan","Weseth","Wicaliran","Wicarep","Wicelath","Wiceliloth","Wicerawyr","Wiciadric","Wicigon","Wicilath","Wicimos","Wicoali","Wicoeder","Wicord","Wicorelith","Wicunad","Wiecon","Wiewin","Wigolin","Wigovudd","Wilawyr","Wilinn","Wimma","Wiraa","Wiralath","Wiratlan","Wirectred","Witrem","Woesh","Wud","Yaewan","Yay","Yayldan","Ybaucred","Ybaulith","Ybaywin","Yberrawin","Ybialin","Ybiraa","Yboibwyn","Ybuwyr","Ybyr","Yea","Yea","Yendard","Yenidd","Yeraseth","Yili","Yili","Yiowyn","Yuth","Zaetram","Zath","Zauth","Zeaa","Zerir","Zienidd","Zilatha","Zilild","Zilind","Ziog","Zionnor","Zira","Zire","Zirel","Zo","Zoewyth","Zoi","Aacan","Aaer","Aalitlan","Aardo","Aaudan","Aaya","Abale","Abarec","Abatram","Abeand","Abeawyn","Abedan","Abeir","Aberamma","Aberith","Abiawyn","Abilith","Abioth","Abiraloth","Abya","Abytlan","Acaewyr","Acaug","Aceat","Aceimar","Acelash","Acera","Acimas","Aciratlan","Acirenad","Acorenad","Acoresean","Acucred","Aculith","Adabwyn","Adalewin","Adaredan","Adawin","Adealith","Adelalgrin","Adeli","Adelif","Aderiw","Adiaran","Adiodus","Adiomos","Adiosean","Adoadan","Adoeand","Adoiand","Adoildan","Adoinidd","Adra","Adrael","Adrayldric","Adreriloth","Adrie","Adrigoa","Adriotram","Adrira","Adrirasean","Adro","Adruseth","Adrutha","Adwardowyth","Adwaretha","Adwat","Adweagord","Adwilanydd","Adwiranydd","Adwirewyr","Adwom","Aeawyn","Aelap","Aeras","Aeril","Afalican","Afalit","Afeannor","Afeaw","Afec","Afeladan","Afelath","Afeligord","Afilip","Afirach","Afirawyn","Afoi","Afua","Agra","Agrarecon","Agraynwan","Agreisean","Agrendatlan","Agreras","Agrerider","Agrietha","Agrio","Agroader","Agroaran","Agrunwan","Ai","Aigog","Airelath","Alaoran","Alardobwyn","Alardodfrid","Alardonyth","Aleaf","Alei","Aleri","Aleri","Alerican","Alerrag","Aliat","Alich","Alilann","Alorectred","Alumas","Aoimma","Aoth","Aralelath","Arardonnor","Areacred","Arelatlan","Arelilin","Arelimond","Areradus","Aries","Arigowan","Arirand","Aroelin","Asaed","Asaenidd","Asalisean","Asayth","Aselaran","Asendawyth","Aserrawyn","Asiecan","Asieth","Asigodus","Asiramma","Asoaldan","Asoic","Asta","Astaecon","Astalemas","Astalemond","Astaoron","Astardoli","Astaycred","Asteig","Astelawyr","Astelidon","Asteliwyr","Astiap","Astiaran","Astirac","Astoemos","Astoi","Astunidd","Astuv","Asynydd","Ban","Beder","Bela","Berranad","Bia","Bigocred","Biodric","Bira","Bitram","Boresh","Braebwyn","Bralid","Brerigord","Breriwin","Brid","Brilith","Broe","Broelgrin","Brynwan","Brynwan","Cadacred","Cadaowyr","Cadarennon","Cadauder","Cadedfrid","Cadeiron","Cadeith","Caderra","Cadiedon","Cadield","Cadililath","Cadirann","Cadirannor","Cadyldric","Calemar","Calemos","Caliwin","Cardo","Carebard","Cash","Caush","Ce","Cea","Ceagord","Ceannor","Celadan","Celatlan","Ceraron","Ceratram","Ceritlan","Ceritram","Cerractred","Cerratram","Cerrav","Chauth","Cheab","Chigonydd","Chigor","Chilimar","Chorech","Chorend","Ciaron","Ciewyn","Ciewyth","Cigotha","Ciowyn","Ciradon","Cirali","Cirawyn","Coaran","Coatrem","Coenwan","Coetrem","Cralidric","Crare","Craynydd","Creidan","Crennon","Creram","Crerid","Crerild","Cresean","Criedan","Crieth","Crigan","Crigogord","Crilacan","Crirach","Criraloth","Crire","Criretrem","Croeldric","Cuwyn","Cybard","Da","Daeg","Daof","Daolath","Darewan","Dautha","Death","Desean","Dial","Digoli","Dirabaen","Drale","Drauvudd","Dreld","Drendald","Drerinn","Drerrawin","Dries","Driesean","Drif","Drilald","Drirawyn","Dwadan","Dwalemar","Dwali","Dwarelin","Dwaulgrin","Dwautram","Dwaytha","Dwaywyr","Dweaseth","Dweicon","Dwelidfrid","Dwerannon","Dwerrap","Dwia","Dwio","Dwiodon","Dwior","Dwoin","Dworegan","Dwywin","Edaectred","Edaletram","Edardoth","Edawin","Edeaw","Edeidan","Edelacan","Edelann","Edendacan","Edendanad","Edendaseth","Ederiwyr","Edeseth","Edetram","Ediabwyn","Edianwan","Edimas","Edirath","Edoish","Elaed","Elaewyth","Elaleth","Elayc","Eleard","Eleawyn","Eleladus","Elelash","Elendagan","Eleri","Eleriwyn","Elidus","Elilad","Eliolath","Eliracon","Eliretrem","Elutrem","Elyl","Eowaedon","Eowaelgrin","Eowaemos","Eowalemar","Eowaosean","Eoweadfrid","Eoweic","Eowerawyn","Eowerilith","Eowerimas","Eowerrald","Eowiav","Eowigonydd","Eowilap","Eowira","Eowiraand","Eralimma","Eraob","Erarewyth","Eraul","Eraynnor","Erelicred","Erendam","Ererravudd","Erigonad","Eriocan","Erorenn","Etaenidd","Etalemos","Etalinn","Etaoldan","Eteicred","Etera","Etera","Eterawyr","Ethalenn","Ethalish","Ethaoder","Ethaomos","Ethardolath","Ethauf","Etheibwyn","Ethelawyth","Etheridfrid","Ethigoth","Ethilac","Ethirawyr","Ethirend","Etiabaen","Etiadon","Etirawyr","Fardodus","Fardov","Farelath","Feanwan","Felali","Felich","Ferican","Ferinwan","Ferrawan","Fiadric","Figog","Fiop","Fior","Foac","Foal","Foid","Fraydon","Frea","Frei","Freitrem","Frelash","Freriron","Frerrawin","Fridfrid","Frilid","Frioder","Frirader","Froabwyn","Froiloth","Fructred","Gaebwyn","Gaeli","Galardolin","Galaucan","Galaugord","Galeisean","Galelath","Galeli","Galendaw","Galenidd","Galeranidd","Galeraron","Galeril","Galeriwin","Galigowan","Galila","Galiliwin","Galio","Galiradfrid","Galoedus","Galoennor","Galoredon","Gardowyr","Geath","Geinyth","Geron","Gerrad","Gerrand","Giamma","Gies","Giv","Glaunydd","Glaymar","Glendatha","Glia","Gligobwyn","Glilith","Glio","Gliol","Gliras","Glirewyn","Glynyth","Goas","Goend","Goidric","Goran","Graeld","Gralidus","Grarenad","Graulin","Grendas","Greril","Grerralath","Gri","Gribard","Grigot","Griladfrid","Griraron","Grorennon","Gruron","Guron","Gweildric","Gwendard","Gwendawyr","Gwican","Gwila","Gwoibard","Gwydader","Gwydaor","Gwydardotlan","Gwydardotram","Gwydarenyth","Gwydea","Gwydeal","Gwydeash","Gwydeidan","Gwydionyth","Gwydiovudd","Gwydiranwan","Gwydireder","Gwydireder","Gwydoedfrid","Gwydoi","Gwydoinn","Gwydorel","Gwydorerd","Gysean","Haaenyth","Haaydfrid","Haeith","Haera","Haew","Haieloth","Hailictred","Hairalin","Hairan","Halitram","Haliwyth","Hardo","Harelgrin","Harep","Haudan","Haycred","Heliand","Heliwyr","Hendabaen","Hendadon","Hendaran","Hiebard","Higoand","Hiloth","Hiradon","Hirewyr","Hitlan","Hoemas","Homma","Ibale","Ibarenwan","Ibaulith","Ibautrem","Ibean","Ibeav","Iberaran","Iberradan","Ibioth","Ibiowyr","Ibirand","Jeraeder","Jerewin","Jeriedric","Jerigoran","Jeriond","Jeriraseth","Jeroch","Jeroenad","Jeroewyth","Jerua","Kaaeand","Kaaenyth","Kaaot","Kaelip","Kaeris","Kaetrem","Kaialgrin","Kaieth","Kaigogord","Kailia","Kairaldan","Kairaw","Kaiw","Kannon","Kaseth","Kaumar","Kayrd","Kedaedus","Kedales","Kedaow","Kedaycan","Kedea","Kedeic","Kederach","Kedilannor","Kedioseth","Kedira","Kedith","Kedoalgrin","Kedumond","Kedy","Kedywyr","Kewyr","Kiam","Kiegan","Kiocon","Kiond","Kogan","Koildric","Kuli","Kywyr","Larareth","Laream","Lareannon","Larelanwan","Larerader","Laria","Larialdric","Larief","Lariladfrid","Larionnon","Lariraldan","Larirali","Larywin","Leacan","Legaebard","Legaef","Legaotha","Legardob","Legauf","Legeamma","Legilatrem","Legiliwyn","Legimond","Legomond","Legore","Legyrd","Leradus","Leritrem","Lilim","Lira","Lira","Liregan","Loaldric","Loran","Loregan","Lorelin","Lothaev","Lothardowan","Lotheadric","Lotheap","Lotheatram","Lothec","Lotheibaen","Lotheir","Lotheiwyn","Lothelictred","Lothiamar","Lothictred","Lothiotlan","Lothoach","Lothomma","Lothug","Lothuth","Maend","Maep","Mardonn","Marewyr","Meinn","Melidus","Mendaseth","Miaran","Milam","Miraecon","Mirale","Miralenidd","Mireamas","Mirean","Mirebaen","Mirerraron","Mirialdric","Mirich","Mirir","Miriramond","Miroir","Miroitrem","Mirywin","Moilgrin","Mubard","Myd","Naretram","Naudfrid","Naywyth","Neab","Neg","Neich","Noa","Noidan","Norebard","Norev","Nowan","Nydalewyth","Nydaucred","Nydayseth","Nydeannor","Nyderaa","Nyderaldan","Nyderiwyth","Nydigobard","Nydiresean","Nydocan","Ocach","Ocae","Ocaegord","Ocaliran","Ocaodric","Ocardobard","Ocareb","Ocarebard","Ocayld","Ocaysean","Oceader","Ocerav","Ocerinn","Ocerith","Ocietlan","Ocigodan","Ociragord","Ocirap","Ocirav","Ocoacan","Olareldan","Olauder","Olauth","Olelif","Olendadan","Olerra","Oli","Oliliwyn","Olirannor","Oloemas","Oloresean","Olynwan","Olytha","Olyw","Onale","Onaliw","Onaunnon","Onautlan","Onawyr","Onea","Oneas","Onemos","Onerraldan","Onilil","Onilis","Oniraron","Oniredon","Onireld","Onoresean","Onyl","Onyldric","Onynwan","Paeron","Pali","Pay","Paywyr","Peramma","Pigan","Pila","Pilidfrid","Pirad","Poatha","Ponyth","Praemar","Praewin","Praldan","Pran","Praoseth","Praywyr","Prendas","Priap","Prigodon","Prilar","Priodric","Prion","Priwyn","Proaloth","Pruran","Ra","Raaold","Raatlan","Raemar","Raemma","Raendaron","Raeriand","Railif","Raiomar","Raiosh","Raodus","Raoidan","Raoimma","Rardoder","Raul","Rawyn","Reap","Reli","Rendagan","Reram","Rheigan","Rhialath","Rhiard","Rhieldan","Rhilaldric","Rhilili","Rhiram","Rhoictred","Riand","Rien","Riranyth","Rirewyn","Ry","Sae","Saetha","Saredan","Seab","Seand","Selath","Sendawyth","Serab","Serral","Sevalip","Sevaumos","Seveagan","Sevelacan","Seveldric","Severigan","Severranwan","Seviebaen","Seviocan","Sevirel","Siep","Sier","Sind","Siracan","Sit","Skalilin","Skardonyth","Skaymar","Skeabaen","Skei","Sketha","Skila","Skod","Skoetram","Soif","Soitha","Sored","Teadon","Teamond","Telimos","Ten","Thalegan","Thalenydd","Thardoseth","Thauctred","Thauth","Theiand","Theinad","Theliwyr","Thendadric","Thendaw","Therach","Therrawyr","Thiaf","Thiard","Thiatram","Thiawyn","Thigonwan","Thiliwyr","Thimond","Thira","Thirawyn","Thobwyn","Thoebaen","Thoiwyn","Thuwin","Toer","Tolin","Traemos","Tralinwan","Tralitrem","Trareran","Trayth","Treav","Trera","Trericred","Trerracon","Trerracred","Triawyr","Trigoloth","Triractred","Troemar","Trorewyr","Trunn","Vaectred","Valiand","Veag","Veitha","Velamma","Velib","Vianwan","Viec","Vigodan","Vigot","Vilar","Viraseth","Viratlan","Vith","Vodan","Voeder","Vywyth","Wadfrid","Waedric","Waedus","Waleb","Walet","Waletram","Walil","Waot","Waum","Waylath","Waytlan","Wea","Weawyn","Weidfrid","Welap","Wer","Werard","Werrawin","Wial","Wicael","Wicaoand","Wicardor","Wicayldan","Wiceinn","Wicelawyth","Wicigotha","Wicilalin","Wicild","Wicilictred","Wicoawin","Wigold","Wiramond","Wiretrem","Witha","Witram","Wo","Woagord","Woigan","Woitram","Woregan","Yab","Yae","Yalenad","Yardomma","Yardowyth","Ybalecon","Ybaocred","Ybaseth","Ybaygan","Ybeatha","Ybeder","Ybeiwyr","Ybie","Ybiedus","Ybiowan","Ybiradric","Ybiralgrin","Ybireb","Ybuf","Yeliseth","Yerimos","Yilalath","Yilap","Yilitram","Yiobaen","Yirevudd","Yoa","Yoath","Yoish","Yorev","Yuw","Yymma","Yynnor","Yytrem","Zaewyn","Zalin","Zayl","Zayn","Zelawin","Zerin","Zerinnor","Zerir","Zerraw","Ziedan","Zilald","Zilgrin","Zililath","Zirawyth","Zoinydd","Zoiw","Zoiwyr","Zycan","Cherra","Gwoinnor","Wicaoa","Zaurd"]

civilizationNameHash =  { 
							"CIVILIZATION_AMERICA" :
							{
								"PRE" : ("Abelard","Ackley","Acton","Addison","Afton","Aida","Aidan","Ailen","Aland","Alcott","Alden","Alder","Aldercy","Aldis","Aldrich","Alfred","Allard","Alvin","Amaris","Amberjill","Amherst","Amsden","Ansley","Ashley","Atherol","Atwater","Atwood","Audrey","Avena","Averill","Ballard","Bancroft","Barclay","Barden","Barnett","Baron","Barse","Barton","Baul","Bavol","Baxter","Beacher","Beaman","Beardsley","Beccalynn","Bede","Beldon","Benson","Bentley","Benton","Bersh","Bethshaya","Beval","Beverly","Birch","Bishop","Blade","Blaine","Blake","Blossom","Blythe","Bob","Bolton","Bond","Booker","Booth","Borden","Bowman","Braden","Bradford","Bradley","Bramwell","Brandon","Bray","Brayden","Brenda","Brennan","Brent","Brett","Brewster","Brigham","Brinley","Brishen","Brock","Broderick","Bromley","Bronson","Brook","Brown","Buck","Buckley","Bud","Bunny","Burdette","Burgess","Burle","Burne","Burt","Burton","Calder","Caldwell","Calhoun","Calvert","Cam","Cameron","Carleton","Carling","Carlisle","Carlton","Carlyle","Carrington","Carter","Carver","Chad","Chal","Channing","Chapman","Charles","Chatwin","Chelsea","Chilton","Claiborne","Clark","Clayton","Clay","Cleveland","Clifford","Clinton","Clive","Clovis","Cody","Colby","Cole","Coleman","Collier","Colton","Columbia","Corin","Corliss","Coty","Courtland","Courtney","Creighton","Crosby","Culver","Currier","Cynric","Dale","Dallin","Dalton","Damon","Dane","Danior","Daralis","Darnell","Darrel","Darren","Darthmouth","Darwin","Dawn","Dayton","Demelza","Dempster","Denley","Denton","Denver","Derwin","Devon","Dickinson","Digby","Dixie","Donald","Dooriya","Dorset","Dory","Dover","Drake","Duane","Dudley","Dugan","Dunstan","Durriken","Durward","Dustin","Dwennon","Dwight","Eartha","Easter","Eaton","Ebony","Edda","Edgardo","Edison","Edlyn","Edmond","Edolie","Edsel","Edward","Edward","Eddie","Egerton","Elden","Eldon","Eldridge","Ella","Elmar","Elton","Ember","Emerson","Emmett","Ena","Erika","Erskine","Esmeralda","Esmond","Ewing","Fairfax","Falkner","Farley","Farrah","Farrah","Fara","Farrell","Fear","Fenton","Fern","Fielding","Finlay","Fleming","Fleta","Fletcher","Floyd","Forbes","Ford","Forrester","Free","Fuller","Fulton","Gage","Gail","Gaines","Garfield","Garrick","Garridan","Gary","Garyson","Geoffrey","Gleda","Goldie","Gordon","Granger","Grayson","Gresham","Grover","Gypsy","Gytha","Hadden","Hale","Hall","Halsey","Halton","Hamilton","Hanley","Harden","Harley","Harman","Harmony","Harold","Harper","Harrison","Hartley","Harva","Harvey","Hayden","Hayes","Haylee","Hazel","Heath","Heather","Hilton","Holbrook","Holly","Holt","Honey","Hope","Houston","Howard","Hugh","Hunter","Huntley","Ida","India","Ives","Jagger","Jal","James","Jimmy","Jamie","Jamison","Jarman","Jarvis","Jillian","Jocelyn","Joyce","Jonesy","Joy","Kaelyn","Keane","Keene","Kell","Kelsey","Kemp","Kenelm","Kenley","Kennard","Kenneth","Kenrich","Kent","Kenton","Ker","Keyon","Kim","Kimberley","King","Kingsley","Kinsey","Kipling","Kipp","Kirsten","Kismet","Knox","Kody","Kyla","Ladd","Lainey","Lander","Landon","Lane","Lang","Langley","Lari","Lark","Latimer","Lawson","Lee","Leigh","Leighton","Leland","Lensar","Leslie","Lew","Liberty","Lincoln","Lind","Lindsay","Linwood","Litton","Llewellyn","Locke","London","Love","Lowell","Luella","Lyman","Lyndon","Lyre","Mac","Macon","Macy","Maida","Maitane","Maitland","Makepeace","Mala","Mander","Manhattan","Manley","Manning","Marden","Marland","Marlow","Marsden","Marshal","Mather","Mavis","Maxwell","Mead","Melor","Melville","Mendel","Mercer","Mercy","Merrick","Merry","Milburn","Millard","Miller","Milton","Missy","Misty","Morley","Morven","Mull","Nara","Nash","Neda","Nelson","Nevin","Newell","Newman","Norman","North","Nyle","Oakes","Oakley","Ogden","Olin","Orman","Orson","Osbert","Osborn","Osmond","Oswald","Oswin","Oxford","Packard","Palma","Palmer","Paris","Parker","Parr","Parry","Paxton","Payton","Pearl","Pebbles","Pell","Penley","Penn","Pepper","Perri","Perry","Pierce","Pierson","Piper","Poppy","Prentice","Prescott","Preston","Putnam","Queen","Queena","Queenie","Quella","Quenna","Radcliff","Radcliffe","Radella","Radford","Rae","Raleigh","Ralph","Ramsey","Ransford","Ransley","Ransom","Raven","Ravinger","Rawlins","Rayburn","Raymond","Read","Redford","Reed","Reeve","Reeves","Reginald","Remington","Rhett","Rhodes","Richard","Richelle","Rider","Ridgley","Ridley","Rigby","Ripley","Rishley","Robert","Roberta","Rochester","Rodman","Rodney","Roldan","Rowan","Rowena","Royce","Rudd","Rudyard","Ruford","Rumer","Russel","Rutherford","Ryesen","Rylan","Sabrina","Brina","Salal","Sanborn","Sanders","Sandon","Sanford","Sawyer","Scarlet","Scarlett","Scott","Seabert","Seaton","Selby","Severin","Seward","Seymour","Shandy","Sharman","Shaw","Shelby","Sheldon","Shelley","Shepherd","Sherlock","Sherman","Sherwood","Shipley","Shirley","Siddel","Skeet","Skye","Skyla","Skylar","Slade","Smith","Snowden","Spalding","Sparrow","Spencer","Spike","Spring","Standish","Stanford","Stanislaw","Stanley","Stanley","Stan","Stanway","Sterling","Sterne","Stockard","Stoke","Stokley","Storm","Stroud","Studs","Summer","Sunny","Sutton","Swain","Tab","Tanner","Tate","Tatum","Tawnie","Taylor","Telford","Tem","Tennyson","Terrel","Thane","Thatcher","Thistle","Thorne","Thorpe","Thurlow","Tilden","Tina","Todd","Tomkin","Townsend","Tranter","Tremayne","Trey","Tripp","Trudy","Truman","Tucker","Tuesday","Turner","Twain","Tye","Tyler","Tyne","Udolf","Ulla","Ulrich","Ulrika","Unity","Unwin","Upshaw","Upton","Vala","Vance","Velvet","Verity","Vian","Wade","Wakefield","Walker","Wallace","Walton","Ward","Warren","Washington","Watson","Waverly","Wayland","Waylen","Wayland","Wayne","Webster","Welcome","Wells","Wendy","Wesley","West","Weston","Wetherby","Wheaton","Wheeler","Whit","Whitfield","Whitlaw","Whitney","Wilfred","Willow","Wilmer","Wilona","Winifred","Winslow","Winston","Winter","Winthrop","Wolf","Woodley","Woodrow","Woodward","Wright","Wyatt","Wylie","Wyndam","Wyndham","Yardley","Yates","Yedda","Yeoman","York","Yule","Zane","Zelene","Zinnia","Allen","Austin","Avery","Bryant","Elmer","Emmett","Everett","Garrett","Gary","Jackson","Larkin","Lark","Lamont","Lawrence","Madison","Merle","Merrill","Mitchell","Morris","Nelson","Otis","Pierce","Stacy","Stacey","Willard","Willis","Wilson","Wyatt","Ainsley","Alton","Ashley","Bailey","Barrington","Bentley","Beverly","Bradford","Bradley","Brady","Brent","Brock","Brooke","Byron","Camden","Carlton","Chester","Clay","Clayton","Clifford","Clifton","Clinton","Clive","Colton","Dale","Dalton","Dana","Darby","Denzil","Digby","Drake","Dudley","Easton","Forrest","Glanville","Grover","Hailey","Haley","Hartley","Heath","Holden","Kelsey","Kendall","Kent","Kenton","Kimberly","Landon","Lee","Lester","Milton","Nash","Norris","Odell","Perry","Peyton","Preston","Rodney","Royston","Shelby","Sheldon","Shirley","Stanley","Stanton","Vance","Van","Wade","Wesley","Whitney","Winston","Woodrow","Roscoe","Barrie","Barry","Colby","Courtney","Courtenay","Darcy","Darrell","Darryl","Lacey","Lance","Lane","Leland","Montague","Mortimer","Morton","Neville","Percy","Sacheverell","Troy","Vernon","Warren","Blake","Brady","Brett","Cade","Chance","Cole","Curtis","Dana","Drew","Franklin","Scott","Tate","Todd","Truman","Wendell","Wynne","Bailey","Baron","Booker","Brewster","Carter","Chandler","Chauncey","Chase","Clark","Cooper","Cody","Cordell","Dexter","Earl","Garnet","Hunter","Jagger","Marshall","Mason","Millard","Page","Paige","Parker","Sherman","Tanner","Taylor","Tucker","Tyler","Travis","Spencer","Walker","Wayne","Bruce","Graham","Lyle","Grant","Ross","Wallace","Stuart","Dallas","Gordon","Kirk","Lindsay","Lindsey","Maxwell","Ramsay","Rutherford","Blair","Douglas","Keith","Kyle","Ross","Sterling","Boyd","Cameron","Cambell","Doyle","Mackenzie","Mckinley","Irving","Logan","Barry","Cody","Darcy","Desmond","Grady","Kelley","Kelly","Kennedy","Sullivan","Barrington","Barry","Brady","Carroll","Casey","Cassidy","Cody","Donovan","Fallon","Hogan","Keegan","Quinn","Sheridan","Corey","Cory","Delaney","Perry","Craig","Kendall","Trevor","Meredith","Vaughan","Wynne"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_ARABIA" :
							{
								"PRE" : ("Abdul","","Al","","Abdel","","'Abd al","Aban","Abbas","Abbud","Abbudin","'Adl","Ahad","Alim","Aliyy","Azim","Aziz","Badi","Ba'ith","Baqi","Bari","Barr","Basir","Basit","Fattah","Ghaffar","Ghafur","Ghani","Hadi","Hafiz","Hakam","Hakim","Halim","Hamid","Haqq","Hasib","Hayy","Jabbar","Jalil","Karim","Khabir","Khaliq","Latif","Malik","Majid","Matin","Mubdi'","Mughni","Muhaimin","Muhsi","Muhyi","Mu'id","Mu'izz","Mujib","Mu'min","Muqaddim","Muqtadir","Musawwir","Muta'al","Nafi'","Nasser","Nasir","Nur","Qadir","Qahhar","Qawi","Qayyum","Quddus","Rafi'","Rahim","Rahman","Rashid","Ra'uf","Razzaq","Sabur","Salam","Samad","Sami","Sattar","Shahid","Shakur","Tawwab","Wadud","Wahhab","Wahid","Wajid","Wakil","Wali","Waliy","Warith","Zahir","Abdullah","'Abid","'Abidin","Abu Bakr","Abu al Khayr","Adan","Adel","'Adil","Adham","Adib","'Adli","Adnan","'Adnan","'Afif","Afeef","Ahmad","Ahmed","'Ajib","'Akif","Akil","Akram","Ala'","Ala' al Din","Al 'Abbas","Aladdin","Ala' al din","Al Bara'","Al Hakam","Al Harith","Alhasan","Alhusain","Alhusayn","Ali","'Ali","'Aliyy","Alim","Almahdi","Al Safi","Altaf","Altair","Al Tayyib","Al Tijani","Al Tufail","Al Tufayl","Amid","'Amid","Amin","Ameen","Amir","Ameer","'Amir","Amjad","Ammar","'Ammar","'Amro","Anas","Anis","'Antarah","Anwar","'Aqil","Arfan","Arif","'Arif","Asad","As'ad","Asadel","Ashraf","Asif","Asim","'Asim","Aswad","Ata'","'Ataa","Ata' Allah","Ata' al Rahman","Athil","Athir","Atif","'Atif","Awad","'Awad","'Awf","Aws","Awwab","Ayham","Ayman","Ayser","Ayyub","Ayoob","Aza","'Azab","Azhar","Azeem","Azim","Aziz","'Aziz","Azzam","'Azzam","Badi","Badi al Zaman","Badr","Badr al Din","Badri","Baha","Baha'","Baha al Din","Bahiyy al Din","Bahij","Bahir","Bakr","Bakri","Baligh","Bandar","Barakah","Barir","Bashir","Bashshar","Basil","Basim","Bassam","Bayhas","Bilal","Bishr","Boulos","Budail","Budayl","Burhan","Bushr","Butrus","Dabir","Dani","Darwish","Da'ud","Dawud","Dhakir","Dhakiy","Dhakwan","Dhul Fiqar","Dirar","Diya","Diya al Din","Duqaq","Fadi","Fadil","Fadl","Fadl Allah","Fahd","Fahad","Fahmi","Faisal","Faysal","Fa'iz","Fakhir","Fakhr al Din","Fakhri","Fakhry","Fakih","Falah","Falih","Faraj","Farraj","Farhan","Farid","Fareed","Fariq","Fareeq","Faris","Faruq","Farooq","Fath","Fathi","Fatih","Fatin","Fateen","Fawwaz","Fawzan","Fawzi","Fayyad","Ferran","Fida","Fikri","Firas","Fouad","Fu'ad","Fudail","Gamal","Gamali","Ghaith","Ghayth","Ghali","Ghalib","Ghanim","Ghassan","Ghawth","Ghazi","Ghazwan","Ghiyath","Habbab","Habib","Hadad","Haddad","Hadi","Hafiz","Hakem","Hakim","Hakeem","Halim","Hamal","Hamas","Hamdan","Hamdi","Hamid","Hamim","Hamzah","Hana","Hana'i","Hanbal","Hani","Hanif","Hannad","Haris","Harith","Haroun","Harun","Hashim","Hassan","Hatim","Haydar","Haytham","Hayyan","Hazim","Hilal","Hilel","Hilmi","Hisham","Hud","Houd","Hudad","Hudhafah","Hudhaifah","Hudhayfah","Humam","Husain","Husayn","Hussein","Husam","Husam al Din","Ibrahim","'Id","Idris","Ihsan","Ihtisham","'Ikrimah","Ilias","Imad","'Imad","Imad al Din","Imam","Imran","'Imran","Imtiyaz","In'am","Iqbal","Irfan","'Irfan","Isa","'Isa","Eisa","Isam","'Isam","Issam","Ishaq","Isma'il","Iyad","Iyas","Izz al Din","Jabalah","Jabbar","Jabr","Jabir","Jad Allah","Jafar","Ja'far","Jal","Jalal","Jalal al Din","Jalil","Jaleel","Jamal","Jamal al Din","Jamil","Jameel","Jarir","Jasim","Jaul","Jaun","Jawad","Jawdah","Jawhar","Jibran","Jibril","Jihad","Jubair","Jubayr","Jul","Jumah","Jumu'ah","Junaid","Junayd","Juwain","Juwayn","Kadar","Kedar","Kadeen","Kadin","Kadeer","Kadir","Kahil","Kaliq","Kamal","Kamil","Kameel","Karam","Kardal","Karif","Kareef","Karim","Kareem","Kasib","Kaseeb","Kaseem","Kasim","Kateb","Katib","Kazim","Khalaf","Khaldun","Khaldoon","Khalid","Khaled","Khalifah","Khalil","Khaleel","Kalil","Khalil al Allah","Khalis","Khatib","Khair al Din","Khairi","Khairy","Khayri","Khoury","Khulus","Khuzaimah","Khuzaymah","Kutaiba","Labib","Labeeb","Lablab","Latif","Layth","Lu'ay","Lubaid","Lubayd","Luqman","Lut","Lutfi","Ma'd","Madani","Mahbub","Mahdi","Mahfuz","Mahir","Mahjub","Mahmud","Mahmoud","Mahrus","Maimun","Maymun","Majd","Majdy","Majd al Din","Majid","Makin","Malik","Mamdouh","Mamduh","Ma'mun","Ma'n","Ma'in","Mandhur","Mansur","Marghub","Marid","Ma'ruf","Marwan","Marzuq","Mash'al","Mashhur","Masrur","Mas'ud","Masun","Maysarah","Mazhar","Mazin","Mihran","Mihyar","Mika'il","Miqdad","Misbah","Mishaal","Mish'al","Miyaz","Mu'adh","Mu'awiyah","Mu'ayyad","Mubarak","Mubin","Mudar","Muddaththir","Mufid","Mufeed","Muflih","Muhab","Muhair","Muhayr","Muhammad","Mohammed","Muhanna","Muhannad","Muhanned","Muhib","Muhibb","Muhsin","Muhtadi","Muhyi al Din","Mu'in","Mu'izz","Mujab","Mujahid","Mukarram","Mukhlis","Mukhtar","Mulham","Mulhim","Mu'mmar","Mu'min","Mumtaz","Munahid","Mundhir","Munib","Munif","Munir","Muneer","Mu'nis","Munjid","Munsif","Muntasir","Murad","Murshid","Murtada","Murtadi","Murtadhy","Musa","Moosa","Mus'ab","Mus'ad","Musa'id","Mushtaq","Muslih","Muslim","Mustafa","Muta'","Mu'tasim","Mutawalli","Mu'tazz","Muthanna","Muti","Muwaffaq","Muyassar","Muzaffar","Muzzammil","Nabhan","Nabih","Nabighah","Nabih","Nabil","Nabeel","Nadhir","Nadim","Nadeem","Nadir","Nafi'","Nahid","Na'il","Na'im","Naji","Najib","Najeeb","Najid","Najjar","Najm al Din","Na'man","Namir","Nash'ah","Nash'at","Nashwan","Nasib","Nasih","Nasim","Nasir","Nasir al Din","Nasr","Nasser","Nasri","Nasuh","Nawaf","Nawwaf","Nawfal","Nayif","Naif","Nazih","Nazeeh","Nazim","Nazeem","Nazmi","Nibras","Nidal","Nijad","Nimr","Nizar","Nu'aim","Nu'aym","Nuh","Nooh","Nuhaid","Nuhayd","Numair","Nu'man","Nur al Din","Nuri","Noori","Nusrah","Nusrat","Qasim","Qays","Qais","Qudamah","Qusay","Qatadah","Qutaybah","Qutaibah","Qutb","Qutuz","Rabah","Rabi","Radi","Rafi","Rafid","Rafiq","Raghib","Ragheb","Raghid","Rahman","Ra'id","Ra'if","Rais","Raja","Rajab","Raji","Rajih","Rakin","Ramadan","Rami","Ramih","Ramiz","Ramzi","Rani","Rashad","Rashid","Rasil","Rasin","Rasmi","Rasul","Ratib","Ra'uf","Rayhan","Rayyan","Razin","Reda","Rida","Ridha","Ridwan","Rihab","Riyad","Riyadh","Rizq","Ruhi","Rushd","Rushdi","Ruwaid","Ruwayd","Saad","Sa'adah","Sab","Sabih","Sabeeh","Sabir","Sabeer","Sabri","Sa'd","Sa'd al Din","Sadad","Sadid","Sadiq","Sa'dun","Sa'eed","Sa'id","Safi","Safiy","Safiy al Din","Safuh","Safwah","Safwat","Safwan","Sahib","Sahir","Sahl","Sa'ib","Saif","Sayf","Seif","Saif al Din","Sajid","Sajjad","Sakhr","Salah","Salah al Din","Salamah","Saleh","Salih","Salim","Saleem","Salman","Sami","Samih","Samir","Sameer","Samman","Saqr","Sariyah","Sati","Saud","Sayyid","Sha'ban","Shadi","Shadin","Shafi","Shafiq","Shafeeq","Shahid","Shahin","Shahir","Shakib","Shakir","Shams al Din","Shamal","Shamil","Shamim","Sharaf","Sharif","Shareef","Shawqi","Shihab","Shihab al Din","Shihad","Shu'aib","Shu'ayb","Shukri","Shumayl","Siddiq","Sinan","Siraj","Siraj al Din","Sofian","Subhi","Sufyan","Suhaib","Suhayb","Suhail","Suhayl","Suhaim","Suhaym","Sulaiman","Sulayman","Sultan","Sumrah","Suraqah","Su'ud","Suoud","Tahir","Tahsin","Taim Allah","Taym Allah","Taj","Taj al Din","Talal","Talib","Tamim","Tamir","Tamam","Tammam","Taqiy","Tarif","Tareef","Tariq","Taslim","Tawfiq","Tawhid","Taymullah","Taysir","Tayyib","Thabit","Thamer","Thamir","Thaqib","Thawab","Thawban","'Ubaidah","'Ubaydah","Ubaid","Ubayy","'Udail","'Udayl","'Uday","'Umar","Omar","Umarah","Umayr","Umair","Umayyah","'Urwah","Usaim","Usaym","Usama","Usamah","'Utbah","Uthal","Uthman","Waddah","Wadi","Wadid","Wafiq","Wafeeq","Wahab","Wahhab","Wahid","Wa'il","Wajdi","Wajid","Wajih","Wakil","Walid","Waleed","Walif","Waliy Allah","Waliy al Din","Waqar","Waqqas","Ward","Wasif","Wasil","Wasim","Waseem","Wazir","Yahya","Yaman","Ya'qub","Yasar","Yasser","Yasin","Yaseen","Yasir","Yazan","Yazid","Yazeed","Youssef","Yusef","Yusuf","Yunus","Yoonus","Yushua","Yusri","Yusuf","Zafar","Zafir","Zahid","Zahir","Zaid","Zayd","Zaim","Zain","Zayn","Zarif","Zakariyya","Zaki","Zaky","Zakwan","Ziad","Ziyad","Zubair","Zubayr","Zuhair","Zuhayr"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_AZTEC" :
							{
								"PRE" : ("Ah","Akh","Bac","Cent","Chalch","Ch","Ci","Ehe","Ek","Huitz","Itz","Ix","Kan","Kis","Kuk","Mac","May","Metz","Mic","N","Om","Pat","Pay","Quetz","Teoy","Tl","Tlatz","Ton","Xil","Xoch","Yac","Yax","Yuc","Yum"),
								"MID" : ("in","pu","papa","uayey","au","ma","ilopo","u","one","a","ipi","e","ao","alo","uilxo","eo","icome","aha","hua","iuhtli","atiu","anti","acatechu","etecu"),
								"END" : ("chil","tl","can","tlilton","tab","coatl","lcoati","lotl","chtli","kaax","mqui","lli","chitl","huel","htli","ch","c","co","chamah","tli","catl","tan","kiq","tlan","con","tecuhtil","nal","shtal","u","bs","h","tl","cue")
							},
							"CIVILIZATION_CARTHAGE" :
							{
								"PRE" : ("Ap","B","C","Cer","Cerb","D","Fl","J","Jup","M","Merc","Min","Nept","Pl","Pros","S","V","Ur"),
								"MID" : ("a","acchu","ai","arpi","e","ercu","i","ia","o","u"),
								"END" : ("a","lcan","llo","na","ne","no","nus","pid","ra","res","rs","rva","rus","ry","s","sta","ter","to","turn")
							},
							"CIVILIZATION_CELT" :
							{
								"PRE" : ("A","Ab","c","Ad","Af","Agr","st","As","Al","Adw","Adr","Ar","r","h","ad","D","r","w","d","th","Et","Er","El","ow","F","r","r","w","wyd","l","l","a","b","er","ed","th","r","eg","r","d","l","c","n","r","h","ev","k","a","r","h","h","b","ic"),
								"MID" : ("a","e","u","o","re","ale","li","ay","rdo","e","i","i","ra","la","li","nda","erra","i","e","ra","la","li","o","ra","go","i","e","re","y"),
								"END" : ("a","and","b","bwyn","baen","bard","c","ctred","cred","ch","can","con","d","dan","don","der","dric","dfrid","dus","f","g","gord","gan","l","ld","li","lgrin","lin","lith","lath","loth","ld","ldric","ldan","m","mas","mma","mos","mar","mond","n","nydd","nidd","nnon","nwan","nyth","nad","nn","nnor","nd","p","r","ran","ron","rd","s","sh","seth","sean","t","th","th","tha","tlan","trem","tram","v","vudd","w","wan","win","win","wyn","wyn","wyr","wyr","wyth")
							},
							"CIVILIZATION_CHINA" :
							{
								"PRE" : ("a","ai","an","ang","ao","cha","ch`a","chai","ch`ai","chan","ch`an","chang","ch`ang","chao","ch`ao","che","ch`e","chen","ch`en","cheng","ch`eng","chi","ch`i","chia","ch`ia","chiang","ch`iang","chiao","ch`iao","chieh","ch`ieh","chien","ch`ien","chih","ch`ih","chin","ch`in","ching","ch`ing","chiu","ch`iu","chiung","ch`iung","cho","ch`o","chou","ch`ou","chu","ch`u","chu","ch`u","chua","chuai","ch`uai","chuan","ch`uan","chuan","ch`uan","chuang","ch`uang","chueh","ch`ueh","chui","ch`ui","chun","ch`un","chun","ch`un","chung","ch`ung","en","erh","fa","fan","fang","fei","fen","feng","fo","fou","fu","ha","hai","han","hang","hao","hei","hen","heng","ho","hou","hsi","hsia","hsiang","hsiao","hsieh","hsien","hsin","hsing","hsiu","hsiung","hsu","hsuan","hsueh","hsun","hu","hua","huai","huan","huang","hui","hun","hung","huo","i","jan","jang","jao","je","jen","jeng","jih","jo","jou","ju","juan","jui","jun","jung","ka","k`a","kai","zha","cha","zhai","chai","zhan","chan","zhang","chang","zhao","chao","zhe","che","zhen","chen","zheng","cheng","ji","qi","jia","qia","jiang","qiang","jiao","qiao","jie","qie","jian","qian","zhi","chi","jin","qin","jing","qing","jiu","qiu","jiong","qiong","zhuo","chuo","zhou","chou","zhu","chu","ju","qu","zhua","zhuai","chuai","zhuan","chuan","juan","quan","zhuang","chuang","jue","que","zhui","chui","zhun","chun","jun","qun","zhong","chong","er","he","xi","xia","xiang","xiao","xie","xian","xin","xing","xiu","xiong","xu","xuan","xue","xun","hong","yi","ran","rang","rao","re","ren","reng","ri","ruo","rou","ru","ruan","rui","run","rong","ga","ka","gai","k`ai","kan","k`an","kang","k`ang","kao","k`ao","ken","k`en","keng","k`eng","ko","k`o","kou","k`ou","ku","k`u","kua","k`ua","kuai","k`uai","kuan","k`uan","kuang","k`uang","kuei","k`uei","kun","k`un","kung","k`ung","kuo","k`uo","la","lai","lan","lang","lao","le","lei","leng","li","liang","liao","lieh","lien","lin","ling","liu","lo","lou","lu","lu","luan","luan","lueh","lun","lung","ma","mai","man","mang","mao","mei","men","meng","mi","miao","mieh","mien","min","ming","miu","mo","mou","mu","na","nai","nan","nang","nao","nei","nen","neng","ni","niang","niao","nieh","nien","nin","ning","niu","no","nou","nu","nu","nuan","nueh","nung","o","ou","pa","p`a","pai","p`ai","pan","p`an","pang","p`ang","pao","p`ao","pei","p`ei","pen","p`en","peng","p`eng","pi","p`i","piao","p`iao","pieh","p`ieh","pien","p`ien","pin","p`in","ping","p`ing","po","p`o","p`ou","kai","gan","kan","gang","kang","gao","kao","gen","ken","geng","keng","ge","ke","gou","kou","gu","ku","gua","kua","guai","kuai","guan","kuan","guang","kuang","gui","kui","gun","kun","gong","kong","guo","kuo","kai","gan","kan","gang","kang","gao","kao","gen","ken","geng","keng","ge","ke","gou","kou","gu","ku","gua","kua","guai","kuai","guan","kuan","guang","kuang","gui","kui","gun","kun","gong","kong","guo","kuo","lie","lian","luo","luan","lue","long","mie","mian","nie","nian","nuo","nue","nong","e","ba","pa","bai","pai","ban","pan","bang","pang","bao","pao","bei","pei","ben","pen","beng","peng","bi","pi","biao","piao","bie","pie","bian","pian","bin","pin","bing","ping","bo","po","pou","pu","p`u","sa","sai","san","sang","sao","se","sen","seng","sha","shai","shan","shang","shao","she","shen","sheng","shih","shou","shu","shua","shuai","shuan","shuang","shui","shun","shuo","so","sou","ssu","su","suan","sui","sun","sung","ta","t`a","tai","t`ai","tan","t`an","tang","t`ang","tao","t`ao","te","t`e","teng","t`eng","ti","t`i","tiao","t`iao","tieh","t`ieh","tien","t`ien","ting","t`ing","tiu","to","t`o","tou","t`ou","tu","t`u","tuan","t`uan","tui","t`ui","tun","t`un","tung","t`ung","tsa","ts`a","tsai","ts`ai","tsan","ts`an","tsang","ts`ang","tsao","ts`ao","tse","ts`e","tsei","tsen","ts`en","tseng","ts`eng","tso","ts`o","tsou","ts`ou","tsu","ts`u","tsuan","ts`uan","tsui","ts`ui","tsun","ts`un","tsung","ts`ung","tzu","tz`u","wa","wai","wan","wang","wei","wen","weng","wo","wu","ya","yai","yang","yao","yeh","yen","yin","ying","yo","yu","yu","yuan","yueh","yun","yung","bu","pu","shi","suo","si","song","da","ta","dai","tai","dan","tan","dang","tang","dao","tao","de","te","deng","teng","di","ti","diao","tiao","die","tie","dian","tian","ding","ting","diu","duo","tuo","dou","tou","du","tu","duan","tuan","dui","tui","dun","tun","dong","tong","za","ca","zai","cai","zan","can","zang","cang","zao","cao","ze","ce","zei","zen","cen","zeng","ceng","zuo","cuo","zou","cou","zu","cu","zuan","cuan","zui","cui","zun","cun","zong","cong","zi","ci","ye","yan","you","yu","yuan","yue","yun","yong"),
								"MID" : (),
								"END" : (),
							},
							"CIVILIZATION_EGYPT" :
							{
								"PRE" : ("Ab","Abt","Ak","Ak","Am","An","Ankh","Ap","Aq","At","Atankh","Bast","Bak","Benn","Cart","Deshr","Dj","D","Fet","G","Hats","Hedj","Hor","Is","Kh","Khn","M","Men","Nekhb","Nem","Neph","Net","N","Osir","Per","Pysh","Pt","R","S","Sekhm","Sep","Ses","Set","Seth","Sh","Sob","Tar","Th","Udj","Ush","Wab","Wadj"),
								"MID" : ("u","arzim","uat","er","abti","het","arna","enta","ut","ulet","at","un","ek","um","ah","ubis","is","oth","ert","ef","en","et","ent","ha","thys","hu","eb","ebu","hepsut","epresh","aos","onsu","aat","ammisi","anu","hed","in"),
								"END" : ()
							},
							"CIVILIZATION_ENGLAND" :
							{
								"PRE" : ("Abelard","Ackley","Acton","Addison","Afton","Aida","Aidan","Ailen","Aland","Alcott","Alden","Alder","Aldercy","Aldis","Aldrich","Alfred","Allard","Alvin","Amaris","Amberjill","Amherst","Amsden","Ansley","Ashley","Atherol","Atwater","Atwood","Audrey","Avena","Averill","Ballard","Bancroft","Barclay","Barden","Barnett","Baron","Barse","Barton","Baul","Bavol","Baxter","Beacher","Beaman","Beardsley","Beccalynn","Bede","Beldon","Benson","Bentley","Benton","Bersh","Bethshaya","Beval","Beverly","Birch","Bishop","Blade","Blaine","Blake","Blossom","Blythe","Bob","Bolton","Bond","Booker","Booth","Borden","Bowman","Braden","Bradford","Bradley","Bramwell","Brandon","Bray","Brayden","Brenda","Brennan","Brent","Brett","Brewster","Brigham","Brinley","Brishen","Brock","Broderick","Bromley","Bronson","Brook","Brown","Buck","Buckley","Bud","Bunny","Burdette","Burgess","Burle","Burne","Burt","Burton","Calder","Caldwell","Calhoun","Calvert","Cam","Cameron","Carleton","Carling","Carlisle","Carlton","Carlyle","Carrington","Carter","Carver","Chad","Chal","Channing","Chapman","Charles","Chatwin","Chelsea","Chilton","Claiborne","Clark","Clayton","Clay","Cleveland","Clifford","Clinton","Clive","Clovis","Cody","Colby","Cole","Coleman","Collier","Colton","Columbia","Corin","Corliss","Coty","Courtland","Courtney","Creighton","Crosby","Culver","Currier","Cynric","Dale","Dallin","Dalton","Damon","Dane","Danior","Daralis","Darnell","Darrel","Darren","Darthmouth","Darwin","Dawn","Dayton","Demelza","Dempster","Denley","Denton","Denver","Derwin","Devon","Dickinson","Digby","Dixie","Donald","Dooriya","Dorset","Dory","Dover","Drake","Duane","Dudley","Dugan","Dunstan","Durriken","Durward","Dustin","Dwennon","Dwight","Eartha","Easter","Eaton","Ebony","Edda","Edgardo","Edison","Edlyn","Edmond","Edolie","Edsel","Edward","Edward","Eddie","Egerton","Elden","Eldon","Eldridge","Ella","Elmar","Elton","Ember","Emerson","Emmett","Ena","Erika","Erskine","Esmeralda","Esmond","Ewing","Fairfax","Falkner","Farley","Farrah","Farrah","Fara","Farrell","Fear","Fenton","Fern","Fielding","Finlay","Fleming","Fleta","Fletcher","Floyd","Forbes","Ford","Forrester","Free","Fuller","Fulton","Gage","Gail","Gaines","Garfield","Garrick","Garridan","Gary","Garyson","Geoffrey","Gleda","Goldie","Gordon","Granger","Grayson","Gresham","Grover","Gypsy","Gytha","Hadden","Hale","Hall","Halsey","Halton","Hamilton","Hanley","Harden","Harley","Harman","Harmony","Harold","Harper","Harrison","Hartley","Harva","Harvey","Hayden","Hayes","Haylee","Hazel","Heath","Heather","Hilton","Holbrook","Holly","Holt","Honey","Hope","Houston","Howard","Hugh","Hunter","Huntley","Ida","India","Ives","Jagger","Jal","James","Jimmy","Jamie","Jamison","Jarman","Jarvis","Jillian","Jocelyn","Joyce","Jonesy","Joy","Kaelyn","Keane","Keene","Kell","Kelsey","Kemp","Kenelm","Kenley","Kennard","Kenneth","Kenrich","Kent","Kenton","Ker","Keyon","Kim","Kimberley","King","Kingsley","Kinsey","Kipling","Kipp","Kirsten","Kismet","Knox","Kody","Kyla","Ladd","Lainey","Lander","Landon","Lane","Lang","Langley","Lari","Lark","Latimer","Lawson","Lee","Leigh","Leighton","Leland","Lensar","Leslie","Lew","Liberty","Lincoln","Lind","Lindsay","Linwood","Litton","Llewellyn","Locke","London","Love","Lowell","Luella","Lyman","Lyndon","Lyre","Mac","Macon","Macy","Maida","Maitane","Maitland","Makepeace","Mala","Mander","Manhattan","Manley","Manning","Marden","Marland","Marlow","Marsden","Marshal","Mather","Mavis","Maxwell","Mead","Melor","Melville","Mendel","Mercer","Mercy","Merrick","Merry","Milburn","Millard","Miller","Milton","Missy","Misty","Morley","Morven","Mull","Nara","Nash","Neda","Nelson","Nevin","Newell","Newman","Norman","North","Nyle","Oakes","Oakley","Ogden","Olin","Orman","Orson","Osbert","Osborn","Osmond","Oswald","Oswin","Oxford","Packard","Palma","Palmer","Paris","Parker","Parr","Parry","Paxton","Payton","Pearl","Pebbles","Pell","Penley","Penn","Pepper","Perri","Perry","Pierce","Pierson","Piper","Poppy","Prentice","Prescott","Preston","Putnam","Queen","Queena","Queenie","Quella","Quenna","Radcliff","Radcliffe","Radella","Radford","Rae","Raleigh","Ralph","Ramsey","Ransford","Ransley","Ransom","Raven","Ravinger","Rawlins","Rayburn","Raymond","Read","Redford","Reed","Reeve","Reeves","Reginald","Remington","Rhett","Rhodes","Richard","Richelle","Rider","Ridgley","Ridley","Rigby","Ripley","Rishley","Robert","Roberta","Rochester","Rodman","Rodney","Roldan","Rowan","Rowena","Royce","Rudd","Rudyard","Ruford","Rumer","Russel","Rutherford","Ryesen","Rylan","Sabrina","Brina","Salal","Sanborn","Sanders","Sandon","Sanford","Sawyer","Scarlet","Scarlett","Scott","Seabert","Seaton","Selby","Severin","Seward","Seymour","Shandy","Sharman","Shaw","Shelby","Sheldon","Shelley","Shepherd","Sherlock","Sherman","Sherwood","Shipley","Shirley","Siddel","Skeet","Skye","Skyla","Skylar","Slade","Smith","Snowden","Spalding","Sparrow","Spencer","Spike","Spring","Standish","Stanford","Stanislaw","Stanley","Stanley","Stan","Stanway","Sterling","Sterne","Stockard","Stoke","Stokley","Storm","Stroud","Studs","Summer","Sunny","Sutton","Swain","Tab","Tanner","Tate","Tatum","Tawnie","Taylor","Telford","Tem","Tennyson","Terrel","Thane","Thatcher","Thistle","Thorne","Thorpe","Thurlow","Tilden","Tina","Todd","Tomkin","Townsend","Tranter","Tremayne","Trey","Tripp","Trudy","Truman","Tucker","Tuesday","Turner","Twain","Tye","Tyler","Tyne","Udolf","Ulla","Ulrich","Ulrika","Unity","Unwin","Upshaw","Upton","Vala","Vance","Velvet","Verity","Vian","Wade","Wakefield","Walker","Wallace","Walton","Ward","Warren","Washington","Watson","Waverly","Wayland","Waylen","Wayland","Wayne","Webster","Welcome","Wells","Wendy","Wesley","West","Weston","Wetherby","Wheaton","Wheeler","Whit","Whitfield","Whitlaw","Whitney","Wilfred","Willow","Wilmer","Wilona","Winifred","Winslow","Winston","Winter","Winthrop","Wolf","Woodley","Woodrow","Woodward","Wright","Wyatt","Wylie","Wyndam","Wyndham","Yardley","Yates","Yedda","Yeoman","York","Yule","Zane","Zelene","Zinnia","Allen","Austin","Avery","Bryant","Elmer","Emmett","Everett","Garrett","Gary","Jackson","Larkin","Lark","Lamont","Lawrence","Madison","Merle","Merrill","Mitchell","Morris","Nelson","Otis","Pierce","Stacy","Stacey","Willard","Willis","Wilson","Wyatt","Ainsley","Alton","Ashley","Bailey","Barrington","Bentley","Beverly","Bradford","Bradley","Brady","Brent","Brock","Brooke","Byron","Camden","Carlton","Chester","Clay","Clayton","Clifford","Clifton","Clinton","Clive","Colton","Dale","Dalton","Dana","Darby","Denzil","Digby","Drake","Dudley","Easton","Forrest","Glanville","Grover","Hailey","Haley","Hartley","Heath","Holden","Kelsey","Kendall","Kent","Kenton","Kimberly","Landon","Lee","Lester","Milton","Nash","Norris","Odell","Perry","Peyton","Preston","Rodney","Royston","Shelby","Sheldon","Shirley","Stanley","Stanton","Vance","Van","Wade","Wesley","Whitney","Winston","Woodrow","Roscoe","Barrie","Barry","Colby","Courtney","Courtenay","Darcy","Darrell","Darryl","Lacey","Lance","Lane","Leland","Montague","Mortimer","Morton","Neville","Percy","Sacheverell","Troy","Vernon","Warren","Blake","Brady","Brett","Cade","Chance","Cole","Curtis","Dana","Drew","Franklin","Scott","Tate","Todd","Truman","Wendell","Wynne","Bailey","Baron","Booker","Brewster","Carter","Chandler","Chauncey","Chase","Clark","Cooper","Cody","Cordell","Dexter","Earl","Garnet","Hunter","Jagger","Marshall","Mason","Millard","Page","Paige","Parker","Sherman","Tanner","Taylor","Tucker","Tyler","Travis","Spencer","Walker","Wayne","Bruce","Graham","Lyle","Grant","Ross","Wallace","Stuart","Dallas","Gordon","Kirk","Lindsay","Lindsey","Maxwell","Ramsay","Rutherford","Blair","Douglas","Keith","Kyle","Ross","Sterling","Boyd","Cameron","Cambell","Doyle","Mackenzie","Mckinley","Irving","Logan","Barry","Cody","Darcy","Desmond","Grady","Kelley","Kelly","Kennedy","Sullivan","Barrington","Barry","Brady","Carroll","Casey","Cassidy","Cody","Donovan","Fallon","Hogan","Keegan","Quinn","Sheridan","Corey","Cory","Delaney","Perry","Craig","Kendall","Trevor","Meredith","Vaughan","Wynne"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_FRANCE" :
							{
								"PRE" : ("St. ","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""),
								"MID" : ("Adora","Alavda","Aleron","Algernon","Amarante","Ancel","Andrew","Angevin","Aramis","Armand","Audric","Babette","Bailey","Bari","Barry","Bayard","Beau","Beaumont","Bebe","Bedelia","Bellamy","Belle","Belle","Bella","Berangèr","Berenger","Boden","Bogart","Bonamy","Boswell","Boyce","Bret","Briand","Brie","Brier","Bruce","Byron","Cable","Campbell","Carel","Caresse","Carissa","Caron","Carrie","Caroline","Case","Chancellor","Chandler","Chanel","Chaney","Chantal","Chapin","Charlene","Charlotte","Chase","Cheney","Cheryl","Chevalier","Ciel","Corbin","Crescent","Cyprien","Dacio","Darell","Dartagnan","Deja","Delano","Delmar","Demi","Destinee","Destry","Diamanta","Dominique","Donatien","Doreen","Dori","Drew","Egil","Elaine","Elise","Elita","Eliza","Elle","Eloise","Etienne","Fantine","Fawne","Faye","Fayme","Felicite","Flannery","Fleur","Forest","Foster","Frank","Franklin","Fraser","Frasier","Gareth","Garland","Gay","Gaye","Gaylord","Geneva","Genevieve","Germain","Ghislaine","Granville","Grosvenor","Guy","Hamlin","Harcourt","Iolanthe","Jaimie","Jamari","Javier","Jean","Jeanne","Jenay","Jolie","Lacy","Lance","Laverna","Laverne","leala","leroy","Liana","Linette","Linus","Lionel","Lyle","Mabel","Macy","Magnolia","Maine","Mala","Marcel","Margot","Marguerite","Marian","Marianne","Marie","Marjorie","Marlon","Marshall","Marvelle","Maslin","Mason","Maurice","Mercy","Merci","Michelle","Mignon","Montague","Montgomery","Mortimer","Musetta","Neville","Noel","Noella","Noelle","Norman","Norris","Odelette","Odetta","Odette","Odil","Olive","Oliver","Orane","Oriel","Orville","Page","Pansy","Papillon","Pascal","Pascale","Percival","Percival","Percy","Pierre","Porter","Prewitt","Purvis","Quennel","Quennell","Questa","Quincy","Quiterie","Raissa","Rance","Ranger","Ray","Remy","Riva","Rochelle","Roslin","Roy","Ruby","Rush","Russel","Russell","Sargent","Searlait","Seaton","Sennett","Seymour","Shannelle","Shantay","Shantelle","Sigourney","Sinclair","Sinjon","Solange","Soleil","Sumner","Sydney","Talbot","Tayce","Taylar","Telo","Tempest","Tenenan","Thibaud","Thosa","Tiffany","Tracy","Travis","Travis","Travers","Tremeur","Trifine","Troilus","Troy","Tudi","Tugdual","Tujan","Turiau","Tyson","Ursanne","Vachel","Vail","Valeray","Valerie","Vallis","Varden","Vardon","Varocher","Vedette","Vere","Verney","Vernon","Verrin","Vinvella","Voletta","Warren","Yannick","Yvonne","Abadie","Abbe","Achard","Adam","Aigremont","Alain","Albert","Alein","Alexandre","Allaire","Allard","Allemand","Amyot","Andre","Andrieu","Antoine","Archambault","Armand","Arnaud","Arpin","Arrive","Asselin","Aube","Aubert","Aubertin","Aubin","Aubry","Auclerc","Audet","Auger","Augereau","Aurelle","Auriole","Babin","Bachelier","Bacon","Baillon","Balan","Barbe","Barbeau","Barbier","Bard","Bardeau","Bardot","Barette","Baril","Barnabe","Baron","Barre","Barthelemy","Basque","Basset","Bastide","Bataille","Baudet","Baudin","Baudoin","Baudry","Bazin","Beaubois","Beauchamp","Beauchesne","Beauclair","Beaudet","Beaudouin","Beaufort","Beaujeu","Beaulieu","Beaumont","Beaupre","Beauregard","Beauvais","Beauvoir","Bechard","Belair","Belard","Bellanger","Belle","isle","Bellemare","Bellevaux","Belmont","Benard","Benoist","Benoit","Berard","Berger","Bergeron","Bergevin","Berlo","Bernard","Bernier","Berthelot","Berthier","Bertin","Bertrand","Besse","Besset","Besson","Bibau","Bigot","Billard","Binet","Biron","Bisson","Bissot","Blain","Blais","Blaise","Blanc","Blanchard","Blanchet","Blin","Blondeau","Blot","Blouin","Bodin","Boileau","Bois","Boisseau","Boivert","Boivin","Bombarde","Boncourt","Bonhomme","Bonin","Bonnaire","Bonnard","Bonneau","Bonnefoix","Bonnet","Bonnin","Bordes","Bosse","Bouchard","Bouche","Boucher","Bouchet","Boudet","Boulanger","Boulay","Boulet","Bouquet","Bourbon","Bourgeois","Bourgoin","Bourree","Bousquet","Boutet","Boutillier","Boutin","Bouvet","Bouvier","Boyer","Brabant","Brassard","Breau","Breton","Briand","Bridot","Briene","Brin","Brisson","Brossard","Brosset","Broussard","Brousse","Bruley","Brullet","Brun","Bruneau","Brunel","Brunet","Bruyere","Bugeaud","Buisson","Bureau","Cailly","Campagne","Camus","Carbonneau","Cardinal","Carlier","Caron","Carpentier","Carre","Carreau","Carrier","Carriere","Cartier","Castel","Cauchon","Cavelier","Chabert","Chabot","Chabrieres","Chalon","Chambly","Champeaux","Champion","Chapelain","Chapelle","Chapellier","Chaperon","Charette","Charles","Charlot","Charon","Charrette","Charrier","Charron","Chauvet","Chauvin","Chenart","Chenier","Chesnay","Chesne","Chevalier","Chevrier","Chirac","Chouet","Chrestien","Chretien","Clavel","Clemenceau","Clement","Clerc","Clermont","Coffin","Coin","Colas","Colbert","Colin","Collard","Collet","Collin","Combe","Comiers","Comte","le","Constant","Constantine","Coq le","Corbin","Cordier","Cormier","Cornu","Corre le","Coste","Coulon","Court","Cousin","Cousinot","Couture","Couturier","Cros","Crosnier","Crozet","Daigremont","D'amours","Daniel","David","Delahaye","Delisle","Delmas","Delorme","Denis","Denys","Deschamps","Deshayes","Desjardins","Desmarais","Desprez","Desvilliers","Devaux","Didier","Doucet","Dubois","Dubreuil","Duclos","Dufaux","Dufour","Dufresne","Dugas","Duguay","Duhamel","Dumas","Dumay","Dumont","Dumoulin","Dupin","Dupont","Dupre","Dupuis","Dupuy","Durand","Duval","Etienne","Evrard","Fabre","Faucher","Faure","Ferrand","Fillion","Fleury","Fontaine","Forest","Forestier","Fort","Fortin","Fosse","Foucaud","Foucault","Foucher","Fougeres","Fouquet","Fournier","Francois","Frenier","Gagne","Gagnon","Gaillard","Galland","Gallet","Garneau","Garnier","Gauthier","Gautier","Gendron","Geoffroy","Georges","Gerard","Germain","Gervais","Gibert","Gillet","Girard","Giraud","Godard","Gosselin","Goullet","Goyer","Goyet","Grandjean","Grangers","Gregoire","Gros","Guerin","Guichard","Guillaume","Guillon","Guillot","Hubert","Huet","Huguet","Humbert","Imbert","Jacob","Jacquemin","Jacques","Jacquet","Jardin","Jean","Jerome","Jobidon","Jobin","Joly","Joseph","Joubert","Jourdain","Jouve","Jouy","Lacoste","Lacour","Lacroix","Ladoucette","Lafont","Lalande","Lalane","Lambert","Langlois","Laporte","Laroche","Lasseur","Laurent","Lauzon","Laval","Lavallee","Lavergne","Lavoir","le goff","leblanc","lebon","lebrun","leclerc","lecomte","lefebvre","lefevre","leger","legrand","lemaire","lemoine","lemonnier","leon","leonard","lepage","leroux","leroy","lesage","Louis","Lucas","Maillard","Maillet","Maillot","Maire","Mallet","Marc","Marchal","Marchand","Marechal","Marie","Marin","Marquet","Martin","Martinais","Martineau","Martinet","Masson","Mathieu","Maury","Menard","Mercier","Meunier","Meyer","Michaud","Michel","Millet","Monnier","Montagne","Monteil","Montfort","Montigny","Montmorency","Morand","Moreau","Morel","Morin","Moulin","Mounier","Mouton","Muller","Nicolas","Noel","Olive","Olivet","Olivier","Origny","Orleans","Ouvrard","Page","Paget","Paradis","Parent","Parisot","Parmentier","Pellerin","Pelletier","Perrault","Perret","Perrier","Perrin","Perrot","Petit","Philippe","Picard","Pichon","Picot","Pierre","Pillon","Poirier","Poisson","Poitiers","Poulain","Poullin","Prat","Prevost","Prigent","Proust","Provost","Prudhomme","Puget","Quesnel","Racine","Ratelle","Raynaud","Remy","Renard","Renaud","Renault","Rey","Richard","Richer","Riel","Rioux","Riviere","Roberge","Robert","Robillard","Rochefort","Roger","Roland","Rousseau","Roussel","Roux","Roy","Royer","Simon","Soullier","Laurent","Amour","Andre","Aubin","Croix","Denis","Etienne","George","Germain","Jacques","Jean","Joseph","Julien","leger","Marc","marie","martin","michel","Paul","Sylvestre","Tardif","Terrien","Tessier","Thebaud","Thibaudeau","Thierry","Thomas","Touchet","Tournier","Tremblay","Turpin","Vacher","Vachon","Vaillant","Vanier","Vasseur","Verdier","Vidal","Vignaux","Vigne de la","Villeneuve","Vincent"),
								"END" : ()
							},
							"CIVILIZATION_GERMANY" :
							{
								"PRE" : ("Abelard","Adalgisa","Adalgiso","Adalia","Adelbert","Adelfried","Adelina","Adelino","Adelmo","Ademaro","Adler","Adolfina","Adolph","Agneta","Ahren","Alaric","Albert","Alberta","Aldous","Alger","Alice","Alphonse","Amara","Ancel","Antje","Arabelle","Arnold","Aubrey","Ava","Baldwin","Barend","Bergen","Berit","Bernadette","Bernard","Berta","Bertram","Bingham","Blaz","Bluma","Brandeis","Brunhilde","Burke","Callan","Carleigh","Caroline","Cecania","Chay","Chloris","Clay","Conrad","Cort","Dagmar","Dagna","Dagobert","Dame","Derek","Dieter","Dietlinde","Dustin","Dutch","Ebba","Eberhard","Edwin","Edwina","Egbert","Egmont","Eldwin","Elisabeth","Ellery","Emery","Emil","Emily","Emma","Erika","Ernest","Ernestine","Faiga","Ferdinand","Floy","Frederick","Frederika","Fremont","Frieda","Galiana","Garin","Geert","Gerard","Gerda","Gilbert","Giselle","Gretchen","Hackett","Hahn","Hank","Hastings","Heidi","Heller","Helmuth","Henrietta","Henry","Herman","Horst","Idonia","Ilse","Imre","Jarvia","Jarvinia","Jenell","Johann","Kasch","Kay","Kellen","Kerstin","Kiefer","Lamar","Lance","Lancelot","Lear","Leonard","Leo","Leon","Leopold","Leopolda","Leyna","Liese","Lorelei","Loring","Lorraine","Louis","Lewis","Louise","Luther","Madison","Mallory","Manfred","Marlene","Mathilda","Maud","Mayer","Merrill","Meyer","Millicent","Minna","Morgen","Nevin","Nixie","Norbert","Norberta","Nordica","Odelia","Odell","Olinda","Omar","Orlantha","Otis","Penrod","Pepin","Raymond","Raynard","Redmond","Richard","Richelle","Ring","Ritter","Roderica","Roderick","Roger","Roland","Roth","Rudolph","Schmetterling","Senta","Serilda","Sonnenschein","Stein","Strom","Tab","Theobold","Ula","Ulbrecht","Ulrika","Ulva","Unna","Uta","Varick","Verner","Vid","Vilhelm","Viveka","Volker","Waggoner","Walter","Wanda","Warner","Warren","Yale","Yohann","Zelda","Zelig","Zelinda","Zelma","Albrecht","Alt","Baer","Becker","Berger","Bernhard","Bach","Bacher","Bacher","Boehm","Behn","Bieber","Betz","Bischof","Schwarz","Portner","Bauer","Baumann","Beyer","Bruckner","Breitenbach","Braun","Brupbacher","Zimmerman","Gerber","Claborg","Klein","Klause","Bottcher","Kraemer","Krebs","Kalb","Durr","Ehrhard","Eschlimann","Eberhard","Fehr","Bauer","Veit","Vogt","Vogel","Fuchs","Frohlich","Friedrich","Fuehre","Fery","Frey","Volmar","Gehring","Goring","Goering","Gaertner","Gos","Goes","Gut","Guth","Hofer","Hoefer","Haintz","Hermann","Hirtzel","Heinrich","Heintz","Huber","Hofstetter","Jager","Tschantz","Kehl","Kuhn","Kurrer","Kummel","Konig","Konigsamen","Kunzi","Klein","Kneissli","Kraemer","Liess","Klein","Lebengut","Lang","Meyer","Musser","Messerschmidt","Muller","Miswchler","Mohr","Meyer","Neumann","Neu","Nussli","Eichli","Oberholtzer","Pfeiffer","Printz","Riese","Rohrig","Reinoehl","Roth","Reiss","Reichert","Reinhard","Seiler","Schaffer","Schertz","Schumacher","Schaumer","Schnaebeli","Schultz","Schlegel","Schleiermacher","Klein","Schmeisser","Schnaebeli","Schnell","Sauter","Sauer","Spengler","Staheli","Stein","Steiner","Strasbach","Schweiger","Schwab","Schneider","Trachsel","Dreher","Theissen","Wannemacher","Weber","Walti","Wirtz","Widmann","Weiand","Wilhelm","Widmer","Jager","Yost","Jung","Zurcher","Zug"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_GREECE" :
							{
								"PRE" : ("Ant","Ap","Aph","Ar","Ascl","Art","Ath","Atl","C","Cr","D","Dem","Dion","Epim","Er","G","H","Hel","Heph","Iap","Hyp","M","Mn","Oc","Pers","Ph","Pos","Prom","Rh","T","Th","Ur","Z"),
								"MID" : ("a","ae","e","ea","ei","emo","eu","i","ia","io","iu","o","oe","y"),
								"END" : ("be","ctor","dite","don","lius","llo","mis","na","ne","nus","phon","phone","pius","rion","rmes","rus","s","stia","stus","sus","syne","ter","theus","thys","tus","us")
							},
							"CIVILIZATION_INCA" :
							{
								"PRE" : ("Ah","Akh","Bac","Cent","Chalch","Ch","Ci","Ehe","Ek","Huitz","Itz","Ix","Kan","Kis","Kuk","Mac","May","Metz","Mic","N","Om","Pat","Pay","Quetz","Teoy","Tl","Tlatz","Ton","Xil","Xoch","Yac","Yax","Yuc","Yum"),
								"MID" : ("in","pu","papa","uayey","au","ma","ilopo","u","one","a","ipi","e","ao","alo","uilxo","eo","icome","aha","hua","iuhtli","atiu","anti","acatechu","etecu"),
								"END" : ("chil","tl","can","tlilton","tab","coatl","lcoati","lotl","chtli","kaax","mqui","lli","chitl","huel","htli","ch","c","co","chamah","tli","catl","tan","kiq","tlan","con","tecuhtil","nal","shtal","u","bs","h","tl","cue")
							},
							"CIVILIZATION_INDIA" :
							{
								"PRE" : ("adhir","adi","aditya","ajit","amar","amarjit","amit","amita","anadi","anita","anjali","anup","anupam","anupama","apu","arun","aruna","arup","arupa","ashok","ashoka","asim","asit","atul","atula","avay","avi","avimanyu","avishek","babul","badal","bahuguna","bahula","bakul","bakula","baladeva","balakrishna","balaram","bali","bani","barsha","barun","baruna","basabi","basanta","benimadhava","bhadra","bhagvati","bhagya","bhakti","bharadwaj","bhima","bimal","biman","bindu","binod","binoy","bipul","biswajit","chaita","chaitali","chaitanya","chaiti","chand","chanda","chandra","chandrashekhar","chinmoy","chitra","chitralekha","chuni","devi","durga","diksha","dikcha","dola","divya","devajit","devjani","daya","din","dinbandhu","deva","devjani","darpan","ekanantha","eka","fani","falgun","falguni","garuda","geeta","gaja","ganga","gaya","gajanan","ganesh","guni","gita","gayatri","gopa","gopinath","govinda","guru","hans","hansmukh","hasi","hemanta","hemanti","hemayanti","hira","hiren","hridaya","indra","indira","indrajit","ipsita","indrani","indranil","jagriti","jamuna","jas","jasbindar","jit","jitendra","jitu","jugal","jwala","jyoti","jyotirmai","kamal","kamala","kamalesh","kanai","karuna","kaushik","kautilya","kaveri","kavi","kaviraj","kavita","keshava","keshta","khusi","kiran","kiran","kirti","kripal","krishna","kriti","kritivasa","kuber","kumar","kumari","kushan","kutil","labani","labanya","lakchmi","lakkhi","lalit","lalita","lalu","lok","loknath","lokpal","","","madanmohan","madhab","madhu","madhusudan","maharshi","mahavir","mahesh","manik","manohar","menaka","mithun","mohan","mridula","","","","nandita","nani","nanigopal","narayan","narayani","nidhi","nikhilesh","nila","nilam","nilkanta","nirmal","nirmalendu","nita","nitesh","nritya","om","omprakash","","","panna","parmeswar","patanjali","phani","phalgun","phalguni","pratap","priti","priya","priyatam","priyatama","purush","purushottam","pushpa","pushpita","rani","ranjan","ranjana","ranjita","rasmi","ravi","ravindra","ravindra","renu,rini","rishi","ritin","roma","","","sujata","sulekha","suman","sundar","sundari","suparna","suresh","sureshwar","surma","susama","susmita","suvarna","suvendu","tanuja","tapti","tarun","taruna","tej","tejpal","tista","tribeni","tripura","uday","uma","urmila","vayu","varsha","varun","varuna","vasabi","vasanta","venimadhava","vadra","vagya","varadwaj","vidyut","vijay","vijaya","vimla","vishnu","vivek","yadav","yadu"),
								"MID" : (),
								"END" : ("adhir","adi","aditya","ajit","amar","amarjit","amit","amita","anadi","anita","anjali","anup","anupam","anupama","apu","arun","aruna","arup","arupa","ashok","ashoka","asim","asit","atul","atula","avay","avi","avimanyu","avishek","babul","badal","bahuguna","bahula","bakul","bakula","baladeva","balakrishna","balaram","bali","bani","barsha","barun","baruna","basabi","basanta","benimadhava","bhadra","bhagvati","bhagya","bhakti","bharadwaj","bhima","bimal","biman","bindu","binod","binoy","bipul","biswajit","chaita","chaitali","chaitanya","chaiti","chand","chanda","chandra","chandrashekhar","chinmoy","chitra","chitralekha","chuni","devi","durga","diksha","dikcha","dola","divya","devajit","devjani","daya","din","dinbandhu","deva","devjani","darpan","ekanantha","eka","fani","falgun","falguni","garuda","geeta","gaja","ganga","gaya","gajanan","ganesh","guni","gita","gayatri","gopa","gopinath","govinda","guru","hans","hansmukh","hasi","hemanta","hemanti","hemayanti","hira","hiren","hridaya","indra","indira","indrajit","ipsita","indrani","indranil","jagriti","jamuna","jas","jasbindar","jit","jitendra","jitu","jugal","jwala","jyoti","jyotirmai","kamal","kamala","kamalesh","kanai","karuna","kaushik","kautilya","kaveri","kavi","kaviraj","kavita","keshava","keshta","khusi","kiran","kiran","kirti","kripal","krishna","kriti","kritivasa","kuber","kumar","kumari","kushan","kutil","labani","labanya","lakchmi","lakkhi","lalit","lalita","lalu","lok","loknath","lokpal","","","madanmohan","madhab","madhu","madhusudan","maharshi","mahavir","mahesh","manik","manohar","menaka","mithun","mohan","mridula","","","","nandita","nani","nanigopal","narayan","narayani","nidhi","nikhilesh","nila","nilam","nilkanta","nirmal","nirmalendu","nita","nitesh","nritya","om","omprakash","","","panna","parmeswar","patanjali","phani","phalgun","phalguni","pratap","priti","priya","priyatam","priyatama","purush","purushottam","pushpa","pushpita","rani","ranjan","ranjana","ranjita","rasmi","ravi","ravindra","ravindra","renu,rini","rishi","ritin","roma","","","sujata","sulekha","suman","sundar","sundari","suparna","suresh","sureshwar","surma","susama","susmita","suvarna","suvendu","tanuja","tapti","tarun","taruna","tej","tejpal","tista","tribeni","tripura","uday","uma","urmila","vayu","varsha","varun","varuna","vasabi","vasanta","venimadhava","vadra","vagya","varadwaj","vidyut","vijay","vijaya","vimla","vishnu","vivek","yadav","yadu")
							},
							"CIVILIZATION_JAPAN" :
							{
								"PRE" : ("fuka","asa","mae","yoko","nishi","kita","higashi","minami","ao","aka","kuro","kiyo","iwa","ishi","matsu","sugi","take","ki","ita","yone","hayashi","bayashi","ue","kami","shita","shimo","hashi","bashi","mori","tsuka","mizu","moto","naka","uchi","yama","oka","saka","no","ike","kawa","tani","sawa","zawa","numa","hata","bata","ta","da","shima","jima","mura","saki","zaki"),
								"MID" : ("","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","fuka","asa","mae","yoko","nishi","kita","higashi","minami","ao","aka","kuro","kiyo","iwa","ishi","matsu","sugi","take","ki","ita","yone","hayashi","bayashi","ue","kami","shita","shimo","hashi","bashi","mori","tsuka","mizu","moto","naka","uchi","yama","oka","saka","no","ike","kawa","tani","sawa","zawa","numa","hata","bata","ta","da","shima","jima","mura","saki","zaki"),
								"END" : ("","","","","","","","","","","","","","","","","","","aki","fumi","go","haru","hei","hiko","hisa","hide","hiro","ji","kazu","ki","ma","masa","michi","mitsu","nari","nobu","nori","o","rou","shi","shige","suke","ta","taka","to","toshi","tomo","ya","zou","a","chi","e","ho","i","ka","ki","ko","mi","na","no","o","ri","sa","ya","yo","ichi","kazu","ji","zo","ko","mi","hime")
							},
							"CIVILIZATION_KOREA" :
							{
								"PRE" : ("An","An","Ahn","Ahn","Cha","Ch'a","Ch'eon","Ch'oe","Cho","Choe","Choi","Choi","Cho'i","Chang","Ch'ang","Jang","Jang","Kang","Cheon","Cheon","Cheong","Cheong","Cheong","Cheong","Cho","Cho","Cho","Cho","Cho","Cho","Cho","Cho","Cho","Chu","Ha","Ha","Ha","Han","Han","Han","Heo","Hong","Hong","Hong","Hong","Hwang","Hwang","Hyeon","Im","Im","Kang","Kang","Kang","Kang","Kang","Kang","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Ko","Ko","Ko","Go","Go","Kong","Kweon","Kweon","Kwun","Gueon","Mok","Mun","Moon","Na","Nam","No","No","O","Oh","Ok","Paek","Baik","Baek","Pak","Pak","Pak","Park","Park","Park","Park","Park","Park","Park","Park","Park","Park","Park","Park","Seo","Seo","Seo","Sim","Shim","Song","Weon","Won","Yang","Yang","Yang","Ye","Rui","Yeom","Yeom","Yi","Yi","Yi","Yi","Yi","Yi","Yi","Li","Li","Li","Li","Li","Li","Li","Li","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Yu","Yu","Yu","Yu","Yoo","Yoo","Ryu","Yun","Yun","Yun","Yun","Yoon","Yoon","An","An","Ahn","Ahn","Cha","Ch'a","Ch'eon","Ch'oe","Cho","Choe","Choi","Choi","Cho'i","Chang","Ch'ang","Jang","Jang","Kang","Cheon","Cheon","Cheong","Cheong","Cheong","Cheong","Cho","Cho","Cho","Cho","Cho","Cho","Cho","Cho","Cho","Chu","Ha","Ha","Ha","Han","Han","Han","Heo","Hong","Hong","Hong","Hong","Hwang","Hwang","Hyeon","Im","Im","Kang","Kang","Kang","Kang","Kang","Kang","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Kim","Ko","Ko","Ko","Go","Go","Kong","Kweon","Kweon","Kwun","Gueon","Mok","Mun","Moon","Na","Nam","No","No","O","Oh","Ok","Paek","Baik","Baek","Pak","Pak","Pak","Park","Park","Park","Park","Park","Park","Park","Park","Park","Park","Park","Park","Seo","Seo","Seo","Sim","Shim","Song","Weon","Won","Yang","Yang","Yang","Ye","Rui","Yeom","Yeom","Yi","Yi","Yi","Yi","Yi","Yi","Yi","Li","Li","Li","Li","Li","Li","Li","Li","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Lee","Yu","Yu","Yu","Yu","Yoo","Yoo","Ryu","Yun","Yun","Yun","Yun","Yoon","Yoon","Cho","yeong","Kwan","uk","Tal","hun","Yeong","kil","Min","su","Su","kweon","P'ung","cho","Ch'ang","weon","Ch'eol","han","Kyu","pyeong","Min","sik","Mun","yeong","Myeong","hun","Chu","chu","Myeong","han","Su","yeong","Tu","chin","Seu Wien","Yeong","seon","Hyeon","san","Su","hyeon","Tae","sang","Tong","sik","Ch'i","hun","Han","seung","Hun","hyeon","Hye","yeon","Nam","ch'eol","Sang","yeon","Seon","chin","Tae","hyeon","Yeong","suk","Hyeong","uk","Ch'an","seok","Ho","cheong","Yeong","il","Ch'eol","kyun","Chong","chin","Hae","weon","Chang","heui","Chang","sik","Chong","hyeon","Kkoch'","no","eul","T'ae","seon","Yeom","Weon","chun","Mi","chin","Chang","sik","Seon","keun","Sun","t'aek","Ch'eol","min","Chi","seong","Hun","Man","u","Mun","ch'eol","Seung","heui","Ch'an","u","Chae","ku","Ch'eol","chung","Chong","chun","Chong","su","Chu","ho","Chun","yeong","Chwa","ki","Hak","su","Heui","chung","Hye","min","Hyeon","cheong","Hyo","cheong","Hyo","kon","Ik","yeong","Il","hwan","In","Kang","keun","Ki","heon","Kwang","sik","Man","su","Min","heui","Myeong","hwan","Myeong","wan","Pyeong","min","Seok","heung","Seong","rae","Seong","ryong","Su","chang","Su","yeong","Seung","chun","T'ae","hyang","Teok","kyu","Tong","myeon","Tong","yeop","Weon","Yeong","hwan","Yeong","sam","Yun","t'ae","Chae","heui","Chae","pong","Kwang","myeong","Kwang","rak","Pyeong","chu","Hyo","chin","Kap","yong","Kyeong","eon","O","min","Chin","seok","Myeong","keun","Yong","chik","Chong","hun","h'i","hyeong","Chun","hwan","Yeong","ha","Kyu","ch'eol","Song","saeng","Teuk","chin","Heung","su","Seong","ho","Tae","hyeon","Chi","eun","Chi","hun","Chin","yeol","Cheong","sang","Chong","yeol","Pyeong","kyu","Sang","ton","Seong","su","Seung","ch'eol","Seung","hyeon","Seung","mun","Yeong","ch'an","Yeong","hun","Mu","sang","Neung","uk","Pong","su","Chong","sik","T'ae","kon","Seong","chin","Chae","ho","Keon","Sang","kuk","Nae","wi","Ch'an","su","Cheong","hun","Ch'ang","ho","Ch'ang","se","Chae","ung","Chi","hyeon","Cheong","u","Cheong","weon","Chu","yong","Chun","hak","Hong","yeol","Heui","seong","Hyeon","uk","Hyeong","ro","Kang","il","Ki","seop","Kwan","ch'eol","Min","chin","Pong","keun","Sang","ch'eol","Sang","hun","Se","tol","Seong","chae","Ta","hye","Tong","kyu","Yeong","sin","Yong","ch'an","Yong","su","Ch'ang","hyeok","Chae","hyeong","Chae","seong","Keon","chae","Kyeong","min","Pyeong","ho","Si","hun","Chong","seop","Hyeok","Hyeon","seok","Ki","hyeon","Seong","hyeon","Yeong","min","Yeong","seon"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_MALI" :
							{
								"PRE" : ("Abdul","","Al","","Abdel","","'Abd al","Aban","Abbas","Abbud","Abbudin","'Adl","Ahad","Alim","Aliyy","Azim","Aziz","Badi","Ba'ith","Baqi","Bari","Barr","Basir","Basit","Fattah","Ghaffar","Ghafur","Ghani","Hadi","Hafiz","Hakam","Hakim","Halim","Hamid","Haqq","Hasib","Hayy","Jabbar","Jalil","Karim","Khabir","Khaliq","Latif","Malik","Majid","Matin","Mubdi'","Mughni","Muhaimin","Muhsi","Muhyi","Mu'id","Mu'izz","Mujib","Mu'min","Muqaddim","Muqtadir","Musawwir","Muta'al","Nafi'","Nasser","Nasir","Nur","Qadir","Qahhar","Qawi","Qayyum","Quddus","Rafi'","Rahim","Rahman","Rashid","Ra'uf","Razzaq","Sabur","Salam","Samad","Sami","Sattar","Shahid","Shakur","Tawwab","Wadud","Wahhab","Wahid","Wajid","Wakil","Wali","Waliy","Warith","Zahir","Abdullah","'Abid","'Abidin","Abu Bakr","Abu al Khayr","Adan","Adel","'Adil","Adham","Adib","'Adli","Adnan","'Adnan","'Afif","Afeef","Ahmad","Ahmed","'Ajib","'Akif","Akil","Akram","Ala'","Ala' al Din","Al 'Abbas","Aladdin","Ala' al din","Al Bara'","Al Hakam","Al Harith","Alhasan","Alhusain","Alhusayn","Ali","'Ali","'Aliyy","Alim","Almahdi","Al Safi","Altaf","Altair","Al Tayyib","Al Tijani","Al Tufail","Al Tufayl","Amid","'Amid","Amin","Ameen","Amir","Ameer","'Amir","Amjad","Ammar","'Ammar","'Amro","Anas","Anis","'Antarah","Anwar","'Aqil","Arfan","Arif","'Arif","Asad","As'ad","Asadel","Ashraf","Asif","Asim","'Asim","Aswad","Ata'","'Ataa","Ata' Allah","Ata' al Rahman","Athil","Athir","Atif","'Atif","Awad","'Awad","'Awf","Aws","Awwab","Ayham","Ayman","Ayser","Ayyub","Ayoob","Aza","'Azab","Azhar","Azeem","Azim","Aziz","'Aziz","Azzam","'Azzam","Badi","Badi al Zaman","Badr","Badr al Din","Badri","Baha","Baha'","Baha al Din","Bahiyy al Din","Bahij","Bahir","Bakr","Bakri","Baligh","Bandar","Barakah","Barir","Bashir","Bashshar","Basil","Basim","Bassam","Bayhas","Bilal","Bishr","Boulos","Budail","Budayl","Burhan","Bushr","Butrus","Dabir","Dani","Darwish","Da'ud","Dawud","Dhakir","Dhakiy","Dhakwan","Dhul Fiqar","Dirar","Diya","Diya al Din","Duqaq","Fadi","Fadil","Fadl","Fadl Allah","Fahd","Fahad","Fahmi","Faisal","Faysal","Fa'iz","Fakhir","Fakhr al Din","Fakhri","Fakhry","Fakih","Falah","Falih","Faraj","Farraj","Farhan","Farid","Fareed","Fariq","Fareeq","Faris","Faruq","Farooq","Fath","Fathi","Fatih","Fatin","Fateen","Fawwaz","Fawzan","Fawzi","Fayyad","Ferran","Fida","Fikri","Firas","Fouad","Fu'ad","Fudail","Gamal","Gamali","Ghaith","Ghayth","Ghali","Ghalib","Ghanim","Ghassan","Ghawth","Ghazi","Ghazwan","Ghiyath","Habbab","Habib","Hadad","Haddad","Hadi","Hafiz","Hakem","Hakim","Hakeem","Halim","Hamal","Hamas","Hamdan","Hamdi","Hamid","Hamim","Hamzah","Hana","Hana'i","Hanbal","Hani","Hanif","Hannad","Haris","Harith","Haroun","Harun","Hashim","Hassan","Hatim","Haydar","Haytham","Hayyan","Hazim","Hilal","Hilel","Hilmi","Hisham","Hud","Houd","Hudad","Hudhafah","Hudhaifah","Hudhayfah","Humam","Husain","Husayn","Hussein","Husam","Husam al Din","Ibrahim","'Id","Idris","Ihsan","Ihtisham","'Ikrimah","Ilias","Imad","'Imad","Imad al Din","Imam","Imran","'Imran","Imtiyaz","In'am","Iqbal","Irfan","'Irfan","Isa","'Isa","Eisa","Isam","'Isam","Issam","Ishaq","Isma'il","Iyad","Iyas","Izz al Din","Jabalah","Jabbar","Jabr","Jabir","Jad Allah","Jafar","Ja'far","Jal","Jalal","Jalal al Din","Jalil","Jaleel","Jamal","Jamal al Din","Jamil","Jameel","Jarir","Jasim","Jaul","Jaun","Jawad","Jawdah","Jawhar","Jibran","Jibril","Jihad","Jubair","Jubayr","Jul","Jumah","Jumu'ah","Junaid","Junayd","Juwain","Juwayn","Kadar","Kedar","Kadeen","Kadin","Kadeer","Kadir","Kahil","Kaliq","Kamal","Kamil","Kameel","Karam","Kardal","Karif","Kareef","Karim","Kareem","Kasib","Kaseeb","Kaseem","Kasim","Kateb","Katib","Kazim","Khalaf","Khaldun","Khaldoon","Khalid","Khaled","Khalifah","Khalil","Khaleel","Kalil","Khalil al Allah","Khalis","Khatib","Khair al Din","Khairi","Khairy","Khayri","Khoury","Khulus","Khuzaimah","Khuzaymah","Kutaiba","Labib","Labeeb","Lablab","Latif","Layth","Lu'ay","Lubaid","Lubayd","Luqman","Lut","Lutfi","Ma'd","Madani","Mahbub","Mahdi","Mahfuz","Mahir","Mahjub","Mahmud","Mahmoud","Mahrus","Maimun","Maymun","Majd","Majdy","Majd al Din","Majid","Makin","Malik","Mamdouh","Mamduh","Ma'mun","Ma'n","Ma'in","Mandhur","Mansur","Marghub","Marid","Ma'ruf","Marwan","Marzuq","Mash'al","Mashhur","Masrur","Mas'ud","Masun","Maysarah","Mazhar","Mazin","Mihran","Mihyar","Mika'il","Miqdad","Misbah","Mishaal","Mish'al","Miyaz","Mu'adh","Mu'awiyah","Mu'ayyad","Mubarak","Mubin","Mudar","Muddaththir","Mufid","Mufeed","Muflih","Muhab","Muhair","Muhayr","Muhammad","Mohammed","Muhanna","Muhannad","Muhanned","Muhib","Muhibb","Muhsin","Muhtadi","Muhyi al Din","Mu'in","Mu'izz","Mujab","Mujahid","Mukarram","Mukhlis","Mukhtar","Mulham","Mulhim","Mu'mmar","Mu'min","Mumtaz","Munahid","Mundhir","Munib","Munif","Munir","Muneer","Mu'nis","Munjid","Munsif","Muntasir","Murad","Murshid","Murtada","Murtadi","Murtadhy","Musa","Moosa","Mus'ab","Mus'ad","Musa'id","Mushtaq","Muslih","Muslim","Mustafa","Muta'","Mu'tasim","Mutawalli","Mu'tazz","Muthanna","Muti","Muwaffaq","Muyassar","Muzaffar","Muzzammil","Nabhan","Nabih","Nabighah","Nabih","Nabil","Nabeel","Nadhir","Nadim","Nadeem","Nadir","Nafi'","Nahid","Na'il","Na'im","Naji","Najib","Najeeb","Najid","Najjar","Najm al Din","Na'man","Namir","Nash'ah","Nash'at","Nashwan","Nasib","Nasih","Nasim","Nasir","Nasir al Din","Nasr","Nasser","Nasri","Nasuh","Nawaf","Nawwaf","Nawfal","Nayif","Naif","Nazih","Nazeeh","Nazim","Nazeem","Nazmi","Nibras","Nidal","Nijad","Nimr","Nizar","Nu'aim","Nu'aym","Nuh","Nooh","Nuhaid","Nuhayd","Numair","Nu'man","Nur al Din","Nuri","Noori","Nusrah","Nusrat","Qasim","Qays","Qais","Qudamah","Qusay","Qatadah","Qutaybah","Qutaibah","Qutb","Qutuz","Rabah","Rabi","Radi","Rafi","Rafid","Rafiq","Raghib","Ragheb","Raghid","Rahman","Ra'id","Ra'if","Rais","Raja","Rajab","Raji","Rajih","Rakin","Ramadan","Rami","Ramih","Ramiz","Ramzi","Rani","Rashad","Rashid","Rasil","Rasin","Rasmi","Rasul","Ratib","Ra'uf","Rayhan","Rayyan","Razin","Reda","Rida","Ridha","Ridwan","Rihab","Riyad","Riyadh","Rizq","Ruhi","Rushd","Rushdi","Ruwaid","Ruwayd","Saad","Sa'adah","Sab","Sabih","Sabeeh","Sabir","Sabeer","Sabri","Sa'd","Sa'd al Din","Sadad","Sadid","Sadiq","Sa'dun","Sa'eed","Sa'id","Safi","Safiy","Safiy al Din","Safuh","Safwah","Safwat","Safwan","Sahib","Sahir","Sahl","Sa'ib","Saif","Sayf","Seif","Saif al Din","Sajid","Sajjad","Sakhr","Salah","Salah al Din","Salamah","Saleh","Salih","Salim","Saleem","Salman","Sami","Samih","Samir","Sameer","Samman","Saqr","Sariyah","Sati","Saud","Sayyid","Sha'ban","Shadi","Shadin","Shafi","Shafiq","Shafeeq","Shahid","Shahin","Shahir","Shakib","Shakir","Shams al Din","Shamal","Shamil","Shamim","Sharaf","Sharif","Shareef","Shawqi","Shihab","Shihab al Din","Shihad","Shu'aib","Shu'ayb","Shukri","Shumayl","Siddiq","Sinan","Siraj","Siraj al Din","Sofian","Subhi","Sufyan","Suhaib","Suhayb","Suhail","Suhayl","Suhaim","Suhaym","Sulaiman","Sulayman","Sultan","Sumrah","Suraqah","Su'ud","Suoud","Tahir","Tahsin","Taim Allah","Taym Allah","Taj","Taj al Din","Talal","Talib","Tamim","Tamir","Tamam","Tammam","Taqiy","Tarif","Tareef","Tariq","Taslim","Tawfiq","Tawhid","Taymullah","Taysir","Tayyib","Thabit","Thamer","Thamir","Thaqib","Thawab","Thawban","'Ubaidah","'Ubaydah","Ubaid","Ubayy","'Udail","'Udayl","'Uday","'Umar","Omar","Umarah","Umayr","Umair","Umayyah","'Urwah","Usaim","Usaym","Usama","Usamah","'Utbah","Uthal","Uthman","Waddah","Wadi","Wadid","Wafiq","Wafeeq","Wahab","Wahhab","Wahid","Wa'il","Wajdi","Wajid","Wajih","Wakil","Walid","Waleed","Walif","Waliy Allah","Waliy al Din","Waqar","Waqqas","Ward","Wasif","Wasil","Wasim","Waseem","Wazir","Yahya","Yaman","Ya'qub","Yasar","Yasser","Yasin","Yaseen","Yasir","Yazan","Yazid","Yazeed","Youssef","Yusef","Yusuf","Yunus","Yoonus","Yushua","Yusri","Yusuf","Zafar","Zafir","Zahid","Zahir","Zaid","Zayd","Zaim","Zain","Zayn","Zarif","Zakariyya","Zaki","Zaky","Zakwan","Ziad","Ziyad","Zubair","Zubayr","Zuhair","Zuhayr"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_MONGOL" :
							{
								"PRE" : ("Negan","Qoyor","Gurban","Dorben","Taban","Jurgaghan","Dologhon","Naiman","Yisun","Arban","Qorin","Juchin","Dochin","Tabin","Jaran","lan","Nayan","Yeran","agun","Minghan","Tumen","Bayan","Qadan","Qutugh","Qutlugh","Temur","Burilgi","Arigh","Boke","Berke","Tegus","Yeke","Batu","olui","Arslan","hecheg","Erdene","Mongke","Cheren","Bayar","Qorchi","Chinua","Unegen","Sube","Gal","ol","Maidar","Vachir","Nasan","Enq","Oyugun","Delger","Dash","Suren","an","acha","Koke","lagan","Bora","Shria","lagh","ulan","hagan","Qara","Altan","l","Mongo"),
								"MID" : (),
								"END" : ("dai","dei","tai","tei","jin","chin","tu","t","qan","lun","nai","gen","teni","tani","char","cher","i","gene ","ge","gge","chi","chu","q","qai","qa","qui")
							},
							"CIVILIZATION_OTTOMAN" :
							{
								"PRE" : ("Abdul","","Al","","Abdel","","'Abd al","Aban","Abbas","Abbud","Abbudin","'Adl","Ahad","Alim","Aliyy","Azim","Aziz","Badi","Ba'ith","Baqi","Bari","Barr","Basir","Basit","Fattah","Ghaffar","Ghafur","Ghani","Hadi","Hafiz","Hakam","Hakim","Halim","Hamid","Haqq","Hasib","Hayy","Jabbar","Jalil","Karim","Khabir","Khaliq","Latif","Malik","Majid","Matin","Mubdi'","Mughni","Muhaimin","Muhsi","Muhyi","Mu'id","Mu'izz","Mujib","Mu'min","Muqaddim","Muqtadir","Musawwir","Muta'al","Nafi'","Nasser","Nasir","Nur","Qadir","Qahhar","Qawi","Qayyum","Quddus","Rafi'","Rahim","Rahman","Rashid","Ra'uf","Razzaq","Sabur","Salam","Samad","Sami","Sattar","Shahid","Shakur","Tawwab","Wadud","Wahhab","Wahid","Wajid","Wakil","Wali","Waliy","Warith","Zahir","Abdullah","'Abid","'Abidin","Abu Bakr","Abu al Khayr","Adan","Adel","'Adil","Adham","Adib","'Adli","Adnan","'Adnan","'Afif","Afeef","Ahmad","Ahmed","'Ajib","'Akif","Akil","Akram","Ala'","Ala' al Din","Al 'Abbas","Aladdin","Ala' al din","Al Bara'","Al Hakam","Al Harith","Alhasan","Alhusain","Alhusayn","Ali","'Ali","'Aliyy","Alim","Almahdi","Al Safi","Altaf","Altair","Al Tayyib","Al Tijani","Al Tufail","Al Tufayl","Amid","'Amid","Amin","Ameen","Amir","Ameer","'Amir","Amjad","Ammar","'Ammar","'Amro","Anas","Anis","'Antarah","Anwar","'Aqil","Arfan","Arif","'Arif","Asad","As'ad","Asadel","Ashraf","Asif","Asim","'Asim","Aswad","Ata'","'Ataa","Ata' Allah","Ata' al Rahman","Athil","Athir","Atif","'Atif","Awad","'Awad","'Awf","Aws","Awwab","Ayham","Ayman","Ayser","Ayyub","Ayoob","Aza","'Azab","Azhar","Azeem","Azim","Aziz","'Aziz","Azzam","'Azzam","Badi","Badi al Zaman","Badr","Badr al Din","Badri","Baha","Baha'","Baha al Din","Bahiyy al Din","Bahij","Bahir","Bakr","Bakri","Baligh","Bandar","Barakah","Barir","Bashir","Bashshar","Basil","Basim","Bassam","Bayhas","Bilal","Bishr","Boulos","Budail","Budayl","Burhan","Bushr","Butrus","Dabir","Dani","Darwish","Da'ud","Dawud","Dhakir","Dhakiy","Dhakwan","Dhul Fiqar","Dirar","Diya","Diya al Din","Duqaq","Fadi","Fadil","Fadl","Fadl Allah","Fahd","Fahad","Fahmi","Faisal","Faysal","Fa'iz","Fakhir","Fakhr al Din","Fakhri","Fakhry","Fakih","Falah","Falih","Faraj","Farraj","Farhan","Farid","Fareed","Fariq","Fareeq","Faris","Faruq","Farooq","Fath","Fathi","Fatih","Fatin","Fateen","Fawwaz","Fawzan","Fawzi","Fayyad","Ferran","Fida","Fikri","Firas","Fouad","Fu'ad","Fudail","Gamal","Gamali","Ghaith","Ghayth","Ghali","Ghalib","Ghanim","Ghassan","Ghawth","Ghazi","Ghazwan","Ghiyath","Habbab","Habib","Hadad","Haddad","Hadi","Hafiz","Hakem","Hakim","Hakeem","Halim","Hamal","Hamas","Hamdan","Hamdi","Hamid","Hamim","Hamzah","Hana","Hana'i","Hanbal","Hani","Hanif","Hannad","Haris","Harith","Haroun","Harun","Hashim","Hassan","Hatim","Haydar","Haytham","Hayyan","Hazim","Hilal","Hilel","Hilmi","Hisham","Hud","Houd","Hudad","Hudhafah","Hudhaifah","Hudhayfah","Humam","Husain","Husayn","Hussein","Husam","Husam al Din","Ibrahim","'Id","Idris","Ihsan","Ihtisham","'Ikrimah","Ilias","Imad","'Imad","Imad al Din","Imam","Imran","'Imran","Imtiyaz","In'am","Iqbal","Irfan","'Irfan","Isa","'Isa","Eisa","Isam","'Isam","Issam","Ishaq","Isma'il","Iyad","Iyas","Izz al Din","Jabalah","Jabbar","Jabr","Jabir","Jad Allah","Jafar","Ja'far","Jal","Jalal","Jalal al Din","Jalil","Jaleel","Jamal","Jamal al Din","Jamil","Jameel","Jarir","Jasim","Jaul","Jaun","Jawad","Jawdah","Jawhar","Jibran","Jibril","Jihad","Jubair","Jubayr","Jul","Jumah","Jumu'ah","Junaid","Junayd","Juwain","Juwayn","Kadar","Kedar","Kadeen","Kadin","Kadeer","Kadir","Kahil","Kaliq","Kamal","Kamil","Kameel","Karam","Kardal","Karif","Kareef","Karim","Kareem","Kasib","Kaseeb","Kaseem","Kasim","Kateb","Katib","Kazim","Khalaf","Khaldun","Khaldoon","Khalid","Khaled","Khalifah","Khalil","Khaleel","Kalil","Khalil al Allah","Khalis","Khatib","Khair al Din","Khairi","Khairy","Khayri","Khoury","Khulus","Khuzaimah","Khuzaymah","Kutaiba","Labib","Labeeb","Lablab","Latif","Layth","Lu'ay","Lubaid","Lubayd","Luqman","Lut","Lutfi","Ma'd","Madani","Mahbub","Mahdi","Mahfuz","Mahir","Mahjub","Mahmud","Mahmoud","Mahrus","Maimun","Maymun","Majd","Majdy","Majd al Din","Majid","Makin","Malik","Mamdouh","Mamduh","Ma'mun","Ma'n","Ma'in","Mandhur","Mansur","Marghub","Marid","Ma'ruf","Marwan","Marzuq","Mash'al","Mashhur","Masrur","Mas'ud","Masun","Maysarah","Mazhar","Mazin","Mihran","Mihyar","Mika'il","Miqdad","Misbah","Mishaal","Mish'al","Miyaz","Mu'adh","Mu'awiyah","Mu'ayyad","Mubarak","Mubin","Mudar","Muddaththir","Mufid","Mufeed","Muflih","Muhab","Muhair","Muhayr","Muhammad","Mohammed","Muhanna","Muhannad","Muhanned","Muhib","Muhibb","Muhsin","Muhtadi","Muhyi al Din","Mu'in","Mu'izz","Mujab","Mujahid","Mukarram","Mukhlis","Mukhtar","Mulham","Mulhim","Mu'mmar","Mu'min","Mumtaz","Munahid","Mundhir","Munib","Munif","Munir","Muneer","Mu'nis","Munjid","Munsif","Muntasir","Murad","Murshid","Murtada","Murtadi","Murtadhy","Musa","Moosa","Mus'ab","Mus'ad","Musa'id","Mushtaq","Muslih","Muslim","Mustafa","Muta'","Mu'tasim","Mutawalli","Mu'tazz","Muthanna","Muti","Muwaffaq","Muyassar","Muzaffar","Muzzammil","Nabhan","Nabih","Nabighah","Nabih","Nabil","Nabeel","Nadhir","Nadim","Nadeem","Nadir","Nafi'","Nahid","Na'il","Na'im","Naji","Najib","Najeeb","Najid","Najjar","Najm al Din","Na'man","Namir","Nash'ah","Nash'at","Nashwan","Nasib","Nasih","Nasim","Nasir","Nasir al Din","Nasr","Nasser","Nasri","Nasuh","Nawaf","Nawwaf","Nawfal","Nayif","Naif","Nazih","Nazeeh","Nazim","Nazeem","Nazmi","Nibras","Nidal","Nijad","Nimr","Nizar","Nu'aim","Nu'aym","Nuh","Nooh","Nuhaid","Nuhayd","Numair","Nu'man","Nur al Din","Nuri","Noori","Nusrah","Nusrat","Qasim","Qays","Qais","Qudamah","Qusay","Qatadah","Qutaybah","Qutaibah","Qutb","Qutuz","Rabah","Rabi","Radi","Rafi","Rafid","Rafiq","Raghib","Ragheb","Raghid","Rahman","Ra'id","Ra'if","Rais","Raja","Rajab","Raji","Rajih","Rakin","Ramadan","Rami","Ramih","Ramiz","Ramzi","Rani","Rashad","Rashid","Rasil","Rasin","Rasmi","Rasul","Ratib","Ra'uf","Rayhan","Rayyan","Razin","Reda","Rida","Ridha","Ridwan","Rihab","Riyad","Riyadh","Rizq","Ruhi","Rushd","Rushdi","Ruwaid","Ruwayd","Saad","Sa'adah","Sab","Sabih","Sabeeh","Sabir","Sabeer","Sabri","Sa'd","Sa'd al Din","Sadad","Sadid","Sadiq","Sa'dun","Sa'eed","Sa'id","Safi","Safiy","Safiy al Din","Safuh","Safwah","Safwat","Safwan","Sahib","Sahir","Sahl","Sa'ib","Saif","Sayf","Seif","Saif al Din","Sajid","Sajjad","Sakhr","Salah","Salah al Din","Salamah","Saleh","Salih","Salim","Saleem","Salman","Sami","Samih","Samir","Sameer","Samman","Saqr","Sariyah","Sati","Saud","Sayyid","Sha'ban","Shadi","Shadin","Shafi","Shafiq","Shafeeq","Shahid","Shahin","Shahir","Shakib","Shakir","Shams al Din","Shamal","Shamil","Shamim","Sharaf","Sharif","Shareef","Shawqi","Shihab","Shihab al Din","Shihad","Shu'aib","Shu'ayb","Shukri","Shumayl","Siddiq","Sinan","Siraj","Siraj al Din","Sofian","Subhi","Sufyan","Suhaib","Suhayb","Suhail","Suhayl","Suhaim","Suhaym","Sulaiman","Sulayman","Sultan","Sumrah","Suraqah","Su'ud","Suoud","Tahir","Tahsin","Taim Allah","Taym Allah","Taj","Taj al Din","Talal","Talib","Tamim","Tamir","Tamam","Tammam","Taqiy","Tarif","Tareef","Tariq","Taslim","Tawfiq","Tawhid","Taymullah","Taysir","Tayyib","Thabit","Thamer","Thamir","Thaqib","Thawab","Thawban","'Ubaidah","'Ubaydah","Ubaid","Ubayy","'Udail","'Udayl","'Uday","'Umar","Omar","Umarah","Umayr","Umair","Umayyah","'Urwah","Usaim","Usaym","Usama","Usamah","'Utbah","Uthal","Uthman","Waddah","Wadi","Wadid","Wafiq","Wafeeq","Wahab","Wahhab","Wahid","Wa'il","Wajdi","Wajid","Wajih","Wakil","Walid","Waleed","Walif","Waliy Allah","Waliy al Din","Waqar","Waqqas","Ward","Wasif","Wasil","Wasim","Waseem","Wazir","Yahya","Yaman","Ya'qub","Yasar","Yasser","Yasin","Yaseen","Yasir","Yazan","Yazid","Yazeed","Youssef","Yusef","Yusuf","Yunus","Yoonus","Yushua","Yusri","Yusuf","Zafar","Zafir","Zahid","Zahir","Zaid","Zayd","Zaim","Zain","Zayn","Zarif","Zakariyya","Zaki","Zaky","Zakwan","Ziad","Ziyad","Zubair","Zubayr","Zuhair","Zuhayr"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_PERSIA" :
							{
								"PRE" : ("Abdul","","Al","","Abdel","","'Abd al","Aban","Abbas","Abbud","Abbudin","'Adl","Ahad","Alim","Aliyy","Azim","Aziz","Badi","Ba'ith","Baqi","Bari","Barr","Basir","Basit","Fattah","Ghaffar","Ghafur","Ghani","Hadi","Hafiz","Hakam","Hakim","Halim","Hamid","Haqq","Hasib","Hayy","Jabbar","Jalil","Karim","Khabir","Khaliq","Latif","Malik","Majid","Matin","Mubdi'","Mughni","Muhaimin","Muhsi","Muhyi","Mu'id","Mu'izz","Mujib","Mu'min","Muqaddim","Muqtadir","Musawwir","Muta'al","Nafi'","Nasser","Nasir","Nur","Qadir","Qahhar","Qawi","Qayyum","Quddus","Rafi'","Rahim","Rahman","Rashid","Ra'uf","Razzaq","Sabur","Salam","Samad","Sami","Sattar","Shahid","Shakur","Tawwab","Wadud","Wahhab","Wahid","Wajid","Wakil","Wali","Waliy","Warith","Zahir","Abdullah","'Abid","'Abidin","Abu Bakr","Abu al Khayr","Adan","Adel","'Adil","Adham","Adib","'Adli","Adnan","'Adnan","'Afif","Afeef","Ahmad","Ahmed","'Ajib","'Akif","Akil","Akram","Ala'","Ala' al Din","Al 'Abbas","Aladdin","Ala' al din","Al Bara'","Al Hakam","Al Harith","Alhasan","Alhusain","Alhusayn","Ali","'Ali","'Aliyy","Alim","Almahdi","Al Safi","Altaf","Altair","Al Tayyib","Al Tijani","Al Tufail","Al Tufayl","Amid","'Amid","Amin","Ameen","Amir","Ameer","'Amir","Amjad","Ammar","'Ammar","'Amro","Anas","Anis","'Antarah","Anwar","'Aqil","Arfan","Arif","'Arif","Asad","As'ad","Asadel","Ashraf","Asif","Asim","'Asim","Aswad","Ata'","'Ataa","Ata' Allah","Ata' al Rahman","Athil","Athir","Atif","'Atif","Awad","'Awad","'Awf","Aws","Awwab","Ayham","Ayman","Ayser","Ayyub","Ayoob","Aza","'Azab","Azhar","Azeem","Azim","Aziz","'Aziz","Azzam","'Azzam","Badi","Badi al Zaman","Badr","Badr al Din","Badri","Baha","Baha'","Baha al Din","Bahiyy al Din","Bahij","Bahir","Bakr","Bakri","Baligh","Bandar","Barakah","Barir","Bashir","Bashshar","Basil","Basim","Bassam","Bayhas","Bilal","Bishr","Boulos","Budail","Budayl","Burhan","Bushr","Butrus","Dabir","Dani","Darwish","Da'ud","Dawud","Dhakir","Dhakiy","Dhakwan","Dhul Fiqar","Dirar","Diya","Diya al Din","Duqaq","Fadi","Fadil","Fadl","Fadl Allah","Fahd","Fahad","Fahmi","Faisal","Faysal","Fa'iz","Fakhir","Fakhr al Din","Fakhri","Fakhry","Fakih","Falah","Falih","Faraj","Farraj","Farhan","Farid","Fareed","Fariq","Fareeq","Faris","Faruq","Farooq","Fath","Fathi","Fatih","Fatin","Fateen","Fawwaz","Fawzan","Fawzi","Fayyad","Ferran","Fida","Fikri","Firas","Fouad","Fu'ad","Fudail","Gamal","Gamali","Ghaith","Ghayth","Ghali","Ghalib","Ghanim","Ghassan","Ghawth","Ghazi","Ghazwan","Ghiyath","Habbab","Habib","Hadad","Haddad","Hadi","Hafiz","Hakem","Hakim","Hakeem","Halim","Hamal","Hamas","Hamdan","Hamdi","Hamid","Hamim","Hamzah","Hana","Hana'i","Hanbal","Hani","Hanif","Hannad","Haris","Harith","Haroun","Harun","Hashim","Hassan","Hatim","Haydar","Haytham","Hayyan","Hazim","Hilal","Hilel","Hilmi","Hisham","Hud","Houd","Hudad","Hudhafah","Hudhaifah","Hudhayfah","Humam","Husain","Husayn","Hussein","Husam","Husam al Din","Ibrahim","'Id","Idris","Ihsan","Ihtisham","'Ikrimah","Ilias","Imad","'Imad","Imad al Din","Imam","Imran","'Imran","Imtiyaz","In'am","Iqbal","Irfan","'Irfan","Isa","'Isa","Eisa","Isam","'Isam","Issam","Ishaq","Isma'il","Iyad","Iyas","Izz al Din","Jabalah","Jabbar","Jabr","Jabir","Jad Allah","Jafar","Ja'far","Jal","Jalal","Jalal al Din","Jalil","Jaleel","Jamal","Jamal al Din","Jamil","Jameel","Jarir","Jasim","Jaul","Jaun","Jawad","Jawdah","Jawhar","Jibran","Jibril","Jihad","Jubair","Jubayr","Jul","Jumah","Jumu'ah","Junaid","Junayd","Juwain","Juwayn","Kadar","Kedar","Kadeen","Kadin","Kadeer","Kadir","Kahil","Kaliq","Kamal","Kamil","Kameel","Karam","Kardal","Karif","Kareef","Karim","Kareem","Kasib","Kaseeb","Kaseem","Kasim","Kateb","Katib","Kazim","Khalaf","Khaldun","Khaldoon","Khalid","Khaled","Khalifah","Khalil","Khaleel","Kalil","Khalil al Allah","Khalis","Khatib","Khair al Din","Khairi","Khairy","Khayri","Khoury","Khulus","Khuzaimah","Khuzaymah","Kutaiba","Labib","Labeeb","Lablab","Latif","Layth","Lu'ay","Lubaid","Lubayd","Luqman","Lut","Lutfi","Ma'd","Madani","Mahbub","Mahdi","Mahfuz","Mahir","Mahjub","Mahmud","Mahmoud","Mahrus","Maimun","Maymun","Majd","Majdy","Majd al Din","Majid","Makin","Malik","Mamdouh","Mamduh","Ma'mun","Ma'n","Ma'in","Mandhur","Mansur","Marghub","Marid","Ma'ruf","Marwan","Marzuq","Mash'al","Mashhur","Masrur","Mas'ud","Masun","Maysarah","Mazhar","Mazin","Mihran","Mihyar","Mika'il","Miqdad","Misbah","Mishaal","Mish'al","Miyaz","Mu'adh","Mu'awiyah","Mu'ayyad","Mubarak","Mubin","Mudar","Muddaththir","Mufid","Mufeed","Muflih","Muhab","Muhair","Muhayr","Muhammad","Mohammed","Muhanna","Muhannad","Muhanned","Muhib","Muhibb","Muhsin","Muhtadi","Muhyi al Din","Mu'in","Mu'izz","Mujab","Mujahid","Mukarram","Mukhlis","Mukhtar","Mulham","Mulhim","Mu'mmar","Mu'min","Mumtaz","Munahid","Mundhir","Munib","Munif","Munir","Muneer","Mu'nis","Munjid","Munsif","Muntasir","Murad","Murshid","Murtada","Murtadi","Murtadhy","Musa","Moosa","Mus'ab","Mus'ad","Musa'id","Mushtaq","Muslih","Muslim","Mustafa","Muta'","Mu'tasim","Mutawalli","Mu'tazz","Muthanna","Muti","Muwaffaq","Muyassar","Muzaffar","Muzzammil","Nabhan","Nabih","Nabighah","Nabih","Nabil","Nabeel","Nadhir","Nadim","Nadeem","Nadir","Nafi'","Nahid","Na'il","Na'im","Naji","Najib","Najeeb","Najid","Najjar","Najm al Din","Na'man","Namir","Nash'ah","Nash'at","Nashwan","Nasib","Nasih","Nasim","Nasir","Nasir al Din","Nasr","Nasser","Nasri","Nasuh","Nawaf","Nawwaf","Nawfal","Nayif","Naif","Nazih","Nazeeh","Nazim","Nazeem","Nazmi","Nibras","Nidal","Nijad","Nimr","Nizar","Nu'aim","Nu'aym","Nuh","Nooh","Nuhaid","Nuhayd","Numair","Nu'man","Nur al Din","Nuri","Noori","Nusrah","Nusrat","Qasim","Qays","Qais","Qudamah","Qusay","Qatadah","Qutaybah","Qutaibah","Qutb","Qutuz","Rabah","Rabi","Radi","Rafi","Rafid","Rafiq","Raghib","Ragheb","Raghid","Rahman","Ra'id","Ra'if","Rais","Raja","Rajab","Raji","Rajih","Rakin","Ramadan","Rami","Ramih","Ramiz","Ramzi","Rani","Rashad","Rashid","Rasil","Rasin","Rasmi","Rasul","Ratib","Ra'uf","Rayhan","Rayyan","Razin","Reda","Rida","Ridha","Ridwan","Rihab","Riyad","Riyadh","Rizq","Ruhi","Rushd","Rushdi","Ruwaid","Ruwayd","Saad","Sa'adah","Sab","Sabih","Sabeeh","Sabir","Sabeer","Sabri","Sa'd","Sa'd al Din","Sadad","Sadid","Sadiq","Sa'dun","Sa'eed","Sa'id","Safi","Safiy","Safiy al Din","Safuh","Safwah","Safwat","Safwan","Sahib","Sahir","Sahl","Sa'ib","Saif","Sayf","Seif","Saif al Din","Sajid","Sajjad","Sakhr","Salah","Salah al Din","Salamah","Saleh","Salih","Salim","Saleem","Salman","Sami","Samih","Samir","Sameer","Samman","Saqr","Sariyah","Sati","Saud","Sayyid","Sha'ban","Shadi","Shadin","Shafi","Shafiq","Shafeeq","Shahid","Shahin","Shahir","Shakib","Shakir","Shams al Din","Shamal","Shamil","Shamim","Sharaf","Sharif","Shareef","Shawqi","Shihab","Shihab al Din","Shihad","Shu'aib","Shu'ayb","Shukri","Shumayl","Siddiq","Sinan","Siraj","Siraj al Din","Sofian","Subhi","Sufyan","Suhaib","Suhayb","Suhail","Suhayl","Suhaim","Suhaym","Sulaiman","Sulayman","Sultan","Sumrah","Suraqah","Su'ud","Suoud","Tahir","Tahsin","Taim Allah","Taym Allah","Taj","Taj al Din","Talal","Talib","Tamim","Tamir","Tamam","Tammam","Taqiy","Tarif","Tareef","Tariq","Taslim","Tawfiq","Tawhid","Taymullah","Taysir","Tayyib","Thabit","Thamer","Thamir","Thaqib","Thawab","Thawban","'Ubaidah","'Ubaydah","Ubaid","Ubayy","'Udail","'Udayl","'Uday","'Umar","Omar","Umarah","Umayr","Umair","Umayyah","'Urwah","Usaim","Usaym","Usama","Usamah","'Utbah","Uthal","Uthman","Waddah","Wadi","Wadid","Wafiq","Wafeeq","Wahab","Wahhab","Wahid","Wa'il","Wajdi","Wajid","Wajih","Wakil","Walid","Waleed","Walif","Waliy Allah","Waliy al Din","Waqar","Waqqas","Ward","Wasif","Wasil","Wasim","Waseem","Wazir","Yahya","Yaman","Ya'qub","Yasar","Yasser","Yasin","Yaseen","Yasir","Yazan","Yazid","Yazeed","Youssef","Yusef","Yusuf","Yunus","Yoonus","Yushua","Yusri","Yusuf","Zafar","Zafir","Zahid","Zahir","Zaid","Zayd","Zaim","Zain","Zayn","Zarif","Zakariyya","Zaki","Zaky","Zakwan","Ziad","Ziyad","Zubair","Zubayr","Zuhair","Zuhayr"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_PORTUGAL" : {
								"PRE" : (u"Aarão", u"Abel", u"Abelardo", u"Abraão", u"Adalberto", u"Adão", u"Adelino", u"Ademar", u"Adilmar", u"Adolfo", u"Adriano", u"Afonso", u"Agostinho", u"Aguinaldo", u"Alarico", u"Alberto", u"Aldo", u"Aleixandre", u"Aleixo", u"Alexandre", u"Alfonso", u"Alfredo", u"Alírio", u"Aloísio", u"Álvaro", u"Amadeu", u"Américo", u"Amílcar", u"André", u"Ângelo", u"Aníbal", u"Antão", u"Antero", u"António", u"Antônio", u"Armando", u"Arnaldo", u"Artur", u"Augusto", u"Aurélio", u"Balduíno", u"Baltasar", u"Baltazar", u"Barnabé", u"Bartolomeu", u"Belarmino", u"Belmiro", u"Benedito", u"Bento", u"Bernardo", u"Bernardim", u"Bernardino", u"Boaventura", u"Bráulio", u"Breno", u"Brites", u"Bruno", u"Caetano", u"Caim", u"Caio", u"Calisto", u"Camilo", u"Cândido", u"Carlos", u"Casimiro", u"Cássio", u"Cecilio", u"César", u"Cláudio", u"Clemente", u"Conrado", u"Constantino", u"Cristiano", u"Cristóvão", u"Damião", u"Daniel", u"Danilo", u"David", u"Davi", u"Diego", u"Diogo", u"Dionísio", u"Dinis", u"Dirce", u"Dirceu", u"Domingos", u"Donato", u"Duarte", u"Edelberto", u"Edgar", u"Edmundo", u"Eduardo", u"Elias", u"Eliseu", u"Emanuel", u"Emílio", u"Epaminondas", u"Érico", u"Ernesto", u"Estanislau", u"Estêvão", u"Eugénio", u"Eugênio", u"Eurico", u"Eusébio", u"Evandro", u"Evaristo", u"Everaldo", u"Ezequiel", u"Fabiano", u"Fábio", u"Fabrício", u"Faustino", u"Fausto", u"Feliciano", u"Felício", u"Felipe", u"Félix", u"Fernando", u"Fernão", u"Filipe", u"Firmino", u"Flávio", u"Flor", u"Florêncio", u"Floriano", u"Florípes", u"Fradique", u"Francisco", u"Frederico", u"Gabriel", u"Gaspar", u"Gastão", u"Gaudêncio", u"George", u"Georgio", u"Geraldo", u"Gerard", u"Germano", u"GianFrancesco", u"GianLuca", u"Gil", u"Gilberto", u"Giorgio", u"Gonçalo", u"Graciano", u"Graciliano", u"Gregório", u"Guido", u"Guilherme", u"Guiomar", u"Gustavo", u"Heitor", u"Hélio", u"Hélder", u"Henrique", u"Herculano", u"Hermínio", u"Hermenegildo", u"Higino", u"Hilário", u"Hipólito", u"Honório", u"Horácio", u"Hugo", u"Humberto", u"Inácio", u"Ivo", u"Jacinto", u"Jaime", u"Jean", u"Jeremias", u"João", u"Joaquim", u"Joel", u"Jonas", u"Jorge", u"José", u"Júlio", u"Juliano", u"Justino", u"Juvenal", u"Lauro", u"Laurus", u"Lázaro", u"Leandro", u"Leonardo", u"Leonel", u"Leopoldo", u"Lineu", u"Lino", u"Lourenço", u"Lucas", u"Lúcio", u"Luciano", u"Ludovico", u"Luís", u"Luiz", u"Manuel", u"Manoel", u"Marco", u"Marcos", u"Marcelino", u"Marcelo", u"Mário", u"Martim", u"Martinho", u"Mateus", u"Matheus", u"Matias", u"Maurício", u"Maurílio", u"Mauro", u"Máximo", u"Maximiliano", u"Mécia", u"Mendo", u"Miguel", u"Murilo", u"Narciso", u"Natalino", u"Nelson", u"Nestor", u"Nicolau", u"Norberto", u"Nuno", u"Octávio", u"Otávio", u"Odílio", u"Olavo", u"Olegário", u"Olímpio", u"Olívio", u"Onofre", u"Orestes", u"Orlando", u"Óscar", u"Oscar", u"Osório", u"Otelo", u"Ovídio", u"Palmiro", u"Pascoal", u"Patrício", u"Paulino", u"Paulo", u"Pedro", u"Petronio", u"Plácido", u"Plínio", u"Políbio", u"Prazeres", u"Prímio", u"Querubim", u"Quintiliano", u"Quirino", u"Quitério", u"Rafael", u"Ramiro", u"Raimundo", u"Raul", u"Reginaldo", u"Reinaldo", u"Renato", u"Ricardo", u"Rivelino", u"Roberto", u"Rodolfo", u"Rodrigo", u"Rogério", u"Romão", u"Romeu", u"Rómulo", u"Rômulo", u"Ronaldo", u"Roque", u"Rúben", u"Rúbem", u"Rui", u"Salomão", u"Salvador", u"Samuel", u"Sancho", u"Sandoval", u"Sandro", u"Sebastião", u"Serafim", u"Sérgio", u"Severino", u"Silvano", u"Silvério", u"Sílvio", u"Silvino", u"Simão", u"Simeão", u"Solano", u"Tadeu", u"Telmo", u"Teobaldo", u"Teodoro", u"Tiago", u"Thiago", u"", u"Timóteo", u"Tobias", u"Tomás", u"Thomaz", u"Trajano", u"Ubaldo", u"Ulisses", u"Umbelino", u"Urbano", u"Valentim", u"Valério", u"Vasco", u"Venâncio", u"Ventura", u"Vicente", u"Victor", u"Vinicius", u"Violante", u"Virgílio", u"Viriato", u"Vítor", u"Xavier", u"Xisto", u"Zacarias", u"Female", u"Adelaide", u"Adélia", u"Adelina", u"Adriana", u"Ágata", u"Alberta", u"Alda", u"Aldina", u"Alexandra", u"Alice", u"Alzira", u"Amália", u"Amanda", u"Amélia", u"Ana", u"Andreia", u"Andréia", "Ângela", u"Angélica", u"Angelina", u"Anita", u"Antónia", u"Antônia", "", "Ava", u"Augusta", u"Augustina", u"Aurélia", u"Aurora", u"Bárbara", u"Beatriz", u"Belarmina", u"Belém", u"Benedita", u"Berengária", u"Bernardete", "Bernarda", u"Bernardina", u"Branca", u"Brígida", u"Brízida", u"Bruna", u"Caetana", u"Camila", u"Cândida", u"Capitolina", u"Carina", u"Carla", u"Carlota", u"Carmen", u"Carmem", "Carolina", u"Catarina", u"Cássia", u"Cátia", u"Cecília", u"Celeste", u"Célia", u"Celina", u"Cesária", u"Cidália", u"Clara", u"Cláudia", "Clementina", u"Clotilde", u"Conceição", u"Constança", u"Constantina", u"Corina", u"Cristiana", u"Cristina", u"Custódia", u"Daniela", u"Débora", u"Denilde", u"Denise", u"Diana", "Dina", u"Diná", u"Donata", u"Doroteia", u"Dorotéia", "Edite", u"Edna", u"Eduarda", u"Elia", u"Elisa", u"Elisabete", u"Elizabete", u"Elsa", u"Elvira", u"Elza", "Ema", u"Emerenciana", u"Emília", u"Epifânia", u"Érica", u"Ermelinda", u"Esmeralda", u"Estefânia", u"Estela", u"Estrela", u"Eugénia", u"Eugênia", "Eulália", u"Eunice", u"Eva", u"Fábia", u"Fabiana", u"Fátima", u"Fausta", u"Faustina", u"Felícia", u"Feliciana", u"Felismina", u"Fernanda", u"Fernandina", u"Filipa", "Filomena", u"Firmina", u"Flávia", u"Flora", u"Florbela", u"Florência", u"Florinda", u"Florípes", u"Francisca", u"Frederica", u"Gabriela", u"Genoveva", u"Georgette", u"Georgina", u"Geraldina", u"Germana", u"Gertrudes", "Gisela", u"Giselda", u"Gisele", u"Glória", u"Graça", u"Guilhermina", u"Helena", u"Hélia", u"Heloísa", "Henriqueta", u"Hermínia", u"Honorina", u"Inês", u"Inácia", u"Iolanda", u"Irene", u"Irina", u"Isabel", "Isaura", u"Isilda", u"Isulina", u"Iva", u"Ivete", u"Ivone", u"Jacinta", u"Janete", u"Joana", u"Joaquina", u"Jorgina", u"Josefa", u"Josefina", "Judite", u"Júlia", u"Juliana", u"Julieta", u"Justina", u"Juvina", u"Laila", u"Lara", u"Laura", u"Laurea", u"Laurel", u"Lauren", u"Laureana", u"Laurinda", u"Leandra", u"Leila", u"Leonor", u"Leonilde", u"Leopoldina", "Letícia", u"Lídia", u"Lígia", u"Lila", u"Lília", u"Lilian", u"Liliane", u"Lilih", u"Lívia", u"Liana", u"Liliana", u"Lina", u"Lourdes", "Lúcia", u"Luciana", u"Lucinda", u"Lucrécia", u"Ludovica", u"Ludovina", u"Luisa", u"Luiza", "Lurdes", u"Luzia", u"Luz", u"Madalena", u"Mafalda", u"Magali", u"Magda", u"Manuela", u"Manoela", "Márcia", u"Marcela", u"Marcelina", u"Margarida", "Maria", u"Maria Joãou", "Maria Joséu", "Mariana", u"Mariane", u"Marilda", u"Marília", u"Marina", u"Marisa", u"Marise", u"Marta", u"Maurícia", u"Máxima", u"Maximiliana", "Mercedes", u"Merciana", u"Micaela", u"Milene", u"Miquelina", u"Miriam", u"Mónica", u"Mônica", "Nádia", u"Natália", u"Natalina", "Natividade", u"Nicole", u"Octávia", u"Otávia", "Odete", u"Odília", "Olga", u"Olímpia", u"Olívia", u"Otília", u"Palmira", u"Pandora", u"Patrícia", u"Paula", u"Paulina", "Penélope", u"Piedade", u"Prantelhana", u"Priscila", u"Querubina", u"Quintiliana", "Quirina", u"Quitéria", u"Rafaela", u"Ramira", u"Raimunda", u"Raquel", u"Rebeca", u"Regina", u"Renata", u"Ricardina", u"Rita", "Roberta", u"Rosa", u"Rosália", u"Rosalina", u"Rosalinda", u"Rosana", u"Rosaura", u"Rute", u"Sabrina", u"Salomé", u"Sancha", "Sandra", u"Sara", u"Sebastiana", u"Selma", u"Serafina", u"Silvana", u"Silvéria", "Sílvia", u"Silvina", u"Simone", u"Sofia", u"Solange", u"Sónia", u"Sônia", "Susana", u"Tânia", u"Tatiana", u"Telma", u"Teodora", "Teresa", u"Thereza", "Tomásia", u"Umbelina", "Úrsula", u"Valentina", u"Valéria", u"Vanda", u"Vanésa", u"Vera", u"Verónica", u"Verônica", "", "Violeta", u"Virgília", u"Virgínia", u"Vitória", u"Viviana", u"Xénia", "Ximena", u"Zara", u"Zélia", u"Zelinda", u"Zilá", u"Zínia", u"Zita", "Zoraide", u"Zuleica", u"Zuleide", u"Zulina", u"Zulmira", u"Abreu", u"Agostinho", u"Águas", u"Aguiar", u"Albuquerque", u"Alcantara", u"Almeida", u"Álvares", u"Alves", u"Alves da Silva", u"Alvim", u"Amaral", u"Amorim", u"Andrade", u"Andrade", u"Antunes", u"Araújo", u"Assunção", u"Ávila", u"Azevedo", u"Bandeira", u"Baptista", u"Barbosa", u"Barreto", u"Barros", u"Batata", u"Batista", u"Belasco", u"Bento", u"Bento Gonçalves", u"Bettencourt", u"Borges", u"Botelho", u"Braga", u"Branco", u"Brandão", u"Brito", u"Cabral", u"Câmara", u"Campos", u"Cardoso", u"Carneiro", u"Carreira", u"Carvalho", u"de Castro", u"Castro", u"Cavaco", u"Coelho", u"Coimbra", u"Colón", u"Conceição", u"Cordeiro", u"Correia", u"Corte-Real", u"Cortes", u"Corvo", u"Costa", u"Coutinho", u"Couto", u"Cruz", u"Cunha", u"Dantas", u"del Rosario", u"Delgado", u"Dias", u"Espinoza", u"Faria", u"Fernandes", u"Ferreira", u"Fidalgo", u"Fonseca", u"Freitas", u"Furtado", u"Gama", u"Garnier", u"Gomes", u"Gonsalves", u"Gonçalves", u"Gouveia", u"Gusmão", u"Góes", u"Henriques", u"Hernandes", u"Leite", u"Lima", u"Lobo", u"Lopes", u"Luz", u"Macedo", u"Machado", u"Maciel", u"Magalhães", u"Martins", u"Mascarenhas", u"Mata", u"Matos", u"Medeiros", u"Melo", u"Mendes", u"Mendonça", u"Menezes", u"Miranda", u"Moniz", u"Morais", u"Moreira", u"Moreno", u"Nascimento", u"Neves", u"Nogueira", u"Nunes", u"Nunez", u"Oliveira", u"Pacheco", u"Paiva", u"Pascoal", u"Pereira", u"Pereira da Silva", u"Peres", u"Pinto", u"Pires", u"Queiroz", u"Rebelo", u"Rego", u"Reis", u"Resendes", u"Ribeiro", u"Rodrigues", u"Rosa", u"Sá", u"Saldanha", u"Santos", u"Seixas", u"Serra", u"Silva", u"Silveira", u"Silvestre", u"Siqueira", u"Soares", u"Sousa", u"Tavares", u"Teixeira", u"Torres", u"Varela", u"Vasconcelos", u"Vaz", u"Vieira", u"Vila"
),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_ROME" :
							{
								"PRE" : ("Ap","B","C","Cer","Cerb","D","Fl","J","Jup","M","Merc","Min","Nept","Pl","Pros","S","V","Ur"),
								"MID" : ("a","acchu","ai","arpi","e","ercu","i","ia","o","u"),
								"END" : ("a","lcan","llo","na","ne","no","nus","pid","ra","res","rs","rva","rus","ry","s","sta","ter","to","turn")
							},
							"CIVILIZATION_RUSSIA" :
							{
								"PRE" : ("Bez","Bliz","Blizh","Blizh","ole","Dab","Do","Doma","Is","z","k","o","oi","a","ad","e","b","n","nyi","Ot","ere","Pre","Pered","Pred","o","d","ri","ro","rotiv","Ras","Raz","Ros","oz","S","So","am","Seb","o","Svoi","e","ei","Sul","ve","Vse","vo","Te","To","i","Tret","retii","Tri","Troe","U","n","Veche","ke","Viache","Viashch","iatsh","Viashte","Vse","ve","Vys","Vysh","yshe","Za","a","Zdat","Zde","a","ai","Va","b","Ba","Bai","Va","Bab","Baba","Babo","Bach","Bad","Bag","Bak","Vak","Vakh","Vats","Bal","Val","Ban","Pan","Bar","Baran","Bas","Bach","Bash","Bat","Bad","Pat","Bato","Batia","Bazh","Bebr","Bobr","Beg","Bel","Bes","Bit","Bits ","Blag","Bleg","Blazh","Blaz","Blud","Plut","Bob","Bog","Bogat","Bazh","Bag","Bozh","Boi","Boich","Bok ","Bol","Bon","Borz","Borzh","Bot","Br","Bor","Vr","Vor","Pr","Por","Bra","Bra ","Brad","Borod","Brat","Bud","Bui","Buk","Bur","Byk","Vyk","Cha","Chab","Chaba","Chava","Chach","Chachti","Chad","Chada","Chado","Chak","Chakh","Chekh","Chan","Chana","Chap","Chep","Chas","Chast","Chast","Chastyi","Chel","Chelo","Chern","Chernyi","Chert","Chest","Chik","Chika","Chil","Chin","Pochin","Chir","Chiryi","Chud","Chudyi","Da","Dat","Dati","Debr","Ded","Dei","Demon","Den","Derevo","Derzha","Derzhat","Des","Desa","Det","Dev","Dik","Dika","Dim","Din","Div","Diva","Dob","Dobr","Dod","Doi","Dok","Dol","Dolg","Drevo","Derevo","Drug","Drugoi","Druk","Druzh","Dub","Debr","Dud","Duda","Dug","Dukh","Dusha","Dum","Dun","Dunai","Dusha","Dvor","Elets","Elka","El'","Iel","Ezer","Ezero","Ozer","Ozero","Ezh","Frang","Frank","Gai","Khai","Gal","Gast","Gavran","Gin","Glad","Glas","Glav","Glaz","Gleb","Gliad","Glukh","Glup","Gna","Gnev","God","Gogol","Goi","Gol","Golod","Golos","Golova","Golub","Gomz","Gomza","Gon","Gonostar","Gor","Gork","Gorb","Gord","Gorlits","Gorlitsa","Gornostai","Gornostal","Gorod","Gost","Govor","Grab","Grach","Grad","Grid","Grim","Grom","Groma","Gromada","Gromaza","Gron","Groz","Grub","Grud","Gub","Guba","Gud","Guda","Gugn","Gul","Guliat'","Gul","Gulk","Gun","Guna","Gunia","Gus","Guz","Gvozd","Gyn","Iabl","Iablon'","Iagel","Iagl","Iagla","Iagod","Iagoda","Iak","Iar","Iaryi","Iel","Im","Imat'","Imet'","In","Ino","Iskr","Iskra","Ist","Istok","Istom","Istoma","Iug","Iun","Iunyi","Iur","Iurii","Izbor","Izmaragd","Kab","Kaba","Kava","Kai","Kal","Kalin","Kalina","Kar","Kara","Kav","Kaz","Kaza","Khabr","Khai","Kher","Khera","Khero","Khlan","Khmel","Khod","Khon","Khorob","Khorvat","Khot","Khrab","Khrabryi","Khran","Khrano ","Khranit'","Khrap","Khrel","Khren","Khrob","Khrom","Khrs","Khrus","Khruv","Khrv","Khud","Khval","Ki","Klen","Klim","Klimati","Kni","Kniaz","Kniazh","Kobyl","Koi","Kokh","Kol","Komon","Kon","Konets","Kon'","Kos","Kosa","Koshut","Koshuta","Kostr","Kovyl","Koz","Koza ","Kozel","Kra","Krai","Pokrai","Krak","Kral","Kras","Krik","Kriv","Krok","Krun","Ku","Kui","Kun","Kuna","Kup","Kur","Kura","Kvas","Ky","Kyi","Lab","Leb","Lach","Lad","Lada","Lak","Lachat'","Lal","Lala","Lavr","Laz","Laza","Leb","Lek","Lel","Lelia","Lep","Lepyi","Lest","Lev","Likh","Likho","Lits","Litse","Liub","Liud","Liut","Lobod","Loboda","Lov","Lovit'","Loz","Loza","Lug","Luk","Lys","Makh","Makhat'","Mal","Malin","Malina","Man","Manit'","Mar","Margarit","Mat","Mater","Mati","Mavr","Mech","Med","Mekh","Men","Men'shii ","Men'shei","Mer","Mera","Mesh","Mest","Mg","Miag","Miagkii ","Miakkii","Miak","Mig","Migat'","Mil","Mir","Mlad","Mn","Mniu","Mol","Molit'","Mom","Mor","Moroz","Mrak","Mraz","Mu","Mukha","Mudr","Mut","Mutit'","Muzh","Mysl","Nach","Nacha","Nag","Nagoi","Naid","Nak","Naka","Nako","Nakh","Nan","Nana","Nena","Narozh","Narush","Nash","Necha","Nechai","Nega","Nem","Neman","Nen","Nerad","Nes","Net","Netk","Netka","Nin","Nos","Nov","Nud","Nutit","Nut","Ob","Oblez","Oblezh","Oblesh)","Obel","Obezd","Obi","Obid","Obil","Oblak","Oblaka","Obrad","Obran","Obrat","Odin","Odno","Odol","Ogn","Ole","Olei","Ol'kha","Ol'sha","Opor","Opr","Orash","Orel","Oresh","Osel","Osob","Osobei","Osto","Ostoi","Ostr","Ostryi","Ot","Ota","Otmar","Otnia","Otrok","Ov","Ozer","Ozor","Pab","Pabek","Pabesh","Paba","Pach","Pak","Paki","Pache","Pakh","Pakha","Pal","Palets","Pan","Par","Para","Pas","Pat","Paun","Pav","Pava","Pchel","Pchela","Pek","Peka","Pekh","Pen","Pena","Per","Peru","Perv","Pervoi","Pesh","Pit'","Pivot'","Piat","Piatyi","Pik","Pikura","Pisk","Piskar ","Pisker","Plav","Plen","Plut","Pochin","Podiv","Pokhval","Pokra","Pol","Pole","Poliud","Polk","Pomnen","Pop","Popel","Por","Postan","Pot","Potikh","Pozd","Pozdo","Pozdnyi","Poznan","Pozvizd","Pr","Prav","Prem","Priam","Priby","Prid","Priia","Priiat","Prisn","Prisnyi","Prod","Prodat'","Pros","Prosit'","Prost","Prud","Pruditi","Prug","Prus","Ptach","Ptak","Ptachek","Ptakh","Pul","Pur","Pura","Put","Rab","Rabek","Rach","Racha","Rad","Rai","Rakh","Rakit","Rakita","Ral","Ralen","Ran","Ranyi","Rapot","Rapota","Rast","Rasti","Rosti","Rat","Rats","Rav","Ravnyi","Razum","Reg","Res","Resa","Reza","Rez","Riab","Riag","Riaka","Rob","Rod","Rog","Rol","Rolek","Rolak","Ros","Rosa","Rost","Rozh","Rub","Rud","Ruk","Ruka","Rum","Rumianyi","Rus","Rut","Ruta","Ruzh","Sab","Saba","Soba","Sad","Sasin","Sby","Sbyt","Sobyt'","Sek","Seku","Sel","Selo","Sem","Semi","Semo","Ser","Serd","Serebr","Serp","Sestr","Sestra","Set","Setiti ","Setovat'","Shar","Shara","Shched","Shchedr","Shchedryi","Shchek","Shchen","Shchenia","ShchenShtenia","Shcherb","Shcherba","Shchit","Shchuk","Shchuka","She","Sheia","Shest","Shestyi","Shib","Shibat","Shim","Shima","Shir","Shirokii","Shish","Shishman","Shkop","Shlekht","Shlekhta","Shliakhta","Shliakh","Shtenia","Shub","Shuba","Shui","Shum","Shuma","Shup","Shupek","Sin","Sinii","Sir","Skar","Skopek","Skor","Slab","Slad","Slav","Slava","Slavii","Slug","Sluga","Smed","Smil","Smokv","Smokva","Smol","Smola","Sob","Sok","Sokol","Sol","Solov","Solovei","Sor","Sora","Span","Spas","Spit","Spet","Spor","Stan","Stoi","Star","Staryi","Stav","Sto","Stolb","Stolp","Strakh","Stran","Strana","Strat","Strata","Strazh","Stregu","Streg","Stro","Stroi","Stup","Subot","Subota","Sud","Sui","Suk","Sur","Sviat","Sviatyi","Svin","Svin'ia","Syn","Tal","Tam","Tan","Tas","Tat","Tato","Tata","Tatia","Tech","Tekh","Tel","Telg ","Telo","Tem","Ten","Tep","Tepati","Ter","Terp","Terpet'","Tet","Teta","Tiag","Tir","Tol","Tolit","Tom","Ton","Trav","Trava","Treb","Treba","Tsan","Tsana","Tsena","Tsap","Tsapa","Tsar","Tsel","Tsen","Tsvet","Tug","Tur","Tverd","Tverdyi","Tvor","Tvorit'","Ub","Ubit","Ubyt","Udr","Udriti","Ugl","Ugol","Ugr","Upyr","Ur","Us","Usia","Ut","Uta","Uda","Uzh","Va","Vab","Vad","Vak","Vakh","Val","Var","Vats","Vav","Vavr","Vech","Vecher","Ved","Vek","Vel","Ver","Vera","Vesel","Vesn","Vesna","Vet","Vid","Vil","Vila","Vit","Vlad","Vlakh","Vlk","Volia","Volk","Volod","Volok","Vor","Vorobei","Voron","Vorona","Vorot","Vr","Vrach","Vrat","Vyk","Zar","Zel","Zem","Zemlia","Zern","Zerno","Zhab","Zhaba","Zhad","Zhada","Zhal","Zhalo","Zhar","Zhark","Zhavoronok","Zheg","Zhel","Zhelat'","Zhelez","Zhelezo","Zhemchug","Zhen","Zherav","Zhereb","Zhgu","Zhiv","Zhup","Zhurav","Zl","Zlyi","Zlat","Zlato","Zoloto","Zme","Zmei","Zna","Znat'","Zolot","Zor","Zora","Zoria","Zret'","Zub","Zver","Zvezd","Zvezda","Zvon"),
								"MID" : (),
								"END" : ("Ba","Bai","Va","Bab","Baba","Babo","Bach","Bad","Bag","Bak","Vak","Vakh","Vats","Bal","Val","Ban","Pan","Bar","Baran","Bas","Bach","Bash","Bat","Bad","Pat","Bato","Batia","Bazh","Bebr","Bobr","Beg","Bel","Bes","Bit","Bits ","Blag","Bleg","Blazh","Blaz","Blud","Plut","Bob","Bog","Bogat","Bazh","Bag","Bozh","Boi","Boich","Bok ","Bol","Bon","Borz","Borzh","Bot","Br","Bor","Vr","Vor","Pr","Por","Bra","Bra ","Brad","Borod","Brat","Bud","Bui","Buk","Bur","Byk","Vyk","Cha","Chab","Chaba","Chava","Chach","Chachti","Chad","Chada","Chado","Chak","Chakh","Chekh","Chan","Chana","Chap","Chep","Chas","Chast","Chast","Chastyi","Chel","Chelo","Chern","Chernyi","Chert","Chest","Chik","Chika","Chil","Chin","Pochin","Chir","Chiryi","Chud","Chudyi","Da","Dat","Dati","Debr","Ded","Dei","Demon","Den","Derevo","Derzha","Derzhat","Des","Desa","Det","Dev","Dik","Dika","Dim","Din","Div","Diva","Dob","Dobr","Dod","Doi","Dok","Dol","Dolg","Drevo","Derevo","Drug","Drugoi","Druk","Druzh","Dub","Debr","Dud","Duda","Dug","Dukh","Dusha","Dum","Dun","Dunai","Dusha","Dvor","Elets","Elka","El'","Iel","Ezer","Ezero","Ozer","Ozero","Ezh","Frang","Frank","Gai","Khai","Gal","Gast","Gavran","Gin","Glad","Glas","Glav","Glaz","Gleb","Gliad","Glukh","Glup","Gna","Gnev","God","Gogol","Goi","Gol","Golod","Golos","Golova","Golub","Gomz","Gomza","Gon","Gonostar","Gor","Gork","Gorb","Gord","Gorlits","Gorlitsa","Gornostai","Gornostal","Gorod","Gost","Govor","Grab","Grach","Grad","Grid","Grim","Grom","Groma","Gromada","Gromaza","Gron","Groz","Grub","Grud","Gub","Guba","Gud","Guda","Gugn","Gul","Guliat'","Gul","Gulk","Gun","Guna","Gunia","Gus","Guz","Gvozd","Gyn","Iabl","Iablon'","Iagel","Iagl","Iagla","Iagod","Iagoda","Iak","Iar","Iaryi","Iel","Im","Imat'","Imet'","In","Ino","Iskr","Iskra","Ist","Istok","Istom","Istoma","Iug","Iun","Iunyi","Iur","Iurii","Izbor","Izmaragd","Kab","Kaba","Kava","Kai","Kal","Kalin","Kalina","Kar","Kara","Kav","Kaz","Kaza","Khabr","Khai","Kher","Khera","Khero","Khlan","Khmel","Khod","Khon","Khorob","Khorvat","Khot","Khrab","Khrabryi","Khran","Khrano ","Khranit'","Khrap","Khrel","Khren","Khrob","Khrom","Khrs","Khrus","Khruv","Khrv","Khud","Khval","Ki","Klen","Klim","Klimati","Kni","Kniaz","Kniazh","Kobyl","Koi","Kokh","Kol","Komon","Kon","Konets","Kon'","Kos","Kosa","Koshut","Koshuta","Kostr","Kovyl","Koz","Koza ","Kozel","Kra","Krai","Pokrai","Krak","Kral","Kras","Krik","Kriv","Krok","Krun","Ku","Kui","Kun","Kuna","Kup","Kur","Kura","Kvas","Ky","Kyi","Lab","Leb","Lach","Lad","Lada","Lak","Lachat'","Lal","Lala","Lavr","Laz","Laza","Leb","Lek","Lel","Lelia","Lep","Lepyi","Lest","Lev","Likh","Likho","Lits","Litse","Liub","Liud","Liut","Lobod","Loboda","Lov","Lovit'","Loz","Loza","Lug","Luk","Lys","Makh","Makhat'","Mal","Malin","Malina","Man","Manit'","Mar","Margarit","Mat","Mater","Mati","Mavr","Mech","Med","Mekh","Men","Men'shii ","Men'shei","Mer","Mera","Mesh","Mest","Mg","Miag","Miagkii ","Miakkii","Miak","Mig","Migat'","Mil","Mir","Mlad","Mn","Mniu","Mol","Molit'","Mom","Mor","Moroz","Mrak","Mraz","Mu","Mukha","Mudr","Mut","Mutit'","Muzh","Mysl","Nach","Nacha","Nag","Nagoi","Naid","Nak","Naka","Nako","Nakh","Nan","Nana","Nena","Narozh","Narush","Nash","Necha","Nechai","Nega","Nem","Neman","Nen","Nerad","Nes","Net","Netk","Netka","Nin","Nos","Nov","Nud","Nutit","Nut","Ob","Oblez","Oblezh","Oblesh)","Obel","Obezd","Obi","Obid","Obil","Oblak","Oblaka","Obrad","Obran","Obrat","Odin","Odno","Odol","Ogn","Ole","Olei","Ol'kha","Ol'sha","Opor","Opr","Orash","Orel","Oresh","Osel","Osob","Osobei","Osto","Ostoi","Ostr","Ostryi","Ot","Ota","Otmar","Otnia","Otrok","Ov","Ozer","Ozor","Pab","Pabek","Pabesh","Paba","Pach","Pak","Paki","Pache","Pakh","Pakha","Pal","Palets","Pan","Par","Para","Pas","Pat","Paun","Pav","Pava","Pchel","Pchela","Pek","Peka","Pekh","Pen","Pena","Per","Peru","Perv","Pervoi","Pesh","Pit'","Pivot'","Piat","Piatyi","Pik","Pikura","Pisk","Piskar ","Pisker","Plav","Plen","Plut","Pochin","Podiv","Pokhval","Pokra","Pol","Pole","Poliud","Polk","Pomnen","Pop","Popel","Por","Postan","Pot","Potikh","Pozd","Pozdo","Pozdnyi","Poznan","Pozvizd","Pr","Prav","Prem","Priam","Priby","Prid","Priia","Priiat","Prisn","Prisnyi","Prod","Prodat'","Pros","Prosit'","Prost","Prud","Pruditi","Prug","Prus","Ptach","Ptak","Ptachek","Ptakh","Pul","Pur","Pura","Put","Rab","Rabek","Rach","Racha","Rad","Rai","Rakh","Rakit","Rakita","Ral","Ralen","Ran","Ranyi","Rapot","Rapota","Rast","Rasti","Rosti","Rat","Rats","Rav","Ravnyi","Razum","Reg","Res","Resa","Reza","Rez","Riab","Riag","Riaka","Rob","Rod","Rog","Rol","Rolek","Rolak","Ros","Rosa","Rost","Rozh","Rub","Rud","Ruk","Ruka","Rum","Rumianyi","Rus","Rut","Ruta","Ruzh","Sab","Saba","Soba","Sad","Sasin","Sby","Sbyt","Sobyt'","Sek","Seku","Sel","Selo","Sem","Semi","Semo","Ser","Serd","Serebr","Serp","Sestr","Sestra","Set","Setiti ","Setovat'","Shar","Shara","Shched","Shchedr","Shchedryi","Shchek","Shchen","Shchenia","ShchenShtenia","Shcherb","Shcherba","Shchit","Shchuk","Shchuka","She","Sheia","Shest","Shestyi","Shib","Shibat","Shim","Shima","Shir","Shirokii","Shish","Shishman","Shkop","Shlekht","Shlekhta","Shliakhta","Shliakh","Shtenia","Shub","Shuba","Shui","Shum","Shuma","Shup","Shupek","Sin","Sinii","Sir","Skar","Skopek","Skor","Slab","Slad","Slav","Slava","Slavii","Slug","Sluga","Smed","Smil","Smokv","Smokva","Smol","Smola","Sob","Sok","Sokol","Sol","Solov","Solovei","Sor","Sora","Span","Spas","Spit","Spet","Spor","Stan","Stoi","Star","Staryi","Stav","Sto","Stolb","Stolp","Strakh","Stran","Strana","Strat","Strata","Strazh","Stregu","Streg","Stro","Stroi","Stup","Subot","Subota","Sud","Sui","Suk","Sur","Sviat","Sviatyi","Svin","Svin'ia","Syn","Tal","Tam","Tan","Tas","Tat","Tato","Tata","Tatia","Tech","Tekh","Tel","Telg ","Telo","Tem","Ten","Tep","Tepati","Ter","Terp","Terpet'","Tet","Teta","Tiag","Tir","Tol","Tolit","Tom","Ton","Trav","Trava","Treb","Treba","Tsan","Tsana","Tsena","Tsap","Tsapa","Tsar","Tsel","Tsen","Tsvet","Tug","Tur","Tverd","Tverdyi","Tvor","Tvorit'","Ub","Ubit","Ubyt","Udr","Udriti","Ugl","Ugol","Ugr","Upyr","Ur","Us","Usia","Ut","Uta","Uda","Uzh","Va","Vab","Vad","Vak","Vakh","Val","Var","Vats","Vav","Vavr","Vech","Vecher","Ved","Vek","Vel","Ver","Vera","Vesel","Vesn","Vesna","Vet","Vid","Vil","Vila","Vit","Vlad","Vlakh","Vlk","Volia","Volk","Volod","Volok","Vor","Vorobei","Voron","Vorona","Vorot","Vr","Vrach","Vrat","Vyk","Zar","Zel","Zem","Zemlia","Zern","Zerno","Zhab","Zhaba","Zhad","Zhada","Zhal","Zhalo","Zhar","Zhark","Zhavoronok","Zheg","Zhel","Zhelat'","Zhelez","Zhelezo","Zhemchug","Zhen","Zherav","Zhereb","Zhgu","Zhiv","Zhup","Zhurav","Zl","Zlyi","Zlat","Zlato","Zoloto","Zme","Zmei","Zna","Znat'","Zolot","Zor","Zora","Zoria","Zret'","Zub","Zver","Zvezd","Zvezda","Zvon")
							},
							"CIVILIZATION_SPAIN" :
							{
								"PRE" : ("Abejundio","Adoncia","Alita","Amador","Amata","Amato","Amistad","Arcadia","Belicia","Belinda","Breezy","Castel","Caton","Chale","Ciro","Cochiti","Colon","Concepcion","Consuelo","Damita","Devante","Diego","Dominga","Dorota","Drina","Dulcinea","Eldora","Elena","Elisa","Elvira","Emerald","Emilio","Eskarne","Esperanza","Esteban","Fidel","Fonda","Fuensanta","Galeno","Gaspar","Gitana","Hermelinda","Herminia","Iago","Ines","Isabel","Isidro","Isleta","Jaimica","Juanita","Kesare","Liani","Linda","Lola","Lujuana","Madeira","Madra","Mandy","Manuel","Manuela","Mariposa","Melisenda","Melosa","Mireya","Mora","Neron","Neva","Nina","Noe","Oleos","Paco","Paloma","Patia","Pilar","Querida","Raeka","Ramona","Ria","Rico","Rogelio","Rosalind","Sally","Salvador","Sandia","Santiago","Santos","Savanna","Senon","Sierra","Solana","Soledad","Tajo","Tia","Tierra","Vidal","Ximen","Xiomara","Yomaris","Zenon","Zerlina","abarca","abramzyk","abrego","acebedo","acevedo","acosta","acuna","adame","agarena","aguilar","aguirre","alaba","alagon","alanis","alaniz","albornoz","alcala","alcanta","alcegayurdinola","alcegaybarguem","alcega","aldaco","aldape","alfonso","allred","almandos","almanza","almaraz","almenara","altamira","altamirano","alvarado","alvarezbernaldo","alvarez","alvearysalazar","alviar","anderson","andrada","anguiano","angulo","anon","ansaldua","anunsarria","anzaldua","anzualda","aragonyabollardo","aragon","arcaute","archiondo","arellano","arevalo","arguelles","arispe","armendarez","arrechederra","arredondo","arrevalo","arrieta","arriola","arzamudi","ashby","autrey","avellanedayzuniga","avellaneda","avila","ayala","badello","badi","baezdebenavides","baezdetrevino","baeztrevino","bagics","baladez","ballesteros","balli","balmayor","barba","barbarigo","barbosa","barbour","barcenas","bareda","baresa","barredayebra","barrera","barrio","barrios","bautista","bayarena","bazan","beaver","becerra","belmar","beltaifa","beltran","benavides","benitez","bera","vera","berengar","bermudez","betancourt","blaker","blevins","bocanegra","boden","borel","boren","borges","borja","borrego","bosque","bosques","botellodemorales","botello","bouis","boyd","bracamonte","braganca","brazell","brittingham","bronzin","brown","buentello","bullard","bundamande","bustamente","byram","caballero","cabrera","cadena","cadriel","cajacob","calderon","calis","callen","camacho","camarillo","cameron","camorlin","camorlingo","campeoni","campos","canales","cano","cansino","canto","cantu","capistran","capistrano","cara","carbajal","carballo","cardenas","cardoso","carmona","carrejo","carrillo","carrion","carroll","carvajal","casarez","casas","castaneda","castano","castellano","castellon","castilla","castillo","castro","cavazos","cavello","cayeros","cenac","cepeda","cerda","cerda?","cervantes","cervera","chamberlain","champion","chano","chapa","charles","chavana","chavezycaballero","chavez","chirino","chronis","cisneros","clarke","cobarrubias","cobarubios","cobos","coddington","codina","colchado","conocenti","contreras","cook","corona","coronado","corral","correa","cortaverria","cortes","cortez","cortinas","crockett","cruz","cuellar","cueto","curl","dacosta","danache","davalos","davila","davis","deanda","defoix","delacruz","delafuente","delagarzafalcon","delagarza","delallata","delamancha","delapaz","delapontiga","delarosa","delavega","deleonquintanilla","deleon","deluna","demesquita","depena","dequinones","derienzo","desosa","delcampillo","delcampo","delrio","delaunay","derby","dias","diazhernandez","diaz","dominguez","donnelly","doria","dovalina","duarte","dufour","duran","echeverzysubiza","eggers","elias","elizondo","delisondo","elizondo","ellis","enriquez","eribe","escalante","escamilla","escandon","escobar","esparza","esperiquetq","espino","esquibel","esquivel","estrada","everett","farias","fee","fernandesdecastro","fernandesdesoutomaior","fernandes","fernandezdecastro","fernandez","floresdeabrego","floresgalan","floresorvalle","floresvaldes","flores","fonseca","franco","fuente","fuentes","furundarena","gaitan","galan","galindo","gallardo","galvan","garces","garciacastanon","garciadearagon","garciadesepulveda","garciadesoberon","garcia","garrido","garza","garzano","gassand","gavilan","geisinger","gil","gill","giron","godoy","gomezmascorro","gomez","gongora","gonzaba","gonzalesdebaro","gonzales","gonzalezdequintanila","gonzalezdequintanilla","gonzalez","goodjohn","gorena","gracia","greer","grimes","guajardo","guardado","guajardo","guerradiaz","guerra","guerrero","guevara","guillen","gutierres","gutierrez","guzman","hammerly","hancock","haraldsdottir","haramboure","hassenfratz","hernandezhidalgo","hernandez","herreraydiaz","herrera","herrmann","hidalgo","higuera","hines","hinojos","orynojos","hinojosa","hohenstaufen","hohenstaufens","holquin","holsey","howard","howell","hoyos","huerta","hyde","ibarra","iglesias","imperial","infante","iribe","irigoyen","iruegas","jacobs","jaffe","jaime","jauregui","jaurigui","jeano","jensen","jimenezdecisneros","jimenez","jones","jorge","juarez","kent","koester","kreuzer","krippner","ladrondeguevara","landa","landin","laphittayberri","lara","lartigue","laurel","layseca","leal","ledwig","leiba","leite","lerma","lessa","lewallan","leza","liehs","liendro","ligarde","light","lisarraras","lissardadefee","lizaranzu","lizarrarasycuellar","llanas","llanes","loa","lobodeacuna","loboguerrero","lombrana","longoriadelapontiga","longoriadequinones","longoriafloresvaldes","longoriaygarcia","castanon","longoria","lopezberlanga","lopezdejaen","lopezprieto","lopez","loya","loys","lozano","lucio","lugo","lujan","luna","lund","luxan","machado","madoma","madano","mahn","maldonado","malito","mancha","mancias","mangania","mangel","manrique","mansilla","manzano","mares","marlow","marquez","marroquin","martin","martinezguajardo","martinez","marulanda","mascorro","massaro","mata","matta","maya","amaya","mayaytrevino","maya","mazariegos","mccandless","mcclure","mccreary","mccutcheon","mcdonald","mcrae","mederia","medina","medrano","mejia","menchaca","mendeaux","mendez","mendiola","mendiondo","mendosa","mendoza","meneses","merinaya","mesa","michaca","menchaca","milares","miller","minjares","mireles","mitchell","molano","molina","monje","monson","montalvo","montana","montanez","montemayor","montesdeoca","montes","montezuma","moore","moorman","mora","morales","moreno","morin","morrison","motayportugal","mota","mother","moya","munguia","muniz","munosyserrano","munos","munoz","musqueda","nagas","nanez","narriahondo","narro","narvaez","nava","navaira","navarro","nevarez","nichols","norona","numbideechenaguizar","nunes","nunez","o'brien","obregon","ochoa","ojeda","olarte","olguin","oliden","olivares","olivarez","oliver","onate","oria","doria","oria","oropeza","oroz","orta","ortiz","otero","owen","oyarbides","ozuna","pacheco","padilla","paes","paez","palacios","paliaga","palma","palmer","paredes","paz","peck","pedraza","pena","penalossa","penn","perales","perezdeescamilla","perez","periera","personius","pesado","pina","pires","pitzer","plantagenet","polanco","pompa","poncedeleon","ponce","porcayo","portugal","priddy","prieto","puente","quintana","quintanilla","quintero","raimundez","ramirez","ramon","ramos","rangel","recio","relaviraoe","rendon","reno","renteria","requenez","resendes","resendez","ressa","revilla","reyes","reyna","rice","richards","rio","rios","rivas","rivera","robles","rocha","rock","rodrguez","rodrigues","rodriguez","romero","romo","rosa","rosado","rosales","rosemand","rosillo","ross","roxas","rojas","ruedaszeuallos","ruelas","ruff","ruiz","runyon","rus","saavedra","saens","saenz","saintmalo","sais","salamea","salas","salasar","salazar","saldana","saldivar?","saldivar","saldua","saleta","salido","salinasdepena","salinas","sanmartin","sanmiguel","sanches","sanchezsaenz","sanchez","sandoval","santiagoymedina","santoscoy","santos","sarmiento","sayas","schacherl","schereck","schiapapria","sedas","segariol","sendeja","sepulveda","sernayalarcon","serna","serrano","servin","sheets","shelby","siller","silva","simms","skleros","smith","smotkin","soberon","sobrevilla","solis","soliz","solorio","sosaalbornoz","sosa","soto","sotomayor","spencer","starck","steele","stenzel","stewart","suarezdelongoria","sutherland","swynford","tagle","tamayo","tames","tamez","tapia","theriot","tijerina","tolosa","toro","torres","trevino","trillaes","turner","unknown","urdinola","uribe","urrutia","uzcanga","valadez","valdera","valdes","valdez","valle","ovalle","vallerecio","valle","vallejo","valverde","vargas","vasquez","vassiliou","vecchio","vega","vela","velasco","velasquez","velautigus","venecia","vera","vidal","vidaurri","vieira","villafana","villalobos","villalon","villanueva","villar","villarico","villarreal","villegas","vivero","vizcaya","vohburg","volpe","vonhohenstaufen","vonmeissen","wagman","walker","walsh","washington","wattles","werbiski","wills","wise","ybarra","yguelesciaysantacruz","ynda","ynojosa","york","yrers","ysaguirre","yslaypalacio","yslasypalacio","zaldivar","zambrano","zamora","zapata","zarateybayarena","zarate","zavala","zavaleta","zepeda","zertucha","zorrilla","zulaica","zunigayavellaneda","zuniga"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_VIKING" :
							{
								"PRE" : ("A","Ab","c","Ad","Af","Agr","st","As","Al","Adw","Adr","Ar","r","h","ad","D","r","w","d","th","Et","Er","El","ow","F","r","r","w","wyd","l","l","a","b","er","ed","th","r","eg","r","d","l","c","n","r","h","ev","k","a","r","h","h","b","ic"),
								"MID" : ("a","e","u","o","re","ale","li","ay","rdo","e","i","i","ra","la","li","nda","erra","i","e","ra","la","li","o","ra","go","i","e","re","y"),
								"END" : ("a","and","b","bwyn","baen","bard","c","ctred","cred","ch","can","con","d","dan","don","der","dric","dfrid","dus","f","g","gord","gan","l","ld","li","lgrin","lin","lith","lath","loth","ld","ldric","ldan","m","mas","mma","mos","mar","mond","n","nydd","nidd","nnon","nwan","nyth","nad","nn","nnor","nd","p","r","ran","ron","rd","s","sh","seth","sean","t","th","th","tha","tlan","trem","tram","v","vudd","w","wan","win","win","wyn","wyn","wyr","wyr","wyth")
							},
							"CIVILIZATION_ZULU" :
							{
								"PRE" : ("Amahle","Andile","Ayanda","Ayize","Bandile","Bheka","Bhekizizwe","Bhekithemba","Bonginkosi","Bongani","Buyisiwe","Busisiwe","Dingane","Duduzile","Dumisani","Gugu","Hlengiwe","Jabulani","Jabu","Khethiwe","Kwanele","Lindelani","Lindiwe","Londisizwe","Mandla","Manelesi","Mbali","Mondli","Msizi","Muzikayise","Nandi","Nathi","Nhlakanipho","Njabulo","Nkosinathi","Nkosingiphile","Nkosiphendule","Nobuhle","Nobesuthu","Nolwazi","Nomathemba","Nomsa","Nomusa","Nomvula","Nomzamo","Nonhlanhla","Nonkululeko","Nothembi","Nozipho","Ntokozo","Ntombintombi","Ntombifuthi","Ntombizanele","Ntombizodwa","Phila","Philani","Phumlani","Sakhile","Samukelisiwe","Sandile","Sanele","S'bu","Sibongile","Sibongiseni","Sibusiso","Sifiso","Sihle","Simangele","Simosihle","Simphiwe","Sindisiwe","Sinethemba","Sinenhlanhla","Siphephelo","Siphelele","Sipho","Siphokazi","Sithembiso","Siyabonga","Siyanda","Sizani","Sizwe","Slindile","S'phamandla","Thabo","Thabisa","Thamsanqa","Thandeka","Thandiwe","Thando","Themba","Thembisile","Thenjiwe","Tholakele","Thulani","Thulisile","Lwazi","Unathi","Vusi","Vusumuzi","Wandile","Xolisile","Xolani","Zama","Zandile","Zanele","Zithembe","Zinhle","Zodwa"),
								"MID" : (),
								"END" : ()
							},
							"CIVILIZATION_MINOR" :
							{
								"PRE" : ("A","Ab","c","Ad","Af","Agr","st","As","Al","Adw","Adr","Ar","r","h","ad","D","r","w","d","th","Et","Er","El","ow","F","r","r","w","wyd","l","l","a","b","er","ed","th","r","eg","r","d","l","c","n","r","h","ev","k","a","r","h","h","b","ic"),
								"MID" : ("a","e","u","o","re","ale","li","ay","rdo","e","i","i","ra","la","li","nda","erra","i","e","ra","la","li","o","ra","go","i","e","re","y"),
								"END" : ("a","and","b","bwyn","baen","bard","c","ctred","cred","ch","can","con","d","dan","don","der","dric","dfrid","dus","f","g","gord","gan","l","ld","li","lgrin","lin","lith","lath","loth","ld","ldric","ldan","m","mas","mma","mos","mar","mond","n","nydd","nidd","nnon","nwan","nyth","nad","nn","nnor","nd","p","r","ran","ron","rd","s","sh","seth","sean","t","th","th","tha","tlan","trem","tram","v","vudd","w","wan","win","win","wyn","wyn","wyr","wyr","wyth")
							},
							"CIVILIZATION_BARBARIAN" :
							{
								"PRE" : ("A","Ab","c","Ad","Af","Agr","st","As","Al","Adw","Adr","Ar","r","h","ad","D","r","w","d","th","Et","Er","El","ow","F","r","r","w","wyd","l","l","a","b","er","ed","th","r","eg","r","d","l","c","n","r","h","ev","k","a","r","h","h","b","ic"),
								"MID" : ("a","e","u","o","re","ale","li","ay","rdo","e","i","i","ra","la","li","nda","erra","i","e","ra","la","li","o","ra","go","i","e","re","y"),
								"END" : ("a","and","b","bwyn","baen","bard","c","ctred","cred","ch","can","con","d","dan","don","der","dric","dfrid","dus","f","g","gord","gan","l","ld","li","lgrin","lin","lith","lath","loth","ld","ldric","ldan","m","mas","mma","mos","mar","mond","n","nydd","nidd","nnon","nwan","nyth","nad","nn","nnor","nd","p","r","ran","ron","rd","s","sh","seth","sean","t","th","th","tha","tlan","trem","tram","v","vudd","w","wan","win","win","wyn","wyn","wyr","wyr","wyth")
							},
							"DEFAULT" :
							{
								"PRE" : ("A","Ab","c","Ad","Af","Agr","st","As","Al","Adw","Adr","Ar","r","h","ad","D","r","w","d","th","Et","Er","El","ow","F","r","r","w","wyd","l","l","a","b","er","ed","th","r","eg","r","d","l","c","n","r","h","ev","k","a","r","h","h","b","ic"),
								"MID" : ("a","e","u","o","re","ale","li","ay","rdo","e","i","i","ra","la","li","nda","erra","i","e","ra","la","li","o","ra","go","i","e","re","y"),
								"END" : ("a","and","b","bwyn","baen","bard","c","ctred","cred","ch","can","con","d","dan","don","der","dric","dfrid","dus","f","g","gord","gan","l","ld","li","lgrin","lin","lith","lath","loth","ld","ldric","ldan","m","mas","mma","mos","mar","mond","n","nydd","nidd","nnon","nwan","nyth","nad","nn","nnor","nd","p","r","ran","ron","rd","s","sh","seth","sean","t","th","th","tha","tlan","trem","tram","v","vudd","w","wan","win","win","wyn","wyn","wyr","wyr","wyth")
							},
						}



def getRandomCivilizationName0(iCivilizationType, pUnit, pCity, masculine):
	unitName = ""

	if(gc.getCivilizationInfo(iCivilizationType) != None):
		strCivilizationType = gc.getCivilizationInfo(iCivilizationType).getType()

	BugUtil.debug("getRandomCivilizationName(%s, %s, %s, %s):%s" % (iCivilizationType, pUnit, pCity, masculine, strCivilizationType))
	if (GENERATORS.has_key(strCivilizationType)):
		generator = GENERATORS[strCivilizationType]
		generator.activate(strCivilizationType)
		return generator.generate(pUnit, pCity, masculine)

	firstName = generateCivilizationName(iCivilizationType)
	lastName = generateCivilizationName(iCivilizationType)

	unitName = firstName + " " + lastName

	if(len(unitName) < 14):
		middleName = generateCivilizationName(iCivilizationType)
		unitName = firstName + " " + middleName + " " + lastName


	return unitName

def getRandomCivilizationName(iCivilizationType, pUnit, pCity):
	return getRandomCivilizationName0(iCivilizationType, pUnit, pCity, True)

def getRandomCivilizationFemaleName(iCivilizationType, pUnit, pCity):
	return getRandomCivilizationName0(iCivilizationType, pUnit, pCity, False)

def getRandomNameExt(pUnit, pCity, bMasculine):
	iPlayer = pUnit.getOwner()
	pPlayer = gc.getPlayer(iPlayer)
	iCivilizationType = pPlayer.getCivilizationType()

	if(gc.getCivilizationInfo(iCivilizationType) != None):
		strCivilizationType = gc.getCivilizationInfo(iCivilizationType).getType()

	if(GENERATORS.has_key(strCivilizationType)):
		return GENERATORS[strCivilizationType].generate(pUnit, pCity, bMasculine)

	return getRandomCivlizationName0(iCivilizationType, pUnit, pCity, bMasculine)


def generateCivilizationName(iCivilizationType):
	strCivilizationType = "DEFAULT"

	if(gc.getCivilizationInfo(iCivilizationType) != None):
		strCivilizationType = gc.getCivilizationInfo(iCivilizationType).getType()
		if not civilizationNameHash.has_key(strCivilizationType):
			strCivilizationType = "DEFAULT"

	strPre = ""
	strMid = ""
	strEnd = ""
	random = gc.getASyncRand()

	if(len(civilizationNameHash[strCivilizationType]["PRE"]) > 0):
		strPre = civilizationNameHash[strCivilizationType]["PRE"][random.get(len(civilizationNameHash[strCivilizationType]["PRE"]), "Random Name")]

	if(len(civilizationNameHash[strCivilizationType]["MID"]) > 0):
		strMid = civilizationNameHash[strCivilizationType]["MID"][random.get(len(civilizationNameHash[strCivilizationType]["MID"]), "Random Name")]

	if(len(civilizationNameHash[strCivilizationType]["END"]) > 0):
		strEnd = civilizationNameHash[strCivilizationType]["END"][random.get(len(civilizationNameHash[strCivilizationType]["END"]), "Random Name")]

	strName = string.capwords(strPre+strMid+strEnd)

	return strName


# Returns a random unique name not found in the global mercenary pool
def getRandomName():

	unitName = ""
	random = gc.getASyncRand()

	firstName = firstNameList[random.get(len(firstNameList), "Random Name")]
	lastName = lastNamesList[random.get(len(lastNamesList), "Random Name")]

	unitName = firstName + " " + lastName

	if(len(unitName) < 14):
		middleName = middleNameList[random.get(len(middleNameList), "Random Name")]
		unitName = firstName + " " + middleName + " " + lastName


	return unitName
