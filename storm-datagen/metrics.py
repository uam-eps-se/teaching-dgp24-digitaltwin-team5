"""
This script generates random data every five seconds for all rooms received
from the storm app.
"""

import os
import random
from time import sleep
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
    people = {"times": [], "values": []}
    nvals = random.randint(1, 3)

    seconds = sorted(random.sample(range(DATAGEN_TIME + 1), nvals))

    # Create N readings
    people["times"] = sorted(
        [
            (time - timedelta(seconds=seconds[i])).strftime("%Y-%m-%dT%H:%M:%S%z")
            for i in range(nvals)
        ]
    )

    # Values for first reading, uses value read from API
    np = random.choices(
        population=[-3, -2, -1, 0, 1, 2, 3], weights=[1, 2, 3, 5, 3, 2, 1]
    )[0]
    people["values"].append(0 if np + pp < 0 else 30 if np + pp > 30 else np + pp)

    # N-1 values, uses previous updated value
    for _ in range(1, nvals):
        np = random.choices(
            population=[-3, -2, -1, 0, 1, 2, 3], weights=[1, 2, 3, 5, 3, 2, 1]
        )[0]
        pp = people["values"][-1]
        people["values"].append(0 if np + pp < 0 else 30 if np + pp > 30 else np + pp)

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
    co2 = {"times": [], "values": []}
    nvals = random.randint(1, 3)

    seconds = sorted(random.sample(range(DATAGEN_TIME + 1), nvals))

    # Create N readings
    co2["times"] = sorted(
        [
            (time - timedelta(seconds=seconds[i])).strftime("%Y-%m-%dT%H:%M:%S%z")
            for i in range(nvals)
        ]
    )

    # Values for first reading, uses value read from API
    nc = random.choices(
        population=[-60, -30, -15, 0, 15, 30, 60], weights=[1, 2, 5, 3, 5, 2, 1]
    )[0]
    co2["values"].append(300 if nc + cc < 300 else 1200 if nc + cc > 1200 else nc + cc)

    # N-1 values, uses previous updated value
    for _ in range(1, nvals):
        nc = random.choices(
            population=[-60, -30, -15, 0, 15, 30, 60], weights=[1, 2, 5, 3, 5, 2, 1]
        )[0]
        cc = co2["values"][-1]
        co2["values"].append(
            300 if nc + cc < 300 else 1200 if nc + cc > 1200 else nc + cc
        )

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
    temps = {"times": [], "values": []}
    nvals = random.randint(1, 3)

    seconds = sorted(random.sample(range(DATAGEN_TIME + 1), nvals))

    # Create N readings
    temps["times"] = sorted(
        [
            (time - timedelta(seconds=seconds[i])).strftime("%Y-%m-%dT%H:%M:%S%z")
            for i in range(nvals)
        ]
    )

    # Values for first reading, uses value read from API
    nt = random.choices(
        population=[-0.7, -0.3, -0.1, 0, 0.1, 0.3, 0.7],
        weights=[1, 2, 3, 5, 5, 4, 2],
    )[0]
    temps["values"].append(
        -20 if nt + tt < -20 else 80 if nt + tt > 80 else round(nt + tt, 2)
    )

    # N-1 values, uses previous updated value
    for _ in range(1, nvals):
        nt = random.choices(
            population=[-0.7, -0.3, -0.1, 0, 0.1, 0.3, 0.7],
            weights=[1, 2, 3, 5, 5, 4, 2],
        )[0]
        tt = temps["values"][-1]
        temps["values"].append(
            -20 if nt + tt < -20 else 80 if nt + tt > 80 else round(nt + tt, 2)
        )

    return temps


load_dotenv(".env")

METRICS_URL = os.getenv("METRICS_ENDPOINT")
ROOMS_URL = os.getenv("ROOMS_ENDPOINT")
DATAGEN_TIME = 5


while True:
    try:
        rooms = requests.get(ROOMS_URL, timeout=60).json()  # 10 seconds
    except requests.exceptions.Timeout:
        break
    metrics = {}
    now = datetime.now(timezone.utc).astimezone()

    for room in rooms:
        metrics[room["id"]] = {
            "people": update_people(room["metrics"]["people"], now),
            "co2": update_co2(room["metrics"]["co2"], now),
            "temperature": update_temperature(room["metrics"]["temperature"], now),
        }
    try:
        requests.post(
            METRICS_URL,
            json=metrics,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
    except requests.exceptions.Timeout:
        break

    print("Generated data!")
    sleep(DATAGEN_TIME)
