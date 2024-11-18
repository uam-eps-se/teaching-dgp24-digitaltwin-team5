"""
This module defines a parent abstract class for room serialization.
"""

# regular imports
from typing import NamedTuple, Dict

# django imports
from django.db import models
from timescale.db.models.models import TimescaleModel

# restframework imports
from rest_framework import serializers

# API imports
from api.models import Room, Ventilator, Light, Window
from api.models import DoorConnectsRoom
from api.models import PeopleInRoom, Co2InRoom, TemperatureInRoom
from api.models import DoorOpen, VentilatorOn, LightOn, WindowOpen
from api.models import Alert


class DeviceMeta(NamedTuple):
    """
    Defines required metadata for handling device serialization.
    """

    model: models.Model
    event: TimescaleModel
    attr: str


class MetricMeta(NamedTuple):
    """
    Defines required metadata for handling metric serialization.
    """

    metric: TimescaleModel
    attr: str


class RoomSerializer(serializers.ModelSerializer):
    """
    This class serializes generic room information to be shown in the dashboard
    at the root url.
    """

    devices = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()
    temperature_status = serializers.SerializerMethodField()
    co2_status = serializers.SerializerMethodField()

    class Meta:
        model = Room
        abstract = True
        fields = [
            "id",
            "name",
            "size",
            "temperature_status",
            "co2_status",
            "devices",
            "metrics",
        ]

    def __init__(self, *args, **kwargs):
        """
        Constructor method for this class.
        """
        self.devs: Dict[str, DeviceMeta] = {
            "doors": DeviceMeta(model=DoorConnectsRoom, event=DoorOpen, attr="is_open"),
            "windows": DeviceMeta(model=Window, event=WindowOpen, attr="is_open"),
            "ventilators": DeviceMeta(
                model=Ventilator, event=VentilatorOn, attr="is_on"
            ),
            "lights": DeviceMeta(model=Light, event=LightOn, attr="is_on"),
        }
        self.mets: Dict[str, DeviceMeta] = {
            "people": MetricMeta(metric=PeopleInRoom, attr="no_people_in_room"),
            "co2": MetricMeta(metric=Co2InRoom, attr="co2"),
            "temperature": MetricMeta(metric=TemperatureInRoom, attr="temp"),
        }
        super().__init__(*args, **kwargs)

    def get_temperature_status(self, obj: Room):
        """
        Obtains the last temperature status for this rooom.
        """
        _ = TemperatureInRoom.objects.filter(room=obj).last()
        return (
            Alert.AlertType.INFO
            if (_ is None or _.temp < 40)
            else (
                Alert.AlertType.WARNING if 40 <= _.temp < 70 else Alert.AlertType.DANGER
            )
        )

    def get_co2_status(self, obj: Room):
        """
        Obtains the last co2 status for this rooom.
        """
        _ = TemperatureInRoom.objects.filter(room=obj).last()
        return (
            Alert.AlertType.INFO
            if (_ is None or _.co2 < 800)
            else (
                Alert.AlertType.WARNING
                if 800 < _.co2 <= 1000
                else Alert.AlertType.DANGER
            )
        )
