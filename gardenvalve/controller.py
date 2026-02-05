"""Runner for garden valve."""
import sys
import pathlib
import json
import sqlite3
import time
import datetime
import logging
import os
from configparser import ConfigParser
import argparse
from collections import deque
from pprint import pformat
import requests
from dotenv import load_dotenv
from base import LOGGER, CONFIGURATION_NAME, LOGGING_NAME

load_dotenv(override=True)


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def load_configuration():
    configuration_path = pathlib.Path(__file__).parent.joinpath(CONFIGURATION_NAME)
    with configuration_path.open("r") as fh:
        configuration = json.load(fh)
    LOGGER.debug(f"configuration -> {configuration}")
    return configuration


def calculate_rain_in_last_hours(dbpath, number_hours):
    connection = sqlite3.connect(dbpath, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    hours_before = time.time() - number_hours * 60 * 60
    cursor.execute(f"SELECT time, rain_mm FROM weather ORDER BY time DESC LIMIT 1")
    item_at_end = cursor.fetchone()
    item_at_end["time"] = datetime.datetime.fromtimestamp(item_at_end["time"])
    cursor.execute(f"SELECT time, rain_mm FROM weather WHERE time >= ? ORDER BY time ASC LIMIT 1", (hours_before, ))
    item_at_start = cursor.fetchone()
    item_at_start["time"] = datetime.datetime.fromtimestamp(item_at_start["time"])
    LOGGER.info(item_at_end)
    LOGGER.info(item_at_start)
    rain_mm = item_at_end["rain_mm"] - item_at_start["rain_mm"]
    return rain_mm
    
    
def run(configuration: dict, state: str) -> None:
    logfile = pathlib.Path(__file__).parent.joinpath(LOGGING_NAME)
    try:
        with logfile.open("r") as fh:
            logrecord = deque(json.load(fh), 10)
    except Exception:
        logrecord = deque(maxlen=10)
    
    now = datetime.datetime.now().isoformat()
    if state == "enable":
        # using a valve which is normally open
        valve_close = configuration["rain_mm"] > configuration["minimum_rain_amount_in_millimeters_for_valve_close"]
    else:
        valve_close = False
    
    url = "http://{0}/button/relais_{1}/press".format(os.environ["switchaddress"], "on" if valve_close else "off")
    r = requests.post(url)
    
    logrecord.appendleft(dict(close=valve_close, rain_mm=configuration["rain_mm"], time=now, status=r.status_code))
    with logfile.open("w") as fh:
        json.dump(list(logrecord), fh, indent=4)
    
        
def setup():
    configuration = load_configuration()

    path = os.environ["weatherstation"]
    assert path is not None, "ERROR: environment variable 'weatherstation' with path to weatherstation folder is missing "
    sys.path.insert(0, path)
    from common import DBPATH
    sys.path.pop()
    configuration["path_to_weatherstation_db"] = path
    configuration["rain_mm"] = calculate_rain_in_last_hours(DBPATH, configuration["calculate_rain_amount_over_hours"])
    
    return configuration
    

def write_systemctl_files(configuration):
    files = []
    contents = []
    contents.append("[Unit]")
    contents.append("Description=Timer for garden valve enable")
    contents.append("\n[Install]")
    contents.append("WantedBy=timers.target")
    contents.append("\n[Timer]")
    for on_run_time in configuration["on_run_times"]:
        contents.append("OnCalendar=*-*-* {0}:{1}:00".format(*on_run_time["on"].split(":")))
    contents.append("Unit=gardenvalve-enable.service")
    contents.append("Persistent=true")
    with open("gardenvalve-enable.timer", "w") as fh:
        fh.write("\n".join(contents))
    print(f"{fh.name} written")
    files.append(fh.name)
    
    contents = []
    contents.append("[Unit]")
    contents.append("Description=Timer for garden valve disable")
    contents.append("\n[Install]")
    contents.append("WantedBy=timers.target")
    contents.append("\n[Timer]")
    for on_run_time in configuration["on_run_times"]:
        hm = on_run_time["on"].split(":", maxsplit=1)
        on_time = datetime.datetime(year=2000, month=1, day=1, hour=int(hm[0]), minute=int(hm[1]))
        off_time = datetime.datetime.fromtimestamp(on_time.timestamp() + on_run_time["for"] * 60)
        contents.append("OnCalendar=*-*-* {0}:{1}:00".format(off_time.hour, off_time.minute))
    contents.append("Unit=gardenvalve-disable.service")
    contents.append("Persistent=true")
    with open("gardenvalve-disable.timer", "w") as fh:
        fh.write("\n".join(contents))
    print(f"{fh.name} written")
    files.append(fh.name)
        
    contents = []
    contents.append("[Unit]")
    contents.append("Description=Controller for garden valve enable")
    contents.append("\n[Service]")
    contents.append("WorkingDirectory={0}".format(str(pathlib.Path(__file__).parent)))
    contents.append("ExecStart=python3 {0} --state enable".format(str(pathlib.Path(__file__))))
    with open("gardenvalve-enable.service", "w") as fh:
        fh.write("\n".join(contents))
    print(f"{fh.name} written")
    files.append(fh.name)

    contents = []
    contents.append("[Unit]")
    contents.append("Description=Controller for garden valve disable")
    contents.append("\n[Service]")
    contents.append("WorkingDirectory={0}".format(str(pathlib.Path(__file__).parent)))
    contents.append("ExecStart=python3 {0} --state disable".format(str(pathlib.Path(__file__))))
    with open("gardenvalve-disable.service", "w") as fh:
        fh.write("\n".join(contents))
    print(f"{fh.name} written")
    files.append(fh.name)
    
    print("\nCopy the generated files to /etc/system/system")
    print("sudo cp {} /etc/systemd/system/".format(" ".join(files)))
    print("sudo systemctl daemon-reload")
    print("sudo systemctl start {}".format(" ".join(files)))
    print("sudo systemctl status gardenvalve-enable.timer gardenvalve-disable.timer gardenvalve-enable.service gardenvalve-disable.service")
    print("sudo systemctl enable {}".format(" ".join(files)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", dest="state", choices=["enable", "disable"], help="enable or disable valve")
    parser.add_argument("-w", "--write", action="store_true", help="write unit files for systemctl")
    args = parser.parse_args()
    configuration = setup()
    LOGGER.info(pformat(configuration))
    if args.write is True:
        write_systemctl_files(configuration)
    else:
        LOGGER.info(f"configuration -> {pformat(configuration)}")
        run(configuration, args.state)