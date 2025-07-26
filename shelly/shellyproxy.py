import logging
import subprocess
import json
from dotenv import dotenv_values
from flask import Flask, render_template, request

# flask --app shellyproxy run --debug --host 0.0.0.0 -port 5010

LOGGER = logging.getLogger('werkzeug')
LOGGER.setLevel(logging.ERROR)


app = Flask(__name__)
shelly_args = None
shelly_url = "http://192.168.178.128/relay/0"

@ app.route("/")
def index():
    return render_template('index.html')


@app.route("/toggle", methods=("POST", ))
def toggle():
    state = request.get_json()
    print(state)
    onoff = "on" if state["relay"] == "On" else "off"
    args = shelly_args + [f"{shelly_url}?turn={onoff}"]
    cp = subprocess.run(args, capture_output=True)
    if cp.returncode != 0:
        return {"relay": "???"}
    status = json.loads(cp.stdout)
    return({"relay": "On" if status["ison"] is True else "Off"})



@app.route("/update", methods=("GET", ))
def update():
    args = shelly_args + [f"{shelly_url}"]
    cp = subprocess.run(args, capture_output=True)
    if cp.returncode != 0:
        return {"relay": "???"}
    status = json.loads(cp.stdout)
    return({"relay": "On" if status["ison"] is True else "Off"})
    

if __name__ == "__main__":
    secrets = dotenv_values(".env")
    username = secrets["USERNAME"] 
    password = secrets["PASSWORD"]
    shelly_args = ["curl", "--anyauth", "-u", f"{username}:{password}"]
    port = 5011
    print(f"Server runs on port {port}")
    app.run(host="0.0.0.0", port=port)
    
# curl -v --anyauth -u admin:shelly261037 http://192.168.178.128/relay/0?turn=on
