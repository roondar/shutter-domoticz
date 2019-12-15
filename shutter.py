#! /usr/bin/env python
import paho.mqtt.client as mqtt
import json
import logging
import yaml

stream = open('shutter.yml', 'r')
config = yaml.safe_load(stream)

logging.basicConfig(level=logging.INFO, format=config['logging']['format'])

mqtt_server = config['mqtt']['host']
mqtt_port = config['mqtt']['port']

for s in config['shutters']:
    shutter_name, shutter_idx = next(iter(s.items()))

SHUTTER_CLOSE_STATE = config['shutter_state']['SHUTTER_CLOSE_STATE']
SHUTTER_OPEN_STATE = config['shutter_state']['SHUTTER_OPEN_STATE']
SHUTTER_CUSTOM_STATE = config['shutter_state']['SHUTTER_CUSTOM_STATE']

sensor_name = config['tasmota']['sensor_name']

client = mqtt.Client()
logger = logging.getLogger(__name__)
client.enable_logger(logger)
publish_topic = f'cmnd/{shutter_name}/shutterposition'


def on_connect(client, userdata, flags, rc):
    client.subscribe(f"+/{shutter_name}/RESULT")
    client.subscribe(config['topics']['domoticz_out'])


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf8"))
    if msg.topic == config['topics']['domoticz_out'] and data['idx'] == shutter_idx:
        nvalue = data['nvalue']
        svalue = data['svalue1']
        if nvalue == SHUTTER_OPEN_STATE:
            logger.info(f"We opening shutter {shutter_name}")
            client.publish(publish_topic, '100')
        elif nvalue == SHUTTER_CLOSE_STATE:
            logger.info(f"We closing shutter {shutter_name}")
            client.publish(publish_topic, '0')
        elif nvalue == SHUTTER_CUSTOM_STATE:
            logger.info(f"We moving shutter {shutter_name} to position {svalue}")
            client.publish(publish_topic, svalue)

    elif shutter_name in msg.topic and sensor_name in data:
        position = str(data[sensor_name]['Position'])
        logger.info(f"My current position is {position}")
        if position == "100":
            payload = {"idx": shutter_idx, "nvalue": SHUTTER_OPEN_STATE, "svalue": position}
        elif position == "0":
            payload = {"idx": shutter_idx, "nvalue": SHUTTER_CLOSE_STATE, "svalue": position}
        else:
            payload = {"idx": shutter_idx, "nvalue": SHUTTER_CUSTOM_STATE, "svalue": position}
        client.publish(config['topics']['domoticz_in'], json.dumps(payload))


client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_server, mqtt_port, 60)

client.loop_forever()
