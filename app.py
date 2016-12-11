import sys
import json
from lxml import html, etree
import requests

if len(sys.argv) < 2:
    print "JSON file required as an argument ex: python app.py data.json"
    sys.exit()

with open(sys.argv[1]) as data_file:    
    data = json.load(data_file)

USERNAME = data["username"]
PASSWORD = data["password"]
TERM = data["query"]["term"]
DEPT_ID = data["query"]["department"]
COURSE_ID = data["query"]["course"] # actually not needed currently, save just in case
SECTION_ID = data["query"]["section"]

# configuration variables
CONFIG = {
    "url": "https://webreg.usc.edu/",
    "username_name":  "USCID",
    "password_name": "PWD",
    "token_name": "__RequestVerificationToken",
    "container_class": "section_alt", # can be alt0 or alt1
    "section_class": "id_alt",
    "seats_class": "regSeats_alt",
    "hours_class": "hours_alt",
    "days_class": "days_alt",
    "instructor_class": "instr_alt"
}

def num_seats_open(status):
    if status == "Closed":
        return 0
    else:
        seats = [int(s) for s in status.split() if s.isdigit()]
        return seats[1] - seats[0]

# results object, we will mutate it and then return
results = {}
for section in SECTION_ID:
    results[section] = {}

# set up session object
session = requests.session()
page = session.get(CONFIG["url"] + "login")
tree = html.fromstring(page.content)
token = tree.xpath("//input[@name=\"" + CONFIG["token_name"] + "\"]/@value")[0]

# WebReg login
page = session.post(
    CONFIG["url"] + "login",
    data = {
        CONFIG["username_name"]: USERNAME,
        CONFIG["password_name"]: PASSWORD,
        CONFIG["token_name"]: token
    },
    headers = dict(referer=CONFIG["url"] + "login")
)

# WebReg departments (for a particular term)
page = session.get(
	CONFIG["url"] + "terms/termSelect?term=" + TERM, 
	headers = dict(referer = CONFIG["url"] + "login")
)

# WebReg course (in a particular department)
page = session.get(
    CONFIG["url"] + "courses?DeptId=" + DEPT_ID,
    headers = dict(referer = CONFIG["url"] + "departments")
)

tree = html.fromstring(page.content)
pagination = tree.xpath("(//ul[contains(@class, \"pagination\")])[1]/child::node()/a/text()") # get children of first ul.pagination
# NOTE: slightly inefficient, scrape first page twice (for pagination info, then for class info). accept inefficiency for readability
for i in pagination:
    if i.isdigit():
        # search each page for class registration and update status
        page = session.get(
            CONFIG["url"] + "courses?DeptId=" + DEPT_ID + "&page=" + i,
            headers = dict(referer = CONFIG["url"] + "departments")
        )
        tree = html.fromstring(page.content)
        
        # get container nodes, check for any variations of class names
        section = tree.xpath("//div[contains(@class, \"" + CONFIG["container_class"] + "0\") or contains(@class, \"" + CONFIG["container_class"] + "1\")]")
        
        # check every listing found for the queried class identifier
        for elem in section:
            tree = html.fromstring(etree.tostring(elem))
            identifier = tree.xpath("//span[contains(@class, \"" + CONFIG["section_class"] + "0\") or contains(@class, \"" + CONFIG["section_class"] + "1\")]/b/text()")
            seats = tree.xpath("//span[contains(@class, \"" + CONFIG["seats_class"] + "0\") or contains(@class, \"" + CONFIG["seats_class"] + "1\")]/span[2]/text()")
            hours = tree.xpath("//span[contains(@class, \"" + CONFIG["hours_class"] + "0\") or contains(@class, \"" + CONFIG["hours_class"] + "1\")]/text()")
            days = tree.xpath("//span[contains(@class, \"" + CONFIG["days_class"] + "0\") or contains(@class, \"" + CONFIG["days_class"] + "1\")]/text()")
            instructor = tree.xpath("//span[contains(@class, \"" + CONFIG["instructor_class"] + "0\") or contains(@class, \"" + CONFIG["instructor_class"] + "1\")]/text()")
            
            # check if matchs section we're looking for, remove from SECTION_ID array if it does
            for item in SECTION_ID:
                if identifier[0] == item:
                    results[item] = {
                        "seats": num_seats_open(seats[0]),
                        "hours": hours[0],
                        "days": days[0],
                        "instructor": instructor[0]
                    }
    
print json.dumps(results, indent=4)