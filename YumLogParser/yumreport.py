# yum report
# parse a yum log for the most recent yum run, and log to Staging server for future parsing

import os
import sys
import argparse
import logging as log
import re
from datetime import datetime

def setup():
    parser = argparse.ArgumentParser(
        description=(
            'Yum Report Log Parser',
        )
    )
    parser.add_argument('-l', '--log', type=str,
                help='Yum Log, defaults to /var/log/yum.log',
                default='/var/log/yum.log')
    parser.add_argument('-d', '--debug', action='store_true',
                help='Enable Debug Logging')
    return parser.parse_args()

def get_logging_level(args):
    if args.debug == True:
        log_level = log.DEBUG
    else:
        log_level = log.INFO
    return log_level

def get_log_file(args):
    yum_log = args.log
    log.debug("Yum Log file is: %s" % yum_log)
    return yum_log

def parse_line_for_date(line):
    log.debug("[PARSER]:%s" % line)
    date_obj = re.match(r"[ADFJMNOS]\w* [\d]{1,2}", line)
    if date_obj is not None:
        date = line[:6]
        log.debug("Date found: %s" % date)
    else:
        log.debug("No date found in line")
    return date

def convert_date_to_obj(date):
    date_obj = datetime.strptime(date, '%b %d')
    log.debug("Date Object: %s" % date_obj)
    return date_obj

def find_last_run(yum_log):
    with open(yum_log,"r") as loaded_log:
        log_lines = loaded_log.readlines()
        last_line = log_lines[len(log_lines)-1]
        log.debug("Last Line is: %s" % last_line)
        last_run = parse_line_for_date(last_line)
        log.info("Date of last yum update run is %s" % last_run)
        last_run_obj = datetime.strptime(last_run, '%b %d')
        log.debug("Datetime object: %s" % last_run_obj)
    return last_run_obj

def read_yum_log(yum_log):
    if os.path.isfile(yum_log):
        log.info("Parsing yum log file: %s" % yum_log)
        last_run = find_last_run(yum_log)
        packages_installed = []
        try:
            for line in reversed(open(yum_log).readlines()):
                date = parse_line_for_date(line)
                date_obj = convert_date_to_obj(date)
                if date_obj == last_run:
                    packages_installed.append(line)
            log.info("Packages: %s" % packages_installed)
        except IOError:
            log.error("ERROR")
    else:
        log.error("Cannot find log file...exiting")
        sys.exit(1)

def main(args):
    log_level = get_logging_level(args)
    FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
    log.basicConfig(stream=sys.stdout, level=log_level, format=FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
    log.info("starting Yum Report Log Parser...")
    yum_log = get_log_file(args)
    read_yum_log(yum_log)
    return 1

if __name__ == "__main__":
    sys.exit(main(setup()))
