"""
This module defines the `v1/doors` endpoint for the API.
"""

from typing import NamedTuple, Dict, Callable

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request

# API imports
from api.models.metrics import PeopleInRoom, TemperatureInRoom, Co2InRoom
from api.models.base import Room, Window, Ventilator, Light
from api.models.base import DoorConnectsRoom
from api.models.events import WindowOpen, VentilatorOn, LightOn, DoorOpen

from timescale.db.models.models import TimescaleModel
from django.utils import timezone

ROOM_EMPTY_THRESHOLD = 0
AIR_QUALITY_THRESHOLD = 1000
TEMP_SAFETY_THRESHOLD = 70


class MetricMetadata(NamedTuple):
    model: TimescaleModel
    attr: str
    action: Callable[[Room, int, TimescaleModel], None]


class MetricsAPIView(APIView):
    """
    Defines views for all end-points associated to sensor generated metrics.
    """

    allowed_methods = ["POST", "POST"]

    def air_quality_control(self, room: Room, value: int, previous: Co2InRoom):
        """
        Triggers actions for air quality control when co2 levels go over safe
        levels.

        Args:
            room (Room): Room with unusual co2 readings.
            value (int): Current co2 reading.
            previous (Co2InRoom): Old co2 value.
        """
        if value > 1000 and previous.co2 <= 1000:
            now = timezone.now()
            for window in Window.objects.filter(room=room):
                last = WindowOpen.objects.filter(window=window).last()
                if not last or last.is_open is False:
                    WindowOpen(time=now, window=window, is_open=True).save()
            for ventilator in Ventilator.objects.filter(room=room):
                last = VentilatorOn.objects.filter(ventilator=ventilator).last()
                if not last or last.is_on is False:
                    VentilatorOn(time=now, ventilator=ventilator, is_on=True).save()

    def energy_efficiency_control(self, room: Room, value: int, previous: PeopleInRoom):
        """
        Triggers actions for energy efficiency control when the number of
        people inside the room change

        Args:
            room (Room): Room to trigger changes.
            value (int): Current number of people.
            previous (Co2InRoom): Old number of people.
        """
        # Room is now empty
        turn_off = value == 0 and previous.no_people_in_room > 0

        # Room is no longer empty
        turn_on = value > 0 and previous.no_people_in_room == 0

        now = timezone.now()
        if turn_on or turn_off:
            value = True if turn_on else False
            for light in Light.objects.filter(room=room):
                last = LightOn.objects.filter(light=light).last()
                if not last or last.is_on is not value:
                    LightOn(time=now, light=light, is_on=value).save()

        if turn_off:
            for ventilator in Ventilator.objects.filter(room=room):
                last = VentilatorOn.objects.filter(ventilator=ventilator).last()
                if not last or last.is_on is True:
                    VentilatorOn(time=now, ventilator=ventilator, is_on=False).save()

    def safety_control(self, room: Room, value: int, previous: TemperatureInRoom):
        if value >= 70 and previous.temp <= 70:
            now = timezone.now()
            for door in DoorConnectsRoom.objects.filter(room=room):
                last = DoorOpen.objects.filter(door=door.door).last()
                if not last or last.is_open is False:
                    DoorOpen(time=now, door=door.door, is_open=True).save()

    def post(self, request: Request):
        """
        Creates new metrics for rooms. This method expects to receive the
        parameters specified in `jsons/metrics/post.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        mets: Dict[str, MetricMetadata] = {
            "people": MetricMetadata(
                PeopleInRoom, "no_people_in_room", self.energy_efficiency_control
            ),
            "co2": MetricMetadata(Co2InRoom, "co2", self.air_quality_control),
            "temperature": MetricMetadata(
                TemperatureInRoom, "temp", self.safety_control
            ),
        }

        for key, data in request.data.items():
            room = Room.objects.filter(id=int(key)).first()

            for metric, readings in data.items():
                model, attr, action = mets[metric]
                last = model.objects.filter(room=room).last()

                for time, value in zip(readings["times"], readings["values"]):
                    model(**{"time": time, attr: value, "room": room}).save()

                action(room, readings["values"], last)

        return Response("Metrics updated successfully!")
