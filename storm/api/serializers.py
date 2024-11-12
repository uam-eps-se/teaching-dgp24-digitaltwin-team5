"""
This module specifices the json-format output of serialized data that is
accessed from the API.
"""

from datetime import timedelta
from api.models import Room, Door, Ventilator, Light, Window
from api.models import DoorConnectsRoom
from api.models import PeopleInRoom, Co2InRoom, TemperatureInRoom
from api.models import DoorOpen, VentilatorOn, LightOn, WindowOpen
from rest_framework import serializers
from django.utils import timezone

#
#   BASE MODELS
#


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


class RoomDetailSerializer(RoomSerializer):
    """
    This class serializes real-time room information to be shown in the room
    details url.
    """

    def _get_doors(self, obj):
        """
        Obtains a history of actions for every door in the room. Recorded
        actions are within one hour of the last update.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with door information.
        """
        doors: dict = {}

        for door in DoorConnectsRoom.objects.filter(room=obj):
            last = DoorOpen.objects.filter(door=door.door).last()
            if last is not None:
                data = DoorOpen.timescale.filter(
                    door=door.door, time__gt=(last.time - timedelta(hours=1))
                ).order_by("-time")

                doors[door.door.name] = {
                    "id": door.door.id,
                    "times": [
                        date.timestamp() for date in data.values_list("time", flat=True)
                    ],
                    "values": list(data.values_list("is_open", flat=True)),
                }
            else:
                doors[door.door.name] = {
                    "id": door.door.id,
                    "times": [],
                    "values": [],
                }
        return doors

    def _get_windows(self, obj):
        """
        Obtains a history of actions for every window in the room. Recorded
        actions are within one hour of the last update.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with window information.
        """
        windows: dict = {}

        for window in Window.objects.filter(room=obj):
            last = WindowOpen.objects.filter(window=window).last()
            if last is not None:
                data = WindowOpen.timescale.filter(
                    window=window, time__gt=(last.time - timedelta(hours=1))
                ).order_by("-time")

                windows[window.name] = {
                    "id": window.id,
                    "times": [
                        date.timestamp() for date in data.values_list("time", flat=True)
                    ],
                    "values": list(data.values_list("is_open", flat=True)),
                }
            else:
                windows[window.name] = {
                    "id": window.id,
                    "times": [],
                    "values": [],
                }

        return windows

    def _get_ventilators(self, obj):
        """
        Obtains a history of actions for every ventilator in the room. Recorded
        actions are within one hour of the last update.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with ventilator information.
        """
        ventilators: dict = {}

        for ventilator in Ventilator.objects.filter(room=obj):
            last = VentilatorOn.objects.filter(ventilator=ventilator).last()
            if last is not None:
                data = VentilatorOn.timescale.filter(
                    ventilator=ventilator, time__gt=(last.time - timedelta(hours=1))
                ).order_by("-time")

                ventilators[ventilator.name] = {
                    "id": ventilator.id,
                    "times": [
                        date.timestamp() for date in data.values_list("time", flat=True)
                    ],
                    "values": list(data.values_list("is_on", flat=True)),
                }
            else:
                ventilators[ventilator.name] = {
                    "id": ventilator.id,
                    "times": [],
                    "values": [],
                }

        return ventilators

    def _get_lights(self, obj):
        """
        Obtains a history of actions for every light in the room. Recorded
        actions are within one hour of the last update.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with light information.
        """
        lights: dict = {}

        for light in Light.objects.filter(room=obj):
            last = LightOn.objects.filter(light=light).last()
            if last is not None:
                data = LightOn.timescale.filter(
                    light=light, time__gt=(last.time - timedelta(hours=1))
                ).order_by("-time")

                lights[light.name] = {
                    "id": light.id,
                    "times": [
                        date.timestamp() for date in data.values_list("time", flat=True)
                    ],
                    "values": list(data.values_list("is_on", flat=True)),
                }
            else:
                lights[light.name] = {
                    "id": light.id,
                    "times": [],
                    "values": [],
                }

        return lights

    def _get_people(self, obj):
        """
        Obtains a history of the number of people in the room from the last
        hour.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with people history.
        """
        data = PeopleInRoom.timescale.filter(
            room=obj, time__gt=(timezone.now() - timedelta(hours=1))
        ).order_by("-time")

        people = {
            "times": [date.timestamp() for date in data.values_list("time", flat=True)],
            "values": list(data.values_list("no_people_in_room", flat=True)),
        }

        return people

    def _get_temperature(self, obj):
        """
        Obtains a history of temperature values in the room from the last hour.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with temperature history.
        """
        data = TemperatureInRoom.timescale.filter(
            room=obj, time__gt=(timezone.now() - timedelta(hours=1))
        ).order_by("-time")

        temps = {
            "times": [date.timestamp() for date in data.values_list("time", flat=True)],
            "values": list(data.values_list("temp", flat=True)),
        }

        return temps

    def _get_co2(self, obj):
        """
        Obtains a history of Co2 values in the room from the last hour.

        Args:
            obj (Room): room from where the information is extracted.

        Returns:
            dict: Dictionary with Co2 history.
        """
        data = Co2InRoom.timescale.filter(
            room=obj, time__gt=(timezone.now() - timedelta(hours=1))
        ).order_by("-time")

        co2 = {
            "times": [date.timestamp() for date in data.values_list("time", flat=True)],
            "values": list(data.values_list("co2", flat=True)),
        }

        return co2


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
