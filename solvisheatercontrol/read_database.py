"""Read data from sqlite3 database."""
import sqlite3
import datetime
import argparse
from common import DBPATH, DBFIELDS


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


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
