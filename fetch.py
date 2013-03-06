import json
import csv
import datetime

from bs4 import BeautifulSoup
import requests

now = datetime.date.today()

params = {"function" : "view", "edit_mode" : "individual", "mode" : "month",
    "library" : None, "year" : now.year, "day" : now.timetuple().tm_yday}
baseurl = "http://hours.library.columbia.edu"


libraries = csv.DictReader(open("libraries.txt"), delimiter="\t")

for library in libraries:
    params["library"] = library["library"]
    r = requests.get(baseurl, params=params)
    s = BeautifulSoup(r.text)
    print "%s%s: Looked for %s. Found %s for %s" % (("\t" if library["library"] != library["group"] else ""),
        library["library"], library["name"],
        s.find("big").find(class_="gray").text.strip(": "),
        s.find("big").find(class_="color").text)