from lxml import html, etree
import requests

USERNAME = ""
PASSWORD = ""
TERM = "20171"
DEPT_ID = ""
COURSE_ID = "" # actually not needed currently, save just in case
SECTION_ID = [""]

# configuration variables
CONFIG = {
    "url": "https://webreg.usc.edu/",
    "username_name":  "USCID",
    "password_name": "PWD",
    "token_name": "__RequestVerificationToken",
    "container_class": "section_alt",
    "section_class": "id_alt", # can be id_alt0 or id_alt1
    "seats_class": "regSeats_alt" # can be regSeats_alt0 or regSeats_alt1
}

# results object we will mutate and then return
results = {}
for section in SECTION_ID:
    results[section] = False

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
        
        for elem in section:
            tree = html.fromstring(etree.tostring(elem))
            identifier = tree.xpath("//span[contains(@class, \"" + CONFIG["section_class"] + "0\") or contains(@class, \"" + CONFIG["section_class"] + "1\")]/b/text()")
            seats = tree.xpath("//span[contains(@class, \"" + CONFIG["seats_class"] + "0\") or contains(@class, \"" + CONFIG["seats_class"] + "1\")]/span[2]/text()")
            
            for item in SECTION_ID:
                if item == identifier[0]:
                    if seats[0] != "Closed":
                        print "Class with section id " + item + " has " + seats[0] + " open seats!"
                        results[item] = True
    
print results