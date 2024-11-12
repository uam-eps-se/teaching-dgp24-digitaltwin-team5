"""
This module defines all model interpretations for tables in the database.
"""

from django.db import models
from timescale.db.models.models import TimescaleModel


#
#   BASE MODELS
#
class Room(models.Model):
    """
    Room table representation.
    """

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    size = models.IntegerField(default=1)


class Door(models.Model):
    """
    Door table representation.
    """

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    rooms = models.ManyToManyField(Room, through="DoorConnectsRoom")


class Ventilator(models.Model):
    """
    Ventilator table representation.
    """

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)


class Window(models.Model):
    """
    Window table representation.
    """

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)


class Light(models.Model):
    """
    Light table representation.
    """

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)


#
#   MANY-TO-MANY MODELS
#


class DoorConnectsRoom(models.Model):
    """
    Model representation for a connection between a door and up to two rooms.
    """

    door = models.ForeignKey(Door, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)


#
#   REAL-TIME STATUS MODELS
#


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


class WindowOpen(TimescaleModel):
    """
    Model representation for window events.
    """

    window = models.ForeignKey(Window, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=False)


class DoorOpen(TimescaleModel):
    """
    Model representation for door events.
    """

    door = models.ForeignKey(Door, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=False)


class VentilatorOn(TimescaleModel):
    """
    Model representation for ventilator events.
    """

    ventilator = models.ForeignKey(Ventilator, on_delete=models.CASCADE)
    is_on = models.BooleanField(default=False)


class LightOn(TimescaleModel):
    """
    Model representation for light events.
    """

    light = models.ForeignKey(Light, on_delete=models.CASCADE)
    is_on = models.BooleanField(default=False)
