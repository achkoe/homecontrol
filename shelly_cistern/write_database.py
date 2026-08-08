#!/usr/bin/env python3

import sqlite3
from types import SimpleNamespace
import json
from datetime import datetime
import paho.mqtt.enums as enums
import paho.mqtt.client as mqtt
from common import DBPATH, DBFIELDS, DBVALUES
from sendemail import email


BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "shelly/cistern/events"


def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("MQTT connected")
        client.subscribe(TOPIC)
    else:
        print("MQTT error:", rc)


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        timestamp = datetime.fromtimestamp(data["timestamp"])
        print(
            f"{timestamp:%Y-%m-%d %H:%M:%S} | "
            f"{data['device']:20s} | "
            f"{data['event']:10s} | "
            f"{data['power']:7.1f} W | "
            f"Threshold {data['threshold']} W"
        )
        userdata.cursor.execute("INSERT OR IGNORE INTO power VALUES (?, ?)", (data["timestamp"], data["power"]))
        userdata.connection.commit()
        
        if data['event'] == "disable":
            subject = "Warning: water pump disabled"
            message = f"Water pump disabled at {timestamp:%Y-%m-%d %H:%M:%S}.\n" \
                "Check all outlets!\n" \
                "Unplug and plug Shelly Plug to enable it again.\n"
            email(subject, message)
    except Exception as e:
        print("ERROR:", e)


if __name__ == '__main__':
    connection = sqlite3.connect(DBPATH, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    s = ",".join(f"{key} {DBFIELDS[key]}" for key in DBFIELDS)    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS power ({s})")
    s = ",".join(DBFIELDS)
    # avoid writing duplicate items
    cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS uniquedata ON power ({s})")
    # create trigger to delete items older than 1 year
    cursor.execute("""CREATE TRIGGER IF NOT EXISTS deletelastyear AFTER INSERT ON power
                   BEGIN
                   DELETE FROM power WHERE (julianday('now') - julianday(time, 'unixepoch')) > 365;
                   END
                   """)
    connection.commit()
    
    # --- MQTT stuff ---
    userdata = SimpleNamespace(cursor=cursor, connection=connection)
    client = mqtt.Client(enums.CallbackAPIVersion(2), userdata=userdata) 
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()
