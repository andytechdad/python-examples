# get the temprature

import os
import sys
import argparse
import logging as log
import requests
import json
import urllib3
import pprint
import time
import blinkt
from time import sleep

urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

hive_url = "https://api.prod.bgchprod.info:443/omnia"
blinkt.set_brightness(0.1)

def setup():
    parser = argparse.ArgumentParser(
        description=(
            'Hive CLI step 1 - login',
            )
        )
    parser.add_argument('-u', '--user', type=str,
                        help='Username',
                        required=True)
    parser.add_argument('-p', '--password', type=str,
                        help='password',
                        required=True)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable Debug Logging')
    return parser.parse_args()


def get_logging_level(args):
    if args.debug is True:
        log_level = log.DEBUG
    else:
        log_level = log.INFO
    return log_level

def get_auth(args):
    username = args.user
    password = args.password
    log.debug("Using credentials %s/XXXXXXXXXXX" % username)
    return username, password

def get_sessionID(hive_url, username, password):
    sessionID = []
    session_url = hive_url + "/auth/sessions"
    request_headers = {
                        'Content-Type': 'application/vnd.alertme.zoo-6.6+json',
                        'Accept': 'application/vnd.alertme.zoo-6.6+json',
                        'X-Omnia-Client': 'Python Hive CLI'
                        }
    request_json = {
                    "sessions": [{
                        "username" : username,
                        "password" : password,
                        "caller" : "WEB"
                    }]
                    }
    try:
        response = requests.post(session_url, data=json.dumps(request_json), headers=request_headers, verify=False)
        log.debug(response.status_code)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            sessionID = response_json['sessions'][0]['sessionId']
            log.debug(sessionID)
    except Exception as e:
        log.error(e)
    return sessionID

def get_nodes(hive_url, sessionID):
    nodes_url = hive_url + "/nodes"
    request_headers = {
                        'Content-Type': 'application/vnd.alertme.zoo-6.6+json',
                        'Accept': 'application/vnd.alertme.zoo-6.6+json',
                        'X-Omnia-Client': 'Python Hive CLI',
                        'X-Omnia-Access-Token': sessionID
                        }
    try:
        response = requests.get(nodes_url, headers=request_headers, verify=False)
        log.debug(response.status_code)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            nodes = response_json['nodes']
            node_index = 0
            for node in nodes:
                nodeType = nodes[node_index]['nodeType']
                if nodeType == "http://alertme.com/schema/json/node.class.thermostat.json#":
                    nodeID = nodes[node_index]['id']
                    nodeName = nodes[node_index]['name']
                    log.debug(nodeID)
                    log.debug(nodeName)
                    node_index = node_index + 1
                    get_nodeInfo(hive_url, sessionID, nodeID)
                else:
                    node_index = node_index + 1
        else:
            log.error("Bad HTTP Response Code")
    except Exception as e:
        log.error(e)
    return 1

def get_nodeInfo(hive_url, sessionID, nodeID):
    nodes_url = hive_url + "/nodes/" + nodeID
    request_headers = {
                        'Content-Type': 'application/vnd.alertme.zoo-6.6+json',
                        'Accept': 'application/vnd.alertme.zoo-6.6+json',
                        'X-Omnia-Client': 'Python Hive CLI',
                        'X-Omnia-Access-Token': sessionID
                        }
    try:
        response = requests.get(nodes_url, headers=request_headers, verify=False)
        log.debug(response.status_code)
        response_json = json.loads(response.text)
        jprint = pprint.PrettyPrinter(indent=4)
        jprint.pprint(response_json)
    except Exception as e:
        log.error(e)
    return 1

def get_channels(hive_url, sessionID):
    channels_url = hive_url + "/channels"
    request_headers = {
                        'Content-Type': 'application/vnd.alertme.zoo-6.6+json',
                        'Accept': 'application/vnd.alertme.zoo-6.6+json',
                        'X-Omnia-Client': 'Python Hive CLI',
                        'X-Omnia-Access-Token': sessionID
                        }
    try:
        response = requests.get(channels_url, headers=request_headers, verify=False)
        log.debug(response.status_code)
        response_json = json.loads(response.text)
        channels = response_json['channels']
        channel_index = 0
        for channel in channels:
            unit = channel['unit']
            if unit == "CELSIUS":
                id = channel['id']
                id_string = str(id)
                if id_string.startswith("temperature@"):
                    log.debug(id)
                    return id
            channel_index = channel_index + 1
    except Exception as e:
        log.error(e)
    return 1

def get_temperature(hive_url, sessionID, id):
    epoch = int(time.time())
    timestamp = epoch * 1000
    timenow = str(timestamp)
    epoch_past = int(time.time() - 240)
    timethen = str(epoch_past * 1000)

    log.debug(timenow)
    temperature_url = hive_url + "/channels/" + id + "?start=" + timethen + "&end=" + timenow + "&timeUnit=MINUTES&rate=1&operation=MAX"
    request_headers = {
                        'Content-Type': 'application/vnd.alertme.zoo-6.6+json',
                        'Accept': 'application/vnd.alertme.zoo-6.6+json',
                        'X-Omnia-Client': 'Python Hive CLI',
                        'X-Omnia-Access-Token': sessionID
                        }
    try:
        log.debug(temperature_url)
        response = requests.get(temperature_url, headers=request_headers, verify=False)
        log.debug(response.status_code)
        response_json = json.loads(response.text)
        if response_json.status_code == 200:
            channels = response_json['channels']
            channels_index = 0
            values = channels[channels_index]['values']
            temp_count = 0
            temperature = []
            while temp_count <= 0:
                for key, value in values.items():
                    log.debug(value)
                    temp_count = temp_count + 1
                    temperature = value
            log.debug("Found %s values" % temp_count)
            return temperature
        else:
            pass
    except Exception as e:
        log.error(e)
    return 1

def set_pixel(pixel, temperature):
    if temperature > 25:
        r = 255
        g = 0
        b = 0
    elif temperature > 22:
        r = 255
        g = 68
        b = 0
    elif temperature > 18:
        r = 255
        g = 145
        b = 0
    elif temperature > 15:
        r = 255
        g = 230
        b = 0
    elif temperature > 10:
        r = 0
        g = 230
        b = 255
    elif temperature > 6:
        r = 0
        g = 0
        b = 255
    else:
        r = 255
        g = 255
        b = 255
    log.debug(temperature)
    log.debug("RGB Value is %s %s %s" % (
    r,
    g,
    b
    ))
    blinkt.set_pixel(pixel, r, g, b)
    blinkt.show()
    return 1

def main(args):
    log_level = get_logging_level(args)
    date_format = "%Y-%m-%dT%H:%M:%S"
    FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
    log.basicConfig(stream=sys.stdout, level=log_level,
                    format=FORMAT, datefmt=date_format)
    log.info("Connecting to Hive....")
    while True:
        for pixel in range(8):
            username, password = get_auth(args)
            sessionID = get_sessionID(hive_url, username, password)
            log.debug("Setting Pixel %s " % pixel)
            id = get_channels(hive_url, sessionID)
            temperature = get_temperature(hive_url, sessionID, id)
            log.info("The House Temperature is %s " % temperature)
            set_pixel(pixel, temperature)
    return 1

if __name__ == "__main__":
    sys.exit(main(setup()))
