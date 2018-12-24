# login example for bg hive

import os
import sys
import argparse
import logging as log
import requests
import json



hive_url = "https://api.prod.bgchprod.info:443/omnia"

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
    session_url = hive_url + "/auth/sessions"
    request_json = {
                    "sessions": [{
                        "username" : username,
                        "password" : password,
                        "caller" : "WEB"
                    }]
                    }
    try:
        response = requests.post(session_url, data=json.dumps(request_json), headers={'Content-Type': 'application/vnd.alertme.zoo-6.6+json', 'Accept': 'application/vnd.alertme.zoo-6.6+json', 'X-Omnia-Client': 'Python Hive CLI'}, verify=False )
        log.debug(response.text)
    except Exception as e:
        log.error(e)
    return 1

def main(args):
    log_level = get_logging_level(args)
    date_format = "%Y-%m-%dT%H:%M:%S"
    FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
    log.basicConfig(stream=sys.stdout, level=log_level,
                    format=FORMAT, datefmt=date_format)
    log.info("starting Script...")
    username, password = get_auth(args)
    get_sessionID(hive_url, username, password)
    return 1

if __name__ == "__main__":
    sys.exit(main(setup()))
