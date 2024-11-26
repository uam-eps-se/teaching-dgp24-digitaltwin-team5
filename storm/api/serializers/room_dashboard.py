"""
This module defines the serialized representation of the room dashboard.
"""

# API imports
from api.serializers.room_base import RoomSerializer


class RoomDashboardSerializer(RoomSerializer):
    """
    This class serializes generic room information to be shown in the dashboard
    at the root url.
    """

    def get_devices(self, obj):
        """
        Obtains generic device information for a room.

        Args:
            obj (Room): Room from where information is extracted

        Returns:
            dict: json-like dictionary with device information.
        """

        devices = {
            "doors": {"total": 0, "open": 0},
            "windows": {"total": 0, "open": 0},
            "ventilators": {"total": 0, "on": 0},
            "lights": {"total": 0, "on": 0},
        }

        for key, (model, event, attr) in self.devs.items():
            for device in model.objects.filter(room=obj):
                devices[key]["total"] += 1
                device = device.door if key == "doors" else device
                _ = event.objects.filter(**{f"{key[:-1]}": device}).last()
                if _ is not None and getattr(_, attr):
                    devices[key][f"{attr[3:]}"] += 1
        return devices

    def get_metrics(self, obj):
        """
        Obtains last real-time metrics for a room.

        Args:
            obj (Room): Room from where information is extracted

        Returns:
            dict: json-like dictionary with metric information.
        """
        metrics = {}

        for key, (model, attr) in self.mets.items():
            _ = model.objects.filter(room=obj).last()
            metrics[key] = getattr(_, attr, 0)

        return metrics
