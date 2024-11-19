"""
This script generates random data every five seconds for all rooms received
from the storm app.
"""

import os
import sys
import select
import random
from datetime import datetime, timezone, timedelta
import requests
from dotenv import load_dotenv


def update_people(pp, time) -> dict:
    """
    Generates random people values from a given room.

    Args:
        pp (int): Current people value.
        time (datetime.datetime): Current timestamp.

    Returns:
        dict: one to three new people values.
    """
    people = {}

    people["time"] = (
        time - timedelta(seconds=random.randint(1, DATAGEN_TIME))
    ).strftime("%Y-%m-%dT%H:%M:%S%z")

    np = random.choices(
        population=[-3, -2, -1, 0, 1, 2, 3], weights=[1, 2, 3, 5, 3, 2, 1]
    )[0]

    people["value"] = 0 if np + pp < 0 else 30 if np + pp > 30 else np + pp

    return people


def update_co2(cc, time) -> dict:
    """
    Generates random co2 values from a given room.

    Args:
        cc (int): Current co2 value.
        time (datetime.datetime): Current timestamp.

    Returns:
        dict: one to three new co2 values.
    """
    co2 = {}

    co2["time"] = (time - timedelta(seconds=random.randint(1, DATAGEN_TIME))).strftime(
        "%Y-%m-%dT%H:%M:%S%z"
    )

    nc = random.choices(
        population=[-20, -15, -10, 0, 10, 15, 20], weights=[1, 2, 5, 3, 5, 2, 1]
    )[0]

    co2["value"] = 300 if nc + cc < 300 else 1200 if nc + cc > 1200 else nc + cc

    return co2


def update_temperature(tt, time) -> dict:
    """
    Generates random temperature values from a given room.

    Args:
        tt (int): Current temperature value.
        time (datetime.datetime): Current timestamp.

    Returns:
        dict: one to three new temperature values.
    """
    temp = {}

    temp["time"] = (time - timedelta(seconds=random.randint(1, DATAGEN_TIME))).strftime(
        "%Y-%m-%dT%H:%M:%S%z"
    )

    nt = random.choices(
        population=[-0.7, -0.3, -0.1, 0, 0.1, 0.3, 0.7],
        weights=[1, 2, 3, 5, 5, 4, 2],
    )[0]
    temp["value"] = -20 if nt + tt < -20 else 80 if nt + tt > 80 else round(nt + tt, 2)

    return temp


load_dotenv(".env")

METRICS_URL = os.getenv("METRICS_ENDPOINT")
ROOMS_URL = os.getenv("ROOMS_ENDPOINT")
DATAGEN_TIME = 5


try:
    while True:
        rooms = requests.get(ROOMS_URL, timeout=60).json()
        metrics = {}
        now = datetime.now(timezone.utc).astimezone()

        i, _, _ = select.select([sys.stdin], [], [], DATAGEN_TIME)
        command = sys.stdin.readline().strip() if i else "default"

        i = random.randint(0, len(rooms) - 1)
        dt, wt, dc, wc, ip, RESTART = -1, -1, -1, -1, -1, False

        match command:
            case "dt":
                dt = i
            case "wt":
                wt = i
            case "dc":
                dc = i
            case "wc":
                wc = i
            case "ip":
                ip = i
            case "restart":
                RESTART = True

        # Restart sensors for better monitoring
        if RESTART:
            for i, room in enumerate(rooms):
                metrics[room["id"]] = {
                    "people": {"value": 5, "time": now.strftime("%Y-%m-%dT%H:%M:%S%z")},
                    "co2": {"value": 500, "time": now.strftime("%Y-%m-%dT%H:%M:%S%z")},
                    "temperature": {
                        "value": 23,
                        "time": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    },
                }
        # Create new random values or inject a value
        else:
            for i, room in enumerate(rooms):
                metrics[room["id"]] = {
                    "people": (
                        {"value": 0, "time": now.strftime("%Y-%m-%dT%H:%M:%S%z")}
                        if ip == i
                        else update_people(room["metrics"]["people"], now)
                    ),
                    "co2": (
                        {"value": 1001, "time": now.strftime("%Y-%m-%dT%H:%M:%S%z")}
                        if dc == i
                        else (
                            {"value": 801, "time": now.strftime("%Y-%m-%dT%H:%M:%S%z")}
                            if wc == i
                            else update_co2(room["metrics"]["co2"], now)
                        )
                    ),
                    "temperature": (
                        {"value": 70.1, "time": now.strftime("%Y-%m-%dT%H:%M:%S%z")}
                        if dt == i
                        else (
                            {"value": 40.1, "time": now.strftime("%Y-%m-%dT%H:%M:%S%z")}
                            if wt == i
                            else update_temperature(room["metrics"]["temperature"], now)
                        )
                    ),
                }

        requests.post(
            METRICS_URL,
            json=metrics,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )

        print("Generated data!")
except requests.exceptions.Timeout:
    print("Request timed out, closing...")
except requests.exceptions.ConnectionError:
    print("Backend unreachable, closing...")
except KeyboardInterrupt:
    print("\nScript interrupted, closing...")
