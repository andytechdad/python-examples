#!/usr/bin/python3
## Upcoming Expirations
## Polls the django_ca api and checks expiration dates for anything within 30 days
## Sends alerts to slack
## Designed to be run once a day.

import argparse
import json
import requests
import sys
import datetime

def setup():
    parser = argparse.ArgumentParser(
        description=(
            'Django CA Certificate Expiry Checking Tool',
        )
    )
    parser.add_argument('-c', '--casigner', type=str,
                        help='URL for CA Signer API in JSON format',
                        required=True)
    parser.add_argument('-d', '--days', type=int,
                        help='Number of Days to check',
                        default='30')
    parser.add_argument('-s', '--slack', type=str,
                        help='Slack Channel for Notifications: NOT IN USE YET')
    return parser.parse_args()

def read_api(args):
    django_ca = args.casigner
    response = requests.get(django_ca).text
    return response

def get_expiry_date(args):
    days = args.days
    today = datetime.datetime.now().replace(microsecond=0)
    expiry_date = str(today + datetime.timedelta(days=days))
    return expiry_date

# post_alert should need server, expiry_date and slack url as optional, defaulted to dev
def post_alert_critical(server, expiry_date, webhook_url='https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXX'):
    http_proxy = {'http' : 'http://proxy:80',
           'https': 'http://proxy:80'}
    slack_data = {
       "attachments":[
          {
             "fallback":"CRITICAL CERTIFICATE EXPIRED [Urgent]: <https://casigner.domain.local/admin/|CA>",
             "pretext":"CRITICAL CERTIFICATE EXPIRED [Urgent]: <https://casigner.domain.local/admin/|CA>",
             "color":"#D00000",
             "fields":[
                {
                   "title": "%s expired on %s" % (server, expiry_date),
                }
             ]
          }
       ]
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data), proxies=http_proxy, headers={'Content-Type': 'application/json'}, verify=False)
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    return

def post_alert_upcoming(server, expiry_date, webhook_url='https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXX'):
    http_proxy = {'http' : 'http://proxy:80',
           'https': 'http://proxy:80'}
    slack_data = {
       "attachments":[
          {
             "fallback":"WARNING CERTIFICATE EXPIRY [Urgent]: <https://casigner.domain.local/admin/|CA>",
             "pretext":"WARNING CERTIFICATE EXPIRY [Urgent]: <https://casigner.domain.local/admin/|CA>",
             "color":"#FFBF00",
             "fields":[
                {
                   "title": "%s expires on %s" % (server, expiry_date),
                }
             ]
          }
       ]
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data), proxies=http_proxy, headers={'Content-Type': 'application/json'}, verify=False)
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    return

def main(args):
    expiry_date = get_expiry_date(args)[:10]
    http_response = read_api(args)
    payload = json.loads(http_response)
    for certificate in payload:
        cert_check = certificate['expires'][:10]
        server = certificate['cn']
        cert_datetime = datetime.datetime.strptime(cert_check, '%Y-%m-%d')
        expiry_deadline = datetime.datetime.strptime(expiry_date, '%Y-%m-%d')
        critical_deadline = datetime.datetime.now().replace(microsecond=0)
        if cert_datetime <= critical_deadline:
          post_alert_critical(server, cert_datetime)
          #post_alert_critical_teams(server, cert_datetime)
        if cert_datetime <= expiry_deadline:
          post_alert_upcoming(server, cert_datetime)
          #post_alert_upcoming_teams(server, cert_datetime)
        else:
          print("{}: Cerificate expires on {}. Not within 30 day limit of {} times.".format(server, cert_datetime, expiry_deadline))
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(setup()))
