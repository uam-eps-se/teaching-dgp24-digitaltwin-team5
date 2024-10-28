from django.contrib import admin
from api.models import *
# Register your models here.
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