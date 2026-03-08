import sqlite3
import argparse
from common import DBPATH, DBFIELDS, TABLENAME, DBCREATE


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store_true", help="delete before create")
    args = parser.parse_args()
    connection = sqlite3.connect(DBPATH)
    cursor = connection.cursor()
    if args.d is True:
        command = f"DROP TABLE {TABLENAME}"
        print(command)
        cursor.execute(command)
    command = f"CREATE TABLE {TABLENAME} ({DBCREATE})"
    print(command)
    cursor.execute(command)
    connection.commit()
        
