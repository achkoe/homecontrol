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
from common import LOGGER, CONFIGURATION_NAME

APP = Flask(__name__)

@APP.route("/")
def index():
    return render_template('index.html', version=f"v{VERSION}")


@APP.route("/get")
def get():
    global INQUEUE, OUTQUEUE
    rval = {"status": "ok"}
    INQUEUE.put("get")
    try:
        response = OUTQUEUE.get(block=False)
        print(f"response -> {response}")
        rval.update({"history": response})
    except queue.Empty:
        rval["status"] = "error"
        
    return rval


if __name__ == "__main__":
    APP.run(host="0.0.0.0", debug=True)