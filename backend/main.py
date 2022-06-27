import paho.mqtt.client as mqtt
from datetime import datetime
import time

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

client = mqtt.Client()
client.on_connect = on_connect

client.connect("localhost", 1883)

client.loop_start()

while True:
    now = datetime.now().isoformat()
    print(f"publishing: {now}")
    client.publish("time", now)
    time.sleep(1)
