"""
This module defines utilities shared amongst views.
"""

# eventstream imports
from django_eventstream import send_event
from django_eventstream.views import get_listener_manager


def send_storm_event(channel: str, event: str, data: object, **send_kwargs: dict):
    """Sends an SSE event to a channel, only if it has listeners

    Args:
        channel (str): Channel to which the event is sent
        event (str): Event name, default may be "message"
        data (object): Data to send
    """

    # Check if there are listeners in channel
    if get_listener_manager().listeners_by_channel.get(channel, False):
        send_event(channel, event, data, **send_kwargs)
