"""Read data from sqlite3 database."""
import sqlite3
import datetime
import argparse
from common import DBPATH, DBFIELDS


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def powerperday(cursor):
    cursor.execute("SELECT * FROM heater ORDER BY time ASC")
    item = cursor.fetchone()
    if item is None:
        return  # FIXME
    previous_time = item["time"]
    item["time"] = datetime.datetime.fromtimestamp(item["time"])
    previous_day = item["time"].day
    previous_month = item["time"].month
    previous_year = item["time"].year
    power = abs(item["power"])
    work = 0.0
        
    while True:
        item = cursor.fetchone()
        if item is None:
            break
        current_time = item["time"]        
        if 0:
            print(f"{current_time:11.7f} | {previous_time:11.7f} | {(current_time - previous_time):6.1f} | {power}")
        work += (current_time - previous_time) * power / (1000 * 60 * 60)
        power = abs(item["power"])
        previous_time = current_time
        
        item["time"] = datetime.datetime.fromtimestamp(item["time"])
        day = item["time"].day
        month = item["time"].month
        year = item["time"].year
        if day != previous_day or month != previous_month or year != previous_year:
            previous_day = day
            previous_month = month
            previous_year = year
            print(f"{previous_year}-{previous_month}-{previous_day} -> {work}")
            work = 0.0
        
    print(f"{previous_year}-{previous_month}-{previous_day} -> {work} kWh")
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--number", type=int, default=0, action="store", help="show last number of items, default %(default)i (means all)")
    args = parser.parse_args()
    connection = sqlite3.connect(DBPATH, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = dict_factory
    cursor = connection.cursor()
        
    cursor.execute("SELECT * FROM heater ORDER BY time DESC")
    while True:
        item = cursor.fetchone()
        if item is None:
            break
        item["time"] = datetime.datetime.fromtimestamp(item["time"])
        print("|".join(f"{key}={item[key]}" for key in DBFIELDS))
        args.number -= 1
        if args.number == 0:
            break

    powerperday(cursor)
    
    connection.close()