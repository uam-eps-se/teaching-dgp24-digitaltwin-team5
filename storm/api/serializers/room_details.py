"""
This module defines the serialized representation of a room.
"""

# regular imports
from datetime import timedelta

# API imports
from api.serializers.room_base import RoomSerializer
from django.utils import timezone


class RoomDetailSerializer(RoomSerializer):
    """
    This class serializes real-time room information to be shown in the room
    details url.
    """

    def get_devices(self, obj):
        """
        Obtains specific device information for a room.

        Args:
            obj (Room): Room from where information is extracted.

        Returns:
            dict: json-like dictionary with device information.
        """

        devices = {"doors": {}, "windows": {}, "ventilators": {}, "lights": {}}
        time = timezone.now() - timedelta(hours=1)

        for key, (model, event, attr) in self.devs.items():
            for device in model.objects.filter(room=obj):
                device = device.door if key == "doors" else device
                query = {f"{key[:-1]}": device}

                last = event.objects.filter(**query).last()
                data = event.timescale.filter(**query, time__gt=time).order_by("-time")

                devices[key][device.id] = {
                    "name": device.name,
                    "current": getattr(last, attr, False),
                    "times": [
                        date.timestamp() for date in data.values_list("time", flat=True)
                    ],
                    "values": list(data.values_list(attr, flat=True)),
                }

        return devices

    def get_metrics(self, obj):
        """
        Obtains detailed real-time metrics for a room.

        Args:
            obj (Room): Room from where information is extracted

        Returns:
            dict: json-like dictionary with metric information.
        """

        metrics = {}
        time = timezone.now() - timedelta(hours=1)

        for key, (model, attr) in self.mets.items():
            data = model.timescale.filter(room=obj, time__gt=time).order_by("-time")
            metrics[key] = {
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list(attr, flat=True)),
            }

        return metrics
