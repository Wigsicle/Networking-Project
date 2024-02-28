import paho.mqtt.client as mqtt

# MQTT broker details
broker_address = "homeassistant.local"
port = 1883
username = "richard"
password = "LogitechG430"

# Callback function to handle incoming messages
def on_publish(client, userdata, result):
    print("Message published!")

# Create MQTT client instance
client = mqtt.Client()

# Set credentials if MQTT broker requires authentication
client.username_pw_set(username, password)

# Assign the on_publish callback function
client.on_publish = on_publish

# Connect to the MQTT broker
client.connect(broker_address, port)

# Publish a message to a topic
topic = "iot/doorbell/state"
message = 1
client.publish(topic, message)

# Disconnect from the broker
client.disconnect()
