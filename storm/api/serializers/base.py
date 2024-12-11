"""
This module defines a base serializer class.
"""

from django.db.models import Count, Q

from api.models import Room, Alert
from api.models import Window, Ventilator, Door, Light

from .devices import WindowSerializer, DoorSerializer
from .devices import VentilatorSerializer, LightSerializer
from .room_dashboard import RoomDashboardSerializer
from .room_details import RoomDetailSerializer


class DataSerializer:
    """
    Wrapper class for serializing functions.
    """

    @classmethod
    def rooms(cls):
        """
        Serializes all rooms in the database.
        """
        rooms = Room.objects.all()
        return RoomDashboardSerializer(rooms, many=True).data

    @classmethod
    def room(cls, identifier):
        """
        Serializes a room with the given id.

        Args:
            identifier (int): Room id.
        """
        room = Room.objects.get(id=identifier)
        return RoomDetailSerializer(room).data

    @classmethod
    def devices(cls):
        """
        Serializes all devices not assigned to a room.
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

    @classmethod
    def doors(cls):
        """
        Serializes all doors connected to less than two rooms.
        """
        doors = Door.objects.annotate(
            connection_count=Count("doorconnectsroom")
        ).filter(Q(connection_count__lt=2) | Q(connection_count=0))

        return DoorSerializer(doors, many=True).data

    @classmethod
    def context(cls):
        """
        Serializes context information, which contains unread alerts and
        all room names.
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
