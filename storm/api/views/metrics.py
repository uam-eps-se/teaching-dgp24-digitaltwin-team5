"""
This module defines the `v1/doors` endpoint for the API.
"""

# regular imports
from typing import NamedTuple, Dict, Callable

# django imports
from timescale.db.models.models import TimescaleModel
from django.utils import timezone

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request

# API imports
from api.models import PeopleInRoom, TemperatureInRoom, Co2InRoom
from api.models import Alert
from api.models import Room, Window, Ventilator, Light
from api.models import DoorConnectsRoom
from api.models import WindowOpen, VentilatorOn, LightOn, DoorOpen
from api.views.utils import send
from api.views.utils import CHANNEL_CONTEXT, CHANNEL_ROOM, CHANNEL_SUMMARY


class MetricMetadata(NamedTuple):
    """
    Defines type hints for models and callables for the `v1/metrics` endpoint.
    """

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
        Triggers actions for air quality control when co2 goes over safe
        levels.

        Args:
            room (Room): Room with unusual co2 readings.
            value (int): Current co2 reading.
            previous (Co2InRoom): Old co2 value.
        """
        now = timezone.now()

        warn = previous is None or previous.co2 < 800 or previous.co2 > 1000
        danger = previous is None or previous.co2 <= 1000
        if 800 <= value <= 1000 and warn:
            content = "Co2 levels are nearing dangerous ppm values"
            Alert(
                time=now,
                room=room,
                type=Alert.AlertType.WARNING,
                content=content,
            ).save()
            return True

        if value > 1000 and danger:
            content = (
                "Co2 levels too high, opening windows and turning on cooling devices"
            )
            for window in Window.objects.filter(room=room):
                last = WindowOpen.objects.filter(window=window).last()
                if not last or last.is_open is False:
                    WindowOpen(time=now, window=window, is_open=True).save()
            for ventilator in Ventilator.objects.filter(room=room):
                last = VentilatorOn.objects.filter(ventilator=ventilator).last()
                if not last or last.is_on is False:
                    VentilatorOn(time=now, ventilator=ventilator, is_on=True).save()
            Alert(
                time=now,
                room=room,
                type=Alert.AlertType.DANGER,
                content=content,
            ).save()
            return True
        return False

    def energy_efficiency_control(self, room: Room, value: int, previous: PeopleInRoom):
        """
        Triggers actions for energy efficiency control when the number of
        people inside the room change.

        Args:
            room (Room): Room to trigger changes.
            value (int): Current number of people.
            previous (Co2InRoom): Old number of people.
        """
        # Room is now empty
        turn_off = value == 0 and (previous is None or previous.no_people_in_room > 0)

        # Room is no longer empty
        turn_on = value > 0 and (previous is None or previous.no_people_in_room == 0)

        now = timezone.now()
        if turn_on:
            content = "People have entered the room. Turning lights on"
            for light in Light.objects.filter(room=room):
                last = LightOn.objects.filter(light=light).last()
                if not last or last.is_on is False:
                    LightOn(time=now, light=light, is_on=True).save()
            Alert(
                time=now,
                room=room,
                type=Alert.AlertType.INFO,
                content=content,
            ).save()
            return True
        if turn_off:
            content = "Room is empty. Lights and Cooling devices turned off"
            for light in Light.objects.filter(room=room):
                last = LightOn.objects.filter(light=light).last()
                if not last or last.is_on is True:
                    LightOn(time=now, light=light, is_on=False).save()

            for ventilator in Ventilator.objects.filter(room=room):
                last = VentilatorOn.objects.filter(ventilator=ventilator).last()
                if not last or last.is_on is True:
                    VentilatorOn(time=now, ventilator=ventilator, is_on=False).save()
            Alert(
                time=now,
                room=room,
                type=Alert.AlertType.INFO,
                content=content,
            ).save()
            return True
        return False

    def safety_control(self, room: Room, value: int, previous: TemperatureInRoom):
        """
        Triggers actions for safety control when temperature goes over safe
        levels.

        Args:
            room (Room): Room with unusual co2 readings.
            value (int): Current co2 reading.
            previous (Co2InRoom): Old co2 value.
        """

        warn = previous is None or previous.temp >= 70 or previous.temp < 40
        danger = previous is None or previous.temp <= 70
        now = timezone.now()

        if 40 <= value <= 70 and warn:
            Alert(
                time=now,
                room=room,
                type=Alert.AlertType.WARNING,
                content="Temperature levels are nearing dangerous values",
            ).save()
            return True
        if value > 70 and danger:
            for door in DoorConnectsRoom.objects.filter(room=room):
                last = DoorOpen.objects.filter(door=door.door).last()
                if not last or last.is_open is False:
                    DoorOpen(time=now, door=door.door, is_open=True).save()
            Alert(
                time=now,
                room=room,
                type=Alert.AlertType.DANGER,
                content="Temperature levels too high, opening doors",
            ).save()
            return True
        return False

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
        new_alerts = False
        for key, metrics in request.data.items():
            room = Room.objects.filter(id=int(key)).first()

            for metric, data in metrics.items():
                model, attr, action = mets[metric]
                last = model.objects.filter(room=room).last()

                model(
                    **{"time": data["time"], "room": room, attr: data["value"]}
                ).save()
                new_alerts |= action(room, data["value"], last)

            send(f"{CHANNEL_ROOM}-{room.id}")

        if new_alerts:
            send(CHANNEL_CONTEXT)
        send(CHANNEL_SUMMARY)

        return Response("Metrics updated successfully!")
