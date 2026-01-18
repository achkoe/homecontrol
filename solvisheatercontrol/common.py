import pathlib


def timestamp(datetimestr):
    return datetime.datetime.fromisoformat(datetimestr).timestamp()
    

DBNAME = "solvisheater.db"
DBPATH = pathlib.Path.cwd().joinpath(DBNAME)
DBFIELDS = dict(time="REAL", power="REAL")
DBVALUES = ", ".join(f":{key}" for key in DBFIELDS)
