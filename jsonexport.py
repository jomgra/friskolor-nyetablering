import sqlite3, sys
import json
import os.path
import datetime

path = os.path.dirname(os.path.realpath(__file__))
db = path + "/skolinspektionen.db" 
jsonpath = path + "/output/"


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

print("Exporting data to json...")

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

data = { "label" : lbl, "value": val}
print(data)
json_string = json.dumps(data)
	
file = jsonpath + "friskola.json"
with open(file, "w", encoding="utf8") as f:
	f.write(json_string)

print(f"Done")
con.close()

