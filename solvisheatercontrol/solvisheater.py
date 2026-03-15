import sqlite3
import requests
import json
import datetime
import time
import threading
from flask import Flask, request, jsonify, render_template
from common import DBPATH, DBFIELDS, DBVALUES, TABLENAME


app = Flask(__name__)
ipaddress = "192.168.178.137"
app.previous_state = None


@app.route("/power", methods=["POST"])
def power_event():
    # {'state': 'above', 'threshold': -100, 'power': -1983.9, 'channel': 1, 'device': 'shellypro2pm-ec626090c434'}
    data = request.json
    print("I>", datetime.datetime.fromtimestamp(time.time()), data, flush=True)
    assert "state" in data
    if data["state"] != app.previous_state:
        app.previous_state = data["state"]
        # Call get_power in a background thread 
        print("call get_power()", flush=True)
        threading.Thread(target=get_power).start()
    rval = {"status": "ok", "message": ""}
    print(rval, flush=True)
    return jsonify(rval), 200


@app.route("/get", methods=["GET"])
def get_power():
    url = f"http://{ipaddress}/rpc"
    payload = {"id":1,"method":"Shelly.GetStatus"}
    r = requests.post(url, data=json.dumps(payload))
    r = r.json()
    # print(json.dumps(r, indent=4))
    r = r["result"]["switch:0"]
    data = dict(time=time.time(), state=r["output"], power=r["apower"], aenergy=r["aenergy"]["total"])
    try:
        connection = sqlite3.connect(DBPATH)
        cursor = connection.cursor()
        print(f"{TABLENAME} -> {DBVALUES} -> {data}", flush=True)
        cursor.execute(f"INSERT INTO {TABLENAME} VALUES({DBVALUES})", data)
        connection.commit()
    except Exception as e:
        print(f"ERROR: {str(e)}")
    r = json.dumps(r, indent=4)
    return r


@ app.route("/")
def index():
    data = get_power()
    return render_template('index.html', title="Solvis Heater Log", data=data)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=False)
