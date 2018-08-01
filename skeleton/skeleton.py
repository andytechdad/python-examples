# yum report
# parse a yum log for the most recent yum run.

import os
import sys
import argparse
import logging as log


def setup():
    parser = argparse.ArgumentParser(
        description=(
            'Script Title - Do things again and again',
            )
        )
    parser.add_argument('-f', '--file', type=str,
                        help='File, do we need a file?',
                        default='test.txt')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable Debug Logging')
    return parser.parse_args()


def get_logging_level(args):
    if args.debug is True:
        log_level = log.DEBUG
    else:
        log_level = log.INFO
    return log_level


# Add your functions here


def main(args):
    log_level = get_logging_level(args)
    date_format = "%Y-%m-%dT%H:%M:%S"
    FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
    log.basicConfig(stream=sys.stdout, level=log_level,
                    format=FORMAT, datefmt=date_format)
    log.info("starting Script...")
    # Main Program goes here, ideally using functions you've defined above
    return 1

if __name__ == "__main__":
    sys.exit(main(setup()))
