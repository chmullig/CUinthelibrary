import json
import csv
from datetime import datetime, date, time, timedelta

from bs4 import BeautifulSoup
import requests

now = date.today()

params = {"function" : "view", "edit_mode" : "individual", "mode" : "month",
    "library" : None, "year" : now.year, "day" : now.timetuple().tm_yday}
baseurl = "http://hours.library.columbia.edu"


libraries = csv.DictReader(open("libraries.txt"), delimiter="\t")

def preptime(dt, timeStr):
    if timeStr == "Noon":
        parsedTime = time(12,00)
        dttime = datetime.combine(dt, parsedTime)
    elif timeStr == "Midnight":
        parsedTime = time(0,00)
        dttime = datetime.combine(dt, parsedTime)+timedelta(days=1)
    else:
        parsedTime = datetime.strptime(timeStr, "%I:%M%p").time()
        dttime = datetime.combine(dt, parsedTime)
    return dttime


for library in libraries:
    if library["library"].startswith("#"):
        continue
    params["library"] = library["library"]
    r = requests.get(baseurl, params=params)
    s = BeautifulSoup(r.text)
    print "%s%s: Looked for %s. Found %s for %s" % (("\t" if library["library"] != library["group"] else ""),
        library["library"], library["name"],
        s.find("big").find(class_="gray").text.strip(": "),
        s.find("big").find(class_="color").text)

    days = sorted(s.find_all(class_='date') + s.find_all(class_='today_date'))
    for day in days:
        notes = day.parent.parent.find(class_="day_notes").text.strip()
        dt = date(now.year, now.month, int(day.text))
        try:
            hours = day.parent.parent.find(class_="today_hours").text.strip()
            if hours.lower() == "24 hours":
                opens = datetime.combine(dt, time(0, 0))
                closes = opens+timedelta(days=1)
            else:
                openStr, closeStr = hours.split("-")
                opens = preptime(dt, openStr)
                closes = preptime(dt, closeStr)
                if closes.time() < time(8, 00):
                    #it closes after midnight
                    closes = closes+timedelta(days=1)
            status = ""
        except AttributeError:
            status = day.parent.parent.find("b").text.strip()
            opens = None
            closes = None
            

        msg = "\t\t%s: %s to %s" % (dt, opens, closes)
        try:
            if status:
                msg += " " + status
        except NameError:
            pass
        if notes:
            msg += " (%s)" % notes
        print msg