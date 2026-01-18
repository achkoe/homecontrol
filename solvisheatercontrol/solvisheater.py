import sqlite3
import datetime
import time
from flask import Flask, request, jsonify, render_template
from common import DBPATH, DBFIELDS, DBVALUES


app = Flask(__name__)


@app.route("/power", methods=["POST"])
def power_event():
    # {'state': 'above', 'threshold': -100, 'power': -1983.9, 'channel': 1, 'device': 'shellypro2pm-ec626090c434'}
    data = request.json
    assert "power" in data
    currenttime = time.time()
    power = data["power"]
    print(f"time {currenttime} -> {power}")
    connection = sqlite3.connect(DBPATH)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO heater VALUES(?,?)", (currenttime, power))
    connection.commit()
    return jsonify({"status": "ok"}), 200


@app.route("/get", methods=["GET"])
def get_power():
    connection = sqlite3.connect(DBPATH)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM heater ORDER BY time DESC")
    return {"status": "ok", "data": cursor.fetchall()}


@ app.route("/")
def index():
    data = get_power()
    return render_template('index.html', title="Solvis Heater Log", data=data)
    

if __name__ == "__main__":
    # sqlite stuff
    print(DBPATH)
    connection = sqlite3.connect(DBPATH)
    cursor = connection.cursor()
    s = ",".join(f"{key} {DBFIELDS[key]}" for key in DBFIELDS)    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS heater ({s})")
    s = ",".join(DBFIELDS)
    # avoid writing duplicate items
    cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS uniquedata ON heater ({s})")
    # create trigger to delete items older than 1 year
    cursor.execute("""CREATE TRIGGER IF NOT EXISTS deletelast30days AFTER INSERT ON heater
                   BEGIN
                   DELETE FROM heater WHERE (julianday('now') - julianday(time, 'unixepoch')) > 30;
                   END
                   """)
    connection.commit()

    app.run(host="0.0.0.0", port=5020, debug=True)