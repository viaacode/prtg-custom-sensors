#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 09:46:57 2023

Attention:
  - credentials supplied via PRTG interface
    'client_id, client_secret, username, password, endpoint_mh' 
  - requires meemoo python mediahaven module
    install with pipfile line :
      mediahaven = {editable = true, ref = "6abd66de7a919cf76c944122b14f53ea29e6e16a", git = "git+https://github.com/viaacode/mediahaven-python"}

@author: tina
updated to Script V2 Sensor by roel (original script in python/)
"""

from mediahaven import MediaHaven
from mediahaven.oauth2 import ROPCGrant, RequestTokenError
import json
from sys import stdin


def report_and_exit(message, status, channels=[]):
    result = {
        "version": 2,
        "status": status,
        "message": message,
    }
    if status == "ok":
        id = 0
        result["channels"] = []
        for ch in channels:
            id += 10
            ch["id"] = id
            ch["type"] = "integer"
            result["channels"].append(ch)

    print(json.dumps(result))
    exit()


def mh_client(client_id, client_secret, username, password, url):
    # Create a ROPC grant
    grant = ROPCGrant(url, client_id, client_secret)
    # Request a token
    try:
        grant.request_token(username, password)
    except RequestTokenError as e:
        print(e)

    # Initialize the MH client
    return MediaHaven(url, grant)


def sensor_channels(client):
    def count_in_progress():
        query = "ArchiveStatus:in_progress"
        records_page = client.records.count(query=f"+({query})")
        return int(records_page)

    def complex_in_progress():
        complex_q = "ArchiveStatus:in_progress AND originalFileName:*.complex"
        records_page = client.records.count(query=f"+({complex_q})")
        return int(records_page)

    def gazetten_in_progress():
        complex_q = "+(RecordType:Newspaper) +(RecordStatus:processing) +(IsInIngestspace:1)"
        records_page = client.records.count(query=f"+({complex_q})")
        return int(records_page)

    def material_artwork_in_progress():
        complex_q = "+(RecordType:MaterialArtwork) +(RecordStatus:processing) +(IsInIngestspace:1)"
        records_page = client.records.count(query=f"+({complex_q})")
        return int(records_page)

    channels = []
    channels.append(
        {
            "name": "In progress",
            "value": count_in_progress(),
        }
    )
    channels.append(
        {
            "name": "Complex in progress",
            "value": complex_in_progress(),
        }
    )
    channels.append(
        {
            "name": "Gazetten in progress",
            "value": gazetten_in_progress(),
        }
    )
    channels.append(
        {
            "name": "Material artwork in progress",
            "value": material_artwork_in_progress(),
        }
    )

    return channels


if __name__ == "__main__":
    params = stdin.readline().rstrip().split(",")
    client_id, client_secret, username, password, endpoint_mh = params

    url = f"https://{endpoint_mh}/mediahaven-rest-api/v2/records"
    client = mh_client(client_id, client_secret, username, password, url)

    channels = sensor_channels(client)

    report_and_exit("mh_inprogress", "ok", channels)
