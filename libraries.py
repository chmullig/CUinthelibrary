from flask import Flask, session, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    con = sqlite3.connect("hours.sqlite")
    cur = con.cursor()
    query = """select distinct *, round((julianday(close)-julianday("now", "localtime"))*24, 2)
                from hours
                where datetime("now", "localtime") between datetime(open) and datetime(close)
                order by library"""
    cur.execute(query)
    libs = cur.fetchall()
    return render_template("index.html", libs=libs)
    

if __name__ == "__main__":
    app.run(debug=True)

