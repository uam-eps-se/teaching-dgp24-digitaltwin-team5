"""
This module defines base models for the database.
"""

from django.db import models


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


class DoorConnectsRoom(models.Model):
    """
    Model representation for a connection between a door and up to two rooms.
    """

    door = models.ForeignKey(Door, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
