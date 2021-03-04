from time import sleep

from paho.mqtt.client import Client

from src.database import Database

sleep(1)
db = Database()
# TODO:Add Code

mqtt_client = Client(client_id = "User Service")
mqtt_client.subscribe("topic")

if __name__ == '__main__':
    mqtt_client.connect("mqtt", 1883)
