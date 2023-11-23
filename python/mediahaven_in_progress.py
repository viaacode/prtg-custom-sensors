#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 09:46:57 2023

Attention:
  - Add credentials before adding thisto prtg server custom sensors dir
  - requires meemoo python mediahaven module
    - install with requirements.txt line :
        - mediahaven @ git+https://github.com/viaacode/mediahaven-python@1ac5a9c5463d7c565b01943d5b73713818c164d6
@author: tina
"""

from mediahaven import MediaHaven
from mediahaven.oauth2 import ROPCGrant, RequestTokenError
import json

CLIENT_ID = "____"
CLIENT_SECRET = "____"
USERNAME = "moo@larry"
PASSWORD = "____"
MH_URL = "https://endpoint.mh/mediahaven-rest-api/v2/records"

# Get the credentials from env vars.
client_id = CLIENT_ID
client_secret = CLIENT_SECRET
username = USERNAME
password = PASSWORD
url = MH_URL

# Create a ROPC grant
grant = ROPCGrant(url, client_id, client_secret)
# Request a token
try:
    grant.request_token(username, password)
except RequestTokenError as e:
    print(e)

# Initialize the MH client
client = MediaHaven(url, grant)

# Get page based on query


def in_progress():
    records_page = client.records.search(
        q="+(MediaObjectArchiveStatus:in_progress)", nrOfResults=1, startIndex=0
    )
    return records_page.total_nr_of_results


def complex_in_progress():
    complex_q = (
        "MediaObjectArchiveStatus:in_progress AND originalFileName:*.complex"
    )
    records_page = client.records.search(
        q=f"+({complex_q})", nrOfResults=1, startIndex=0
    )
    return records_page.total_nr_of_results


def gazetten_in_progress():
    complex_q = "+(RecordType:Newspaper) +(RecordStatus:processing) +(IsInIngestspace:1)"
    records_page = client.records.search(
        q=f"+({complex_q})", nrOfResults=1, startIndex=0
    )
    return records_page.total_nr_of_results


def sensor():
    return {
        "prtg": {
            "result": [
                {"channel": "In progress", "value": int(in_progress())},
                {
                    "channel": "Complex in progress",
                    "value": int(complex_in_progress()),
                },
                {
                    "channel": "Gazetten in progress",
                    "value": int(gazetten_in_progress()),
                },
            ]
        }
    }


if __name__ == "__main__":
    print(json.dumps(sensor()))
