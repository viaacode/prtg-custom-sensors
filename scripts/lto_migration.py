import json
import math
import requests
from datetime import datetime


def last_migration_event_delta():
    res = requests.get(
        "https://lto-migration-status-prd-meemoo-infra.private.cloud.meemoo.be/"
    )
    migration_event_date = datetime.strptime(
        res.json(), "%Y-%m-%dT%H:%M:%S.%f")
    now = datetime.now()
    time_delta = now - migration_event_date
    time_delta_hours = divmod(time_delta.total_seconds(), 3600)[0]

    return time_delta_hours


def sensor():
    return {
        "prtg": {
            "result": [
                {
                    "channel": "LTO migration",
                    "value": int(math.floor(last_migration_event_delta())),
                },
            ]
        }
    }


if __name__ == "__main__":
    print(json.dumps(sensor()))

