"""
This module defines models for metrics events related to rooms.
"""

from api.models.base import Room
from django.db import models
from timescale.db.models.models import TimescaleModel

INFO, WARNING, DANGER = 0, 1, 2
ALERT_CHOICES = [(INFO, "Info"), (WARNING, "Warning"), (DANGER, "Danger")]


class PeopleInRoom(TimescaleModel):
    """
    Model representation for the people metrics in a room.
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    no_people_in_room = models.IntegerField(default=0)


class TemperatureInRoom(TimescaleModel):
    """
    Model representation for temperature metrics in a room.
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    temp = models.DecimalField(default=0, max_digits=5, decimal_places=2)


class Co2InRoom(TimescaleModel):
    """
    Model representation for Co2 metrics in a room.
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    co2 = models.IntegerField(default=0)


class Alert(TimescaleModel):
    """
    Model representation for alerts related to various metrics.
    """

    class AlertType(models.IntegerChoices):  # pylint: disable=too-many-ancestors
        """
        Model to represent alert types.
        """

        INFO = 0
        WARNING = 1
        DANGER = 2

    id = models.AutoField(primary_key=True)
    type = models.IntegerField(choices=AlertType)
    content = models.TextField(max_length=200)
    received = models.BooleanField(default=False)
