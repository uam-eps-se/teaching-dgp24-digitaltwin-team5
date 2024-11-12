"""
This module defines the serialized representation of a room.
"""

from datetime import timedelta
from api.models.base import Room, Ventilator, Light, Window
from api.models.base import DoorConnectsRoom
from api.models.metrics import PeopleInRoom, Co2InRoom, TemperatureInRoom
from api.models.events import DoorOpen, VentilatorOn, LightOn, WindowOpen
from django.utils import timezone

from rest_framework import serializers


class RoomDetailSerializer(serializers.ModelSerializer):
    """
    This class serializes real-time room information to be shown in the room
    details url.
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

        devices = {"doors": {}, "windows": {}, "ventilators": {}, "lights": {}}
        time = timezone.now() - timedelta(hours=1)

        for key, (model, event, attr) in devs.items():
            for device in model.objects.filter(room=obj):
                device = device.door if key == "doors" else device
                query = {f"{key[:-1]}": device}

                last = event.objects.filter(**query).last()
                data = event.timescale.filter(**query, time__gt=time).order_by("-time")

                devices[key][device.id] = {
                    "id": device.id,
                    "name": device.name,
                    "current": getattr(last, attr) if last is not None else False,
                    "times": [
                        date.timestamp() for date in data.values_list("time", flat=True)
                    ],
                    "values": list(data.values_list(attr, flat=True)),
                }

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
        time = timezone.now() - timedelta(hours=1)

        for key, (model, attr) in mets.items():
            data = model.timescale.filter(room=obj, time__gt=time).order_by("-time")
            metrics[key] = {
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list(attr, flat=True)),
            }

        return metrics
