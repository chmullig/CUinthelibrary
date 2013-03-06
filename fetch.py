import json
import csv
from datetime import datetime, date, time, timedelta
from bs4 import BeautifulSoup
import requests
from monthdelta import MonthDelta
import sqlite3

VERBOSE=False

params = {"function" : "view", "edit_mode" : "individual", "mode" : "month",
    "library" : None, "year" : None, "day" : None}
baseurl = "http://hours.library.columbia.edu"

libraries = csv.DictReader(open("libraries.txt"), delimiter="\t")

conn = sqlite3.connect("hours.sqlite")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS hours \
    (date text, library text, grp text, open text, close text, status text, notes text)")
conn.commit()

thismonth = date(date.today().year, date.today().month, 1)

for library in libraries:
    if library["library"].startswith("#"):
        continue
    params["library"] = library["library"]
    for month in [thismonth, thismonth+MonthDelta(months=1), thismonth+MonthDelta(months=2)]:
        params["year"] = month.year
        params["day"] = month.timetuple().tm_yday
        r = requests.get(baseurl, params=params)
        s = BeautifulSoup(r.text)
        print "%s%s: Looked for %s. Found %s for %s" % (("\t" if library["library"] != library["group"] else ""),
            library["library"], library["name"],
            s.find("big").find(class_="gray").text.strip(": "),
            s.find("big").find(class_="color").text)

        days = sorted(s.find_all(class_='date') + s.find_all(class_='today_date'))
        for day in days:
            notes = day.parent.parent.find(class_="day_notes").text.strip()
            dt = date(month.year, month.month, int(day.text))
            try:
                hours = day.parent.parent.find(class_="today_hours").text.strip()
                if hours.lower() == "24 hours":
                    opens = datetime.combine(dt, time(0, 0))
                    closes = opens+timedelta(days=1)
                else:
                    openStr, closeStr = hours.split("-")
                    if openStr == "Noon":
                        parsedTime = time(12,00)
                    elif openStr == "Midnight":
                        parsedTime = time(0,00)
                    else:
                        parsedTime = datetime.strptime(openStr, "%I:%M%p").time()
                    opens = datetime.combine(dt, parsedTime)

                    if closeStr == "Noon":
                        parsedTime = time(12,00)
                    elif closeStr == "Midnight":
                        parsedTime = time(0,00)
                    else:
                        parsedTime = datetime.strptime(closeStr, "%I:%M%p").time()
                    closes = datetime.combine(dt, parsedTime)
                    
                    if closes.time() < time(8, 00):
                        #it closes after midnight
                        closes = closes+timedelta(days=1)
                status = ""
                length = (closes - opens).total_seconds()/(60*60)
            except AttributeError:
                try:
                    status = day.parent.parent.find("b").text.strip()
                except AttributeError:
                    status = "Unknown"
                opens = None
                closes = None
                length = 0

            cursor.execute("INSERT INTO hours VALUES (?,?,?,?,?,?,?)",
                (dt, library["library"], library["group"],
                opens, closes, status, notes))
                
            if VERBOSE:
                msg = "\t\t%s: %s to %s. %s hrs." % (dt, opens, closes, length)
                try:
                    if status:
                        msg += " " + status
                except NameError:
                    pass
                if notes:
                    msg += " (%s)" % notes
                print msg
        conn.commit()