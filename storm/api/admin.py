"""
This module handles which models are added to the django administration page.
"""

from django.contrib import admin
from api.models.base import Room, Door, Ventilator, Light, Window
from api.models.base import DoorConnectsRoom
from api.models.metrics import PeopleInRoom, Co2InRoom, TemperatureInRoom
from api.models.events import DoorOpen, VentilatorOn, LightOn, WindowOpen


admin.site.register(Room)
admin.site.register(Door)
admin.site.register(Ventilator)
admin.site.register(Light)
admin.site.register(Window)

admin.site.register(DoorConnectsRoom)

admin.site.register(PeopleInRoom)
admin.site.register(Co2InRoom)
admin.site.register(TemperatureInRoom)

admin.site.register(DoorOpen)
admin.site.register(VentilatorOn)
admin.site.register(LightOn)
admin.site.register(WindowOpen)
