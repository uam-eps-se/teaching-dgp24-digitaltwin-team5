"""
This module defines the serialized representation of a room.
"""

from datetime import timedelta
from api.models.base import Ventilator, Light, Window
from api.models.base import DoorConnectsRoom
from api.models.metrics import PeopleInRoom, Co2InRoom, TemperatureInRoom
from api.models.events import DoorOpen, VentilatorOn, LightOn, WindowOpen
from api.serializers.base import RoomSerializer
from django.utils import timezone


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
            data = DoorOpen.timescale.filter(
                door=door.door, time__gt=(timezone.now() - timedelta(hours=1))
            ).order_by("-time")

            doors[door.door.id] = {
                "id": door.door.id,
                "name": door.door.name,
                "current": last.is_open if last is not None else False,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_open", flat=True)),
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
            data = WindowOpen.timescale.filter(
                window=window, time__gt=(timezone.now() - timedelta(hours=1))
            ).order_by("-time")

            windows[window.id] = {
                "id": window.id,
                "name": window.name,
                "current": last.is_open if last is not None else False,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_open", flat=True)),
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
            data = VentilatorOn.timescale.filter(
                ventilator=ventilator, time__gt=(timezone.now() - timedelta(hours=1))
            ).order_by("-time")

            ventilators[ventilator.id] = {
                "id": ventilator.id,
                "name": ventilator.name,
                "current": last.is_on if last is not None else False,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_on", flat=True)),
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
            data = LightOn.timescale.filter(
                light=light, time__gt=(timezone.now() - timedelta(hours=1))
            ).order_by("-time")

            lights[light.id] = {
                "id": light.id,
                "name": light.name,
                "current": last.is_on if last is not None else False,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_on", flat=True)),
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
