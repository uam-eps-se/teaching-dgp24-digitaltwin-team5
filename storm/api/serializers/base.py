"""
This module defines a base serialzier model for rooms.
"""

from api.models.base import Room
from rest_framework import serializers


class RoomSerializer(serializers.ModelSerializer):
    """
    Parent class for specifying handlers and methods for room serialization.
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
            "doors": self._get_doors,
            "windows": self._get_windows,
            "ventilators": self._get_ventilators,
            "lights": self._get_lights,
        }
        return {key: func(obj) for key, func in devs.items()}

    def get_metrics(self, obj):
        """
        Obtains real-time metrics for a room.

        Args:
            obj (Room): Room from where information is extracted

        Returns:
            dict: json-like dictionary with metric information.
        """
        mets = {
            "people": self._get_people,
            "co2": self._get_co2,
            "temperature": self._get_temperature,
        }
        return {key: func(obj) for key, func in mets.items()}

    def _get_doors(self, obj):
        pass

    def _get_windows(self, obj):
        pass

    def _get_ventilators(self, obj):
        pass

    def _get_lights(self, obj):
        pass

    def _get_people(self, obj):
        pass

    def _get_co2(self, obj):
        pass

    def _get_temperature(self, obj):
        pass
