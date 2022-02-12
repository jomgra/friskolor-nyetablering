import json, sqlite3
import sys, os.path, datetime

#  SITE CLASS  ====================
#
#  x = site(output_path)
#  x.addPage(id, title, desc)
#  x.removePage(id)
#  x.save()

class site():
	def __init__(self, path):
		self.path = self._fixpath(path)
		self.id = "index"
		self.file = self.path + self.id + ".cfg"
		self._loadcfg()
		return
	
	def _fixpath(self, path):
		if path[-1] != "/":
			path += "/"
		return path
				
	def _loadcfg(self):
		
		try:
			with open(self.file, "r", encoding="utf8") as f:
				content = f.read()
				c = json.loads(content)
				self.title = c["title"]
				self.pages = c["pages"]
				self.exist = True
		except:
			self.title = ""
			self.pages = []
			self.exist = False
		return
		
	def addPage(self, index, id, title, desc):
		page = {
			"index": int(index),
			"id": self._cleanid(id),
			"title": title,
			"desc": desc
			}
		for i in range(len(self.pages)):
			if self.pages[i]["id"] == self._cleanid(id):
				self.pages.pop(i)
				break
		self.pages.append(page)	
		self.pages.sort(key=lambda x: x["index"])
		return

	def removePage(self, id):
		for i in range(len(self.pages)):
			if self.pages[i]["id"] == self._cleanid(id):
				self.pages.pop(i)
				break
		return

	def _cleanid(self, idTxt):
		chars = [" ", "å", "ä", "ö"]
		newChars = ["", "a", "a", "o"]
		idTxt = idTxt.lower()
		for i in range(len(chars)):
			idTxt = idTxt.replace(chars[i], newChars[i])
		return idTxt
	
	def dump(self):
		dump = vars(self).copy()
		dump.pop("file")
		dump.pop("path")
		dump.pop("exist")
		return dump
	
	def json(self):
		return json.dumps(self.dump())
		
	def save(self):
		try:
			with open(self.file, "w", encoding="utf8") as f:
				f.write(self.json())
				if self.exist:
					print("Updated:", self.file)
				else:
					print("Created:", self.file)
		except:
			print("Couldn't save file:", self.file)

#  CHARTJS CLASS  =================
#
#  x = chartjs(typeofchart)
#  x.addDataset(label, dataarray, clr)
#  x.addLabels(labelsarray)
#  x.save()
#  x.options - attributes
				
class chartjs:
	defaultColor = "#fff"
	
	def __init__(self, type="line"):
		self.type = type.lower()
		self.data = {
			"labels": [],
			"datasets": []
			}
		self.options = {
			"maintainAspectRatio": False,
			"plugins": {
				"display": False,
				"legend": {},
				"tooltip": {}
			},
			"scales": {
				"y": {
					"beginAtZero": True
					}
			},
			"animations": {}
			}
		return
		
	def _fixpath(self, path):
		if path[-1] != "/":
			path += "/"
		return path
		
	def _cleanid(self, idTxt):
		chars = [" ", "å", "ä", "ö"]
		newChars = ["", "a", "a", "o"]
		idTxt = idTxt.lower()
		for i in range(len(chars)):
			idTxt = idTxt.replace(chars[i], newChars[i])
		return idTxt
		
	def dump(self):
		return vars(self)
	
	def json(self):
		return json.dumps(vars(self))
	
	def addDataset(self, label, dataList, color=defaultColor):
		dset = {
			"label": label,
			"data": dataList,
			"backgroundColor": color,
			"borderColor": color
		}
		if len(dataList) > 0:
			self.data["datasets"].append(dset)
		return
	
	def addLabels(self, labels):
		if len(labels) > 0:
			self.data["labels"] = labels
		return
		
	def save(self, path, id):
		file = self._fixpath(path) + self._cleanid(id) + ".chart"
		try:
			with open(file, "w", encoding="utf8") as f:
				f.write(self.json())
			print("Saved:", file)
		except:
			print("Couldn't save file:", self.file)


#  SET OUTPUT PATH =============

path = os.path.dirname(os.path.realpath(__file__))

if len(sys.argv) > 1:
	opath = sys.argv[1]
else:
	opath = path + "/"

#  CHART SETUP  =================

db = path + "/skolinspektionen.db" 

if not os.path.isfile(db):
	print("No database")
	sys.exit()
	
try:
	con = sqlite3.connect(db)
except Error as e:
	print(e)

cur = con.cursor()
cur.execute(f"SELECT * FROM skolinspektionen ORDER BY date")
data = cur.fetchall()

va = {}
for d in data:
	if d[1] in va:
		va[d[1]] += 1
	else:
		va[d[1]] = 1

sd = datetime.date(datetime.datetime.now().year, 1, 1)
ed = datetime.date.today()
delta = datetime.timedelta(days=1)

acva = 0
val = []
lbl = []
while sd <= ed:
	if str(sd) in va:
		acva += va[str(sd)]
	lbl.append(str(sd))
	val.append(acva)
	sd += delta

con.close()

chart = chartjs("line")

chart.addLabels(lbl)
chart.addDataset("Antal ansökning fram till detta datum", val)

chart.save(opath, "friskolansexpansion")

#  SITE SETUP  ===================

minasiffror = site(opath)

minasiffror.addPage(
	100,
	"friskolansexpansion",
	"Friskolans expansion",
	"Följ friskolekoncernernas expansion genom det ackumulerade antalet ansökningar om nyetablering av friskolor i Sverige. Uppgifterna hämtas automatiskt från Skolinspektionens diarium."
	)

minasiffror.save()
