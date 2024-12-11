"""
This module defines utilities shared amongst views.
"""

# eventstream imports
from django_eventstream import send_event
from django_eventstream.views import get_listener_manager

# API imports
from api.serializers import DataSerializer


CHANNEL_SUMMARY = "summary"
CHANNEL_ROOM = "room"
CHANNEL_DEVICES = "devices"
CHANNEL_CONTEXT = "context"
DEVS, DOORS = 0, 1


def send(channel: str, event: int = 0, **kwargs: dict):
    """Sends an SSE event to a channel, only if it has listeners

    Args:
        channel (str): Channel to which the event is sent
        event (str): Event name, default may be "message"
        data (object): Data to send
    """

    # Check if there are listeners in channel
    if get_listeners(channel):
        event = "message"

        match channel[0]:
            case "s":
                data = DataSerializer.rooms()
            case "r":
                data = DataSerializer.room(int(channel[5:]))
            case "d":
                data = (
                    DataSerializer.devices()
                    if event == DEVS
                    else DataSerializer.doors()
                )
                event = "devices" if event == DEVS else "doors"
            case "c":
                data = DataSerializer.context()
            case _:
                raise ValueError(f"channel {channel} is not supported!")

        send_event(channel, event, data, **kwargs)


def get_listeners(channel: str) -> set | bool:
    """Gets listeners from a given `channel`

    Args:
        channel (str): Channel to get listeners from

    Returns:
        set | bool: Set of unique listeners or False if channel doesn't exist
    """
    return get_listener_manager().listeners_by_channel.get(channel, False)
