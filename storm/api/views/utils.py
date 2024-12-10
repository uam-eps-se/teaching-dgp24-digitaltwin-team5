"""
This module defines utilities shared amongst views.
"""

# eventstream imports
from django.db.models import Count, Q
from django_eventstream import send_event
from django_eventstream.views import get_listener_manager

from api.models import Room, Alert
from api.models import Window, Ventilator, Door, Light

from api.serializers.devices import WindowSerializer, DoorSerializer
from api.serializers.devices import VentilatorSerializer, LightSerializer
from api.serializers.room_dashboard import RoomDashboardSerializer
from api.serializers.room_details import RoomDetailSerializer


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
                data = get_rooms()
            case "r":
                data = get_room(int(channel[5:]))
            case "d":
                data = get_devices() if event == DEVS else get_doors()
                event = "devices" if event == DEVS else "doors"
            case "c":
                data = get_context()
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


def get_rooms():
    """
    Equivalent to 'v1/rooms' GET without circular imports
    """
    rooms = Room.objects.all()
    return RoomDashboardSerializer(rooms, many=True).data


def get_room(identifier):
    """
    Equivalent to 'v1/room/id' GET without circular imports
    """
    room = Room.objects.get(id=identifier)
    return RoomDetailSerializer(room).data


def get_devices():
    """
    Equivalent to 'v1/devices' GET without circular imports
    """

    # Dictionary with classes and serializers for all devices
    devmodels = {
        "windows": (Window, WindowSerializer),
        "ventilators": (Ventilator, VentilatorSerializer),
        "lights": (Light, LightSerializer),
    }
    data = {}

    # Serialize non-associated devices
    for key, (model, serializer) in devmodels.items():
        devs = model.objects.filter(room=None)
        data[key] = serializer(devs, many=True).data

    return data


def get_doors():
    """
    Equivalent to 'v1/doors' GET without circular imports
    """
    doors = Door.objects.annotate(connection_count=Count("doorconnectsroom")).filter(
        Q(connection_count__lt=2) | Q(connection_count=0)
    )

    return DoorSerializer(doors, many=True).data


def get_context():
    """
    Equivalent to 'v1/context' GET without circular imports
    """
    return {
        "rooms": [{"id": r.id, "name": r.name} for r in Room.objects.all()],
        "alerts": [
            {
                "id": a.id,
                "type": a.type,
                "content": a.content,
                "time": a.time.timestamp(),
                "roomId": a.room.id,
                "roomName": a.room.name,
            }
            for a in Alert.objects.filter(received=False)
        ],
    }
