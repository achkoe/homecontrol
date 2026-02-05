import sys
import pathlib
import json
import sqlite3
import time
import datetime
import multiprocessing
import queue
import logging
from collections import deque
from flask import Flask, render_template, request
from base import LOGGER, CONFIGURATION_NAME, LOGGING_NAME, VERSION
from controller import setup, run

APP = Flask(__name__)

@APP.route("/")
def index():
    return render_template('index.html', version=f"v{VERSION}")


@APP.route("/get")
def get():
    with pathlib.Path(__file__).parent.joinpath(LOGGING_NAME).open("r") as fh:
        valve_log = json.load(fh)
    return valve_log

@APP.route("/set", methods=("POST", ))
def set():
    state = request.get_json()
    LOGGER.info(f"state -> {state}")
    configuration = setup()
    run(configuration, "enable" if state["state"] == "false" else "disable")
    return state


if __name__ == "__main__":
    APP.run(host="0.0.0.0", debug=True)