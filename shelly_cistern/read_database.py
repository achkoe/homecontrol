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
    
    index = 0
    
    cursor.execute("SELECT * FROM power ORDER BY time DESC")
    while True:
        item = cursor.fetchone()
        if item is None:
            break
        item["i"] = index
        index += 1
        item["time"] = datetime.datetime.fromtimestamp(item["time"])
        print("|".join(f"{key}={item[key]}" for key in item))
        args.number -= 1
        if args.number == 0:
            break

    rlist = []
    elist = []
    plimit = 50
    index = 0
    ison = False

    cursor.execute("SELECT * FROM power ORDER BY time ASC")
    while True:
        item = cursor.fetchone()
        if item is None:
            break
        elist.append(item)
        if item["power"] > plimit and ison is False:
            tstart = item["time"]
            istart = index
            ison = True
        if item["power"] < plimit:
            rlist.append((item["time"] - tstart, istart))   
            ison = False
        index += 1
        
    rlist.sort(key=lambda x: x[0])
    
    for index, item in enumerate(elist):
        item["time"] = datetime.datetime.fromtimestamp(item["time"])
        print("{0:3} | {1} | {2:5.1f}".format(index, item["time"], item["power"]))
        
    for index in range(3):
        print("{1} -> {0}".format(*rlist[-index]))
        
    maxtime = rlist[-1]
    print(f"Maximum on time is {maxtime[0]} seconds, {maxtime[0] / 60} minutes (at index {maxtime[1]})")