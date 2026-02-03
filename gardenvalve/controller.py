import sys
import pathlib
import json
import sqlite3
import time
import datetime


CONFIGURATION_NAME = "configuration.json"


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def _make_integer_time(timestr: str) -> int:
    hms = (int(item) for item in timestr.split(":"))
    rval = 0
    for item, factor in zip(hms, (60 * 60, 60, 1)):
        rval += item * factor
    return rval


def load_configuration():
    configuration_path = pathlib.Path(__file__).parent.joinpath(CONFIGURATION_NAME)
    with configuration_path.open("r") as fh:
        configuration = json.load(fh)
    for index, on_off_time in enumerate(configuration["on_off_times"]):
        for key in ["on", "off"]:
            the_time = on_off_time[key]
            configuration["on_off_times"][index][f"{key}_i"] = _make_integer_time(the_time)
    print(configuration)
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
    print(item_at_end)
    print(item_at_start)
    rain_mm = item_at_end["rain_mm"] - item_at_start["rain_mm"]
    return rain_mm
    
    
def run():
    configuration = load_configuration()
    sys.path.append(configuration["path_to_weatherstation"])
    from common import DBPATH
    sys.path.pop()
    rain_mm = calculate_rain_in_last_hours(DBPATH, configuration["calculate_rain_amount_over_hours"])
    print(rain_mm)
    
    while True:
        time_struct = time.localtime()
        current_time = time_struct.tm_hour * 60 * 60 + time_struct.tm_min * 60 + time_struct.tm_sec
        for index, on_off_time in enumerate(configuration["on_off_times"]):
            on_i = on_off_time["on_i"]
            off_i = on_off_time["off_i"]
            invert = on_i > off_i
            if invert:
                on_i, off_i = off_i, on_i
            switch_on = invert ^ (current_time >= on_i and current_time <= off_i)
            
            print(f"{index} -> {switch_on}")

        time.sleep(10)    
        

    
if __name__ == "__main__":
    run()