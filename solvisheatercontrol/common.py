import pathlib


def timestamp(datetimestr):
    return datetime.datetime.fromisoformat(datetimestr).timestamp()
    

DBNAME = "solvisheater.db"
TABLENAME = "solvisheater"
DBPATH = pathlib.Path.cwd().joinpath(DBNAME)
DBFIELDS = dict(time="REAL", power="REAL", aenergy="REAL", state="INTEGER")
DBVALUES = ", ".join(f":{key}" for key in DBFIELDS)
DBCREATE = ", ".join(f"{key} {value}" for key, value in DBFIELDS.items())


if __name__ == "__main__":
    print(f"DBNAME={DBNAME}")
    print(f"TABLENAME={TABLENAME}")
    print(f"DBPATH={DBPATH}")
    print(f"DBFIELDS={DBFIELDS}")
    print(f"DBVALUES={DBVALUES}")
    print(f"DBCREATE={DBCREATE}")
    