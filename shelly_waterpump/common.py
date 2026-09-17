import pathlib

DBNAME = "cistern.db"
DBPATH = pathlib.Path().joinpath("/", "opt", "cistern", DBNAME)
DBFIELDS = dict(time="REAL", power="REAL")
DBVALUES = ", ".join(f":{key}" for key in DBFIELDS)
VERSION = "0.9.0"