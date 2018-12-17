import os
import sys
import shutil
import argparse
import json
import logging as log
import requests

from requests import Session
from requests.auth import HTTPBasicAuth

def setup():
    parser = argparse.ArgumentParser(
        description=(
            'Nexus REST asset list using continuation token',
            )
        )
    parser.add_argument('-n', '--nexus', type=str,
                        help='Nexus Hostname',
                        default='nexus')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable Debug Logging')
    return parser.parse_args()


def get_logging_level(args):
    if args.debug is True:
        log_level = log.DEBUG
    else:
        log_level = log.INFO
    return log_level


def get_nexus(args):
    nexus = args.nexus
    log.debug("Nexus Hostname is %s" % nexus)
    repository = "Software"
    rest_api = "/service/rest/"
    api_ver = "v1"
    nexus_url = "http://" + nexus + ":8081" + rest_api + api_ver + "/"
    log.debug("Nexus Rest Base URL is %s" % nexus_url)
    return nexus_url


def check_nexus(nexus_url):
    repository = "Software"
    url_check = nexus_url + "repositories"
    log.debug("HTTP Header Check on Nexus endpoint to check Nexus is up")
    try:
        nexus_check = requests.head(url_check)
        log.debug("Quick HTTP Header check on %s" % nexus_check)
        log.debug(nexus_check.status_code)
        if nexus_check.status_code == 200:
            log.info("....PASSED")
        else:
            log.error("Cannot Find Nexus API....exiting")
            sys.exit(1)
    except requests.exceptions.RequestException as requests_error:
        log.error(requests_error)
        sys.exit(1)
    return nexus_check.status_code


def nexus_opening_request(nexus_url):
    log.debug("Make initial call to list assets")
    log.debug("We except some Assets and a continuation token")
    repository = "Nexus"
    assets_url = nexus_url + "assets?repository=" + repository
    log.debug("Making call to %s" % assets_url)
    try:
        asset_response = requests.get(assets_url)
        log.debug(asset_response.status_code)
        if asset_response.status_code == 200:
            assets_to_parse = json.loads(asset_response.text)
            continuation_token = []
            if assets_to_parse['continuationToken'] is not None:
                continuation_token = assets_to_parse['continuationToken']
                log.debug("Continuation Token %s found, make another call" %
                          continuation_token)
                #make another call with the continuation token
            else:
                #return what we have
                return return_values
        else:
            log.warn("Did not get expected HTTP 200 response")
    except requests.exceptions.RequestException as requests_error:
        log.error(requests_error)
        sys.exit(1)
    return_values = ()
    return return_values


def nexus_continuation_request(nexus_url, continuation_token):
    log.debug("Making a continuation Call")
    log.debug("we except some Assets and a continuation token")
    repository = "Software"
    continuation_url = "assets?continuationToken=" + continuation_token
    reposisotry_url = "&repository=" + repository
    assets_url = nexus_url + continuation_url + reposisotry_url
    log.debug("Making call to %s" % assets_url)
    try:
        asset_response = requests.get(assets_url)
        log.debug(asset_response.status_code)
        if asset_response.status_code == 200:
            # do stuff here with the json response
            continuation_token = []
            if assets_to_parse['continuationToken'] is not None:
                continuation_token = assets_to_parse['continuationToken']
                log.debug("Continuation Token %s found, make another call" %
                          continuation_token)
                # make another call with the continuation token
            else:
                # return everything you have
                return return_values
        else:
            log.warn("Did not get expected HTTP 200 response")
    except requests.exceptions.RequestException as requests_error:
        log.error(requests_error)
        sys.exit(1)
    return_values = ()
    return return_values

def main(args):
    log_level = get_logging_level(args)
    date_format = "%Y-%m-%dT%H:%M:%S"
    FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
    log.basicConfig(stream=sys.stdout, level=log_level,
                    format=FORMAT, datefmt=date_format)
    log.info("Starting Nexus API script")
    nexus_url = get_nexus(args)
    nexus_api_check = check_nexus(nexus_url)
    if nexus_api_check == 200:
        log.info("Calling NEXUS API URL")
        # make your opening request here
    return 0


if __name__ == "__main__":
    sys.exit(main(setup()))
