from django.db import models
from timescale.db.models.models import TimescaleModel


#
#   BASE MODELS
#
class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    size = models.IntegerField(default=1)


class Door(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    rooms = models.ManyToManyField(Room, through="DoorConnectsRoom")


class Ventilator(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)


class Window(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)


class Light(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)


#
#   MANY-TO-MANY MODELS
#


class DoorConnectsRoom(models.Model):
    door = models.ForeignKey(Door, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)


#
#   REAL-TIME STATUS MODELS
#


class PeopleInRoom(TimescaleModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    no_people_in_room = models.IntegerField(default=0)


class TemperatureInRoom(TimescaleModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    temp = models.DecimalField(default=0, max_digits=5, decimal_places=2)


class Co2InRoom(TimescaleModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    co2 = models.IntegerField(default=0)


class WindowOpen(TimescaleModel):
    window = models.ForeignKey(Window, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=False)


class DoorOpen(TimescaleModel):
    door = models.ForeignKey(Door, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=False)


class VentilatorOn(TimescaleModel):
    ventilator = models.ForeignKey(Ventilator, on_delete=models.CASCADE)
    is_on = models.BooleanField(default=False)


class LightOn(TimescaleModel):
    light = models.ForeignKey(Light, on_delete=models.CASCADE)
    is_on = models.BooleanField(default=False)
