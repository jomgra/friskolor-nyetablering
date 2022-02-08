import sys, os.path
import requests
from bs4 import BeautifulSoup
import sqlite3

url = "https://externsearchport.skolinspektionen.se/"

needle = "ansökan om godkännande för en nyetablering av en fristående"

path = os.path.dirname(os.path.realpath(__file__))

db = path + '/skolinspektionen.db'

def createconnection(db_file):
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	
	return conn


def createdb(db):
	conn = createconnection(db)
	cursor = conn.cursor()
	sql = '''
	CREATE TABLE "skolinspektionen" (
		"dnr" TEXT,
		"date" TEXT,
		"company" TEXT,
		PRIMARY KEY("dnr", "date")
		)
	'''
	cursor.execute(sql)
	conn.close()
	return
	
	
def addpost(dnr, date, company):
	try:
		conn = createconnection(db)
		cursor = conn.cursor()
		sql = f'INSERT INTO skolinspektionen ( dnr, date, company ) values ("{dnr}", "{date}", "{company}")'
		cursor.execute(sql)
		conn.commit()
		conn.close()
		
	except:
		pass
	
	return


if not os.path.isfile(db):
	createdb(db)

s = requests.Session() 
web = s.get(url)
soup = BeautifulSoup(web.text, "html5lib")

input = soup.find_all("input")

payload = {}
for i in input:
	id = i.get("id")
	value = i.get("value")
	payload[id] = value

payload["ddlSearchInterval"] = "-1d:-1d"
#payload["ddlSearchInterval"] = "-3m:-1d"

web = s.post(url, payload)

soup = BeautifulSoup(web.text, "html5lib")

cases = web.text.split("\r\n")
s = {}

for case in cases[1:]:
	dta = case.split("\t")
	if len(dta) == 3:
		desc = dta[2].lower().strip()
		if (desc.find(needle) != -1):
			sp = desc.split(",")
			addpost(dta[0], dta[1], sp[-1])
			#print(dta[0],"|", dta[1], "|", sp[-1])

