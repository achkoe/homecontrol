import sqlite3
import requests
import json
import datetime
import time
from flask import Flask, request, jsonify, render_template
from common import DBPATH, DBFIELDS, DBVALUES


app = Flask(__name__)
ipaddress = "192.168.178.137"


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
    url = f"http://{ipaddress}/rpc"
    payload = {"id":1,"method":"Shelly.GetStatus"}
    r = requests.post(url, data=json.dumps(payload))
    r = r.json()
    r = r["result"]["switch:0"]
    r = json.dumps(r, indent=4)
    return r


@ app.route("/")
def index():
    data = get_power()
    return render_template('index.html', title="Solvis Heater Log", data=data)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=True)