import logging
import sqlite3
import argparse
import pathlib
import time
import json
import datetime
import requests
from dotenv import dotenv_values

loglevel = int(dotenv_values(".env").get("LOGLEVEL", logging.CRITICAL))
logging.basicConfig(format="%(levelname)s:%(asctime)s:%(lineno)d:%(message)s", level=loglevel)
LOGGER = logging.getLogger(__name__)

DEBUG = False
IPADDRESS = "192.168.178.137" 
DBNAME = "shelly2pm.db"
TABLENAME = "shelly2pm"
DBPATH = pathlib.Path("/opt/solvisheater/").joinpath(DBNAME)
DBFIELDS = dict(time="REAL", power="REAL", aenergy="REAL", state="INTEGER")
DBVALUES = ", ".join(f":{key}" for key in DBFIELDS)
DBCREATE = ", ".join(f"{key} {value}" for key, value in DBFIELDS.items())
POWER_DELTA = 100
TIME_DELTA = 1 * 60 if DEBUG else 10 * 60
TIME_INTERVAL = 10 if DEBUG else 60


def timestamp(datetimestr):
    return datetime.datetime.fromisoformat(datetimestr).timestamp()
    

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

        
def create_db(delete_db: bool):
    DBPATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(DBPATH)
    cursor = connection.cursor()
    if delete_db is True:
        command = f"DROP TABLE {TABLENAME}"
        LOGGER.critical(command)
        cursor.execute(command)
    command = f"CREATE TABLE {TABLENAME} ({DBCREATE})"
    LOGGER.critical(command)
    cursor.execute(command)
    # create trigger to delete items older than 1 year
    command = f"""CREATE TRIGGER IF NOT EXISTS deletelastyear AFTER INSERT ON {TABLENAME}
                   BEGIN
                   DELETE FROM {TABLENAME} WHERE (julianday('now') - julianday(time, 'unixepoch')) > 365;
                   END
                   """
    LOGGER.critical(command)
    cursor.execute(command)
    connection.commit()


def read_db():
    connection = sqlite3.connect(DBPATH, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = dict_factory
    cursor = connection.cursor()
        
    cursor.execute(f"SELECT * FROM {TABLENAME} ORDER BY time DESC")
    while True:
        item = cursor.fetchone()
        if item is None:
            break
        item["time"] = datetime.datetime.fromtimestamp(item["time"])
        print("|".join(f"{key}={item[key]}" for key in DBFIELDS))
        args.number -= 1
        if args.number == 0:
            break    
    connection.close()


def run():
    previous_state, previous_power, previous_time = None, -100, time.time() - 2 * TIME_DELTA
    url = f"http://{IPADDRESS}/rpc"
    payload = {"id":1,"method":"Shelly.GetStatus"}
    
    while True:
        r = requests.post(url, data=json.dumps(payload))
        r = r.json()
        r = r["result"]["switch:0"]
        data = dict(time=time.time(), state=r["output"], power=r["apower"], aenergy=r["aenergy"]["total"])
        LOGGER.debug(data)
        
        if previous_state != data["state"] or abs(data["power"] - previous_power) > POWER_DELTA or data["time"] - previous_time > TIME_DELTA:
            previous_state = data["state"]
            previous_power = data["power"]
            previous_time = data["time"]
            try:
                connection = sqlite3.connect(DBPATH)
                cursor = connection.cursor()
                LOGGER.info(f"{TABLENAME} -> {DBVALUES} -> {data}")
                cursor.execute(f"INSERT INTO {TABLENAME} VALUES({DBVALUES})", data)
                connection.commit()
            except Exception as e:
                LOGGER.critical(f"ERROR: {str(e)}")
        time.sleep(TIME_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["read", "run", "create"])
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("-n", "--number", type=int, default=0, action="store", help="show last number of items, default %(default)i (means all)")
    args = parser.parse_args()
    if args.command == "create":
        create_db(args.delete)
    elif args.command == "read":
        read_db()
    elif args.command == "run":
        run()