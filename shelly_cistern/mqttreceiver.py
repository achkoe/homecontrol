#!/usr/bin/env python3

import json
from datetime import datetime
import paho.mqtt.client as mqtt


BROKER = "192.168.178.114"
PORT = 1883

TOPIC = "shelly/cistern/events"


def on_connect(client, userdata, flags, rc):
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
    except Exception as e:
        print("ERROR:", e)


if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)

    client.loop_forever()
