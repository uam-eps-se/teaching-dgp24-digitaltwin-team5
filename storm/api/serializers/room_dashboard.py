"""
This module defines the serialized representation of the room dashboard.
"""

from api.models.base import Room, Ventilator, Light, Window
from api.models.base import DoorConnectsRoom
from api.models.metrics import PeopleInRoom, Co2InRoom, TemperatureInRoom
from api.models.events import DoorOpen, VentilatorOn, LightOn, WindowOpen

from rest_framework import serializers


class RoomDashboardSerializer(serializers.ModelSerializer):
    """
    This class serializes generic room information to be shown in the dashboard
    at the root url.
    """

    devices = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "name", "size", "devices", "metrics"]

    def get_devices(self, obj):
        """
        Obtains generic device information for a room.

        Args:
            obj (Room): Room from where information is extracted

        Returns:
            dict: json-like dictionary with device information.
        """
        devs = {
            "doors": (DoorConnectsRoom, DoorOpen, "is_open"),
            "windows": (Window, WindowOpen, "is_open"),
            "ventilators": (Ventilator, VentilatorOn, "is_on"),
            "lights": (Light, LightOn, "is_on"),
        }

        devices = {
            "doors": {"total": 0, "open": 0},
            "windows": {"total": 0, "open": 0},
            "ventilators": {"total": 0, "on": 0},
            "lights": {"total": 0, "on": 0},
        }

        for key, (model, event, attr) in devs.items():
            for device in model.objects.filter(room=obj):
                devices[key]["total"] += 1
                device = device.door if key == "doors" else device
                _ = event.objects.filter(**{f"{key[:-1]}": device}).last()
                if _ is not None and getattr(_, attr):
                    devices[key][f"{attr[3:]}"] += 1
        return devices

    def get_metrics(self, obj):
        """
        Obtains real-time metrics for a room.

        Args:
            obj (Room): Room from where information is extracted

        Returns:
            dict: json-like dictionary with metric information.
        """
        mets = {
            "people": (PeopleInRoom, "no_people_in_room"),
            "co2": (Co2InRoom, "co2"),
            "temperature": (TemperatureInRoom, "temp"),
        }
        metrics = {}

        for key, (model, attr) in mets.items():
            _ = model.objects.filter(room=obj).last()
            metrics[key] = getattr(_, attr, 0)

        return metrics
