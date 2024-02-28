import paho.mqtt.client as mqtt

# MQTT broker details
broker_address = "homeassistant.local"
port = 1883
username = "richard"
password = "LogitechG430"

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    print("Payload:", str(message.payload.decode("utf-8")))

# Create MQTT client instance
client = mqtt.Client()

# Set credentials if MQTT broker requires authentication
client.username_pw_set(username, password)

# Assign the on_message callback function
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, port)

# Subscribe to a topic
topic = "iot/doorbell/state"
client.subscribe(topic)

# Loop to maintain network traffic flow
client.loop_forever()