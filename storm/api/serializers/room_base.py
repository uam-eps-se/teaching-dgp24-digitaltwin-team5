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

    class Meta:
        model = Room
        abstract = True
        fields = ["id", "name", "size", "devices", "metrics"]

    def __init__(self, *args, **kwargs):
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
