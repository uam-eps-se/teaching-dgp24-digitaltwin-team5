"""
This module defines models for metrics events related to rooms.
"""

from api.models.base import Room
from django.db import models
from timescale.db.models.models import TimescaleModel


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
