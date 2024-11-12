"""
This module defines the serialized representation of devices.
"""

from api.models.base import Door, Ventilator, Light, Window
from rest_framework import serializers


class WindowSerializer(serializers.ModelSerializer):
    """
    Serializes window database records.
    """

    class Meta:
        model = Window
        fields = ["id", "name"]


class LightSerializer(serializers.ModelSerializer):
    """
    Serializes light database records.
    """

    class Meta:
        model = Light
        fields = ["id", "name"]


class VentilatorSerializer(serializers.ModelSerializer):
    """
    Serializes ventilator database records.
    """

    class Meta:
        model = Ventilator
        fields = ["id", "name"]


class DoorSerializer(serializers.ModelSerializer):
    """
    Serializes door database records.
    """

    class Meta:
        model = Door
        fields = ["id", "name", "rooms"]
