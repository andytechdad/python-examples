import os
from requests import Session
from requests.auth import HTTPBasicAuth
import shutil
import argparse
import sys
import logging as log


def setup():
    parser = argparse.ArgumentParser(
        description=(
            'Nexus Uploader - Upload a file to Nexus Repository Manager',
        )
    )
    parser.add_argument('-f', '--file', type=str,
                        help='File to upload',
                        required=True)
    parser.add_argument('-p', '--path', type=str,
                        help='Path/Project folder for the file',
                        required=True)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable Debug Logging')
    return parser.parse_args()


def get_logging_level(args):
    if args.verbose is True:
        log_level = log.DEBUG
    else:
        log_level = log.INFO
    return log_level


def get_file(args):
    file = args.file
    log.debug("File to upload is %s, checking local file system" % file)
    if os.path.isfile(file):
        log.info("File: %s found." % file)
        full_path = os.path.abspath(file)
        log.debug("Asbolute Path is %s" % full_path)
        file_name = os.path.basename(full_path)
        log.debug("File Name is %s" % file_name)
    else:
        log.error("Cannot find file....exiting")
        sys.exit(1)
    return file, file_name


def get_path(args):
    path = args.path
    log.debug("Nexus Folder is %s" % path)
    return path


def build_nexus_remote_path(path, file_name):
    nexus_host = "http://nexus:8081"
    nexus_repo = "SampleRepository"
    nexus = nexus_host + "/repository/" + nexus_repo
    remote_path = nexus + "/" + path + "/" + file_name
    log.debug("Full path to upload is %s" % remote_path)
    return remote_path


def uploader(file, remote_path):
    session = Session()
    session.auth = HTTPBasicAuth('admin', 'admin')
    if os.path.isfile(file):
        try:
            log.info("Uploading file %s to %s" % (
                    file,
                    remote_path,
                    ))
            with open(file, 'rb') as nexus_src:
                payload = session.put(remote_path, data=nexus_src)
                log.debug(payload)
                if payload.status_code == 201:
                    log.info("....Upload Sucessful")
                else:
                    log.warning("Something went wrong")
        except requests.exceptions.RequestException as requests_error:
            log.error(requests_error)
            sys.exit(1)
    return 1


def main(args):
    log_level = get_logging_level(args)
    date_format = "%Y-%m-%dT%H:%M:%S"
    FORMAT = "[%(levelname)s] %(asctime)s - %(message)s"
    log.basicConfig(stream=sys.stdout, level=log_level,
                    format=FORMAT, datefmt=date_format)
    log.info("Starting Nexus Uploader....")
    file, file_name = get_file(args)
    path = get_path(args)
    remote_path = build_nexus_remote_path(path, file_name)
    uploader(file, remote_path)
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main(setup()))
