"""
This module defines a base class used to populate the teest database.
"""

from django.utils import timezone
from rest_framework.test import APITestCase

from api.models import Room, Ventilator, Light, Window, Door
from api.models import TemperatureInRoom, Co2InRoom, PeopleInRoom
from api.models import DoorConnectsRoom
from api.models import WindowOpen

ROOMS = 3
DEVS_PER_ROOM = 3


class Base(APITestCase):
    """
    Base class that sets up a database for test cases
    """

    @classmethod
    def setUpTestData(cls):
        """
        Populates the test database.
        """
        now = timezone.now()

        # Create Rooms
        cls.rooms = [Room(name=f"Room {i}", size=100 + i) for i in range(ROOMS)]
        Room.objects.bulk_create(cls.rooms)

        # Create Doors
        cls.doors = [Door(name=f"Door {i}") for i in range(ROOMS)]
        Door.objects.bulk_create(cls.doors)

        # Create & Assign Ventilators
        cls.ventilators = [
            Ventilator(name=f"Ventilator {i}", room=cls.rooms[int(i / ROOMS)])
            for i in range(ROOMS * DEVS_PER_ROOM)
        ]
        Ventilator.objects.bulk_create(cls.ventilators)

        # Create & Assign Lights
        cls.lights = [
            Light(name=f"Light {i}", room=cls.rooms[int(i / ROOMS)])
            for i in range(ROOMS * DEVS_PER_ROOM)
        ]
        Light.objects.bulk_create(cls.lights)

        # Create & Assign Windows
        cls.windows = [
            Window(name=f"Window {i}", room=cls.rooms[int(i / ROOMS)])
            for i in range(ROOMS * DEVS_PER_ROOM)
        ]
        Window.objects.bulk_create(cls.windows)

        # Connect Doors to Rooms
        for i, door in enumerate(cls.doors):
            DoorConnectsRoom(door=door, room=cls.rooms[i]).save()
            DoorConnectsRoom(door=door, room=cls.rooms[(i + 1) % ROOMS]).save()

        # Create random metrics
        for room in cls.rooms:
            TemperatureInRoom(room=room, time=now, temp=22.1).save()
            PeopleInRoom(room=room, time=now, no_people_in_room=3).save()
            Co2InRoom(room=room, time=now, co2=500).save()

        WindowOpen(time=now, window=cls.windows[0], is_open=True).save()

        super().setUpTestData()
