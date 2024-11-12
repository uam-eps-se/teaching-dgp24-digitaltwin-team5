"""
This module defines models for events related to devices.
"""

from api.models.base import Window, Door, Ventilator, Light
from django.db import models
from timescale.db.models.models import TimescaleModel


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
