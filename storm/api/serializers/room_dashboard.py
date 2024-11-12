"""
This module defines the serialized representation of the room dashboard.
"""

from api.models.base import Ventilator, Light, Window
from api.models.base import DoorConnectsRoom
from api.models.metrics import PeopleInRoom, Co2InRoom, TemperatureInRoom
from api.models.events import DoorOpen, VentilatorOn, LightOn, WindowOpen
from api.serializers.base import RoomSerializer


class RoomDashboardSerializer(RoomSerializer):
    """
    This class serializes generic room information to be shown in the dashboard
    at the root url.
    """

    def _get_doors(self, obj):
        """
        Obtains the number of opened/total doors in a room.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with the number of opened and total doors.
        """
        doors: dict = {"total": 0, "open": 0}

        for door in DoorConnectsRoom.objects.filter(room=obj.id):
            doors["total"] += 1
            _ = DoorOpen.objects.filter(door=door.door).last()
            if _ is not None and _.is_open:
                doors["open"] += 1

        return doors

    def _get_windows(self, obj):
        """
        Obtains the number of opened/total windows in a room.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with the number of opened and total windows.
        """
        windows: dict = {"total": 0, "open": 0}

        for window in Window.objects.filter(room=obj.id):
            windows["total"] += 1
            _ = WindowOpen.objects.filter(window=window).last()
            if _ is not None and _.is_open:
                windows["open"] += 1

        return windows

    def _get_ventilators(self, obj):
        """
        Obtains the number of on/total ventilators in a room.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with the number of on and total ventilators.
        """
        ventilators: dict = {"total": 0, "on": 0}

        for ventilator in Ventilator.objects.filter(room=obj.id):
            ventilators["total"] += 1
            _ = VentilatorOn.objects.filter(ventilator=ventilator).last()
            if _ is not None and _.is_on:
                ventilators["on"] += 1

        return ventilators

    def _get_lights(self, obj):
        """
        Obtains the number of on/total lights in a room.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with the number of on and total lights.
        """
        lights: dict = {"total": 0, "on": 0}

        for light in Light.objects.filter(room=obj.id):
            lights["total"] += 1
            _ = LightOn.objects.filter(light=light).last()
            if _ is not None and _.is_on:
                lights["on"] += 1

        return lights

    def _get_people(self, obj):
        """
        Obtains the current number of people in a room.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            int: Number of people.
        """
        _ = PeopleInRoom.objects.filter(room=obj).last()
        return 0 if _ is None else _.no_people_in_room

    def _get_co2(self, obj):
        """
        Obtains the current Co2 value in a room.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            int: Co2 value.
        """
        _ = Co2InRoom.objects.filter(room=obj).last()
        return 0 if _ is None else _.co2

    def _get_temperature(self, obj):
        """
        Obtains the current temperature in a room.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            int: Temperature value.
        """
        _ = TemperatureInRoom.objects.filter(room=obj).last()
        return 0 if _ is None else _.temp
