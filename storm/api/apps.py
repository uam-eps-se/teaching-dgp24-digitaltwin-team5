"""
This module handles the initialization of the REST API and starts a thread for
automatic event and metric generation every five seconds.
"""

import decimal
import random

# import signal
# import sys
from threading import Thread, Event
from django.utils import timezone
from django.apps import AppConfig


class RealTimeModelUpdater(Thread):
    """
    This class is a wrapper for "real" data generation done by a dedicated
    worker thread.
    """

    def __init__(self):
        """
        Constructor method for this class.
        """
        Thread.__init__(self)
        self.stopped = Event()

    def run(self):
        """
        Main loop for this class. Executes data generation every five
        seconds for all records in the database.
        """
        while not self.stopped.wait(5):
            self.update_people()
            self.update_co2()
            self.update_temperature()

    def update_people(self):
        """
        Generates new people values for each room.
        """
        from api.models.base import Room
        from api.models.metrics import PeopleInRoom

        for r in Room.objects.all():

            # Get most recent people value
            _ = PeopleInRoom.objects.filter(room=r).last()

            if _ is None:
                # Generate a first value on no record
                people = PeopleInRoom(
                    room=r,
                    time=timezone.now(),
                    no_people_in_room=random.choice([0, 1, 2, 3, 4]),
                )
            else:
                # Update value randomly
                np = random.choices(
                    population=[-3, -2, -1, 0, 1, 2, 3], weights=[1, 2, 3, 5, 3, 2, 1]
                )[0]
                np += _.no_people_in_room

                # Assign value "realistically"
                if np < 0:
                    people = PeopleInRoom(
                        room=r, time=timezone.now(), no_people_in_room=0
                    )
                elif np > 30:
                    people = PeopleInRoom(
                        room=r, time=timezone.now(), no_people_in_room=30
                    )
                else:
                    people = PeopleInRoom(
                        room=r, time=timezone.now(), no_people_in_room=np
                    )
            people.save()

    def update_co2(self):
        """
        Generates new Co2 values for each room.
        """
        from api.models.base import Room
        from api.models.metrics import Co2InRoom

        for r in Room.objects.all():
            # Get most recent co2 value
            _ = Co2InRoom.objects.filter(room=r).last()

            if _ is None:
                # Generate a first value on no record
                co2 = Co2InRoom(
                    room=r,
                    time=timezone.now(),
                    co2=random.choice([400, 500, 600, 700, 800]),
                )
            else:
                # Update value randomly
                co2_val = random.choices(
                    population=[-60, -30, -15, 0, 15, 30, 60],
                    weights=[1, 2, 3, 5, 3, 2, 1],
                )[0]
                co2_val += _.co2

                # Update values "realistically"
                if co2_val < 300:
                    co2 = Co2InRoom(room=r, time=timezone.now(), co2=300)
                elif co2_val > 1200:
                    co2 = Co2InRoom(room=r, time=timezone.now(), co2=1200)
                else:
                    co2 = Co2InRoom(room=r, time=timezone.now(), co2=co2_val)
            co2.save()

    def update_temperature(self):
        """
        Generates new temperature values for each room.
        """
        from api.models.base import Room
        from api.models.metrics import TemperatureInRoom

        for r in Room.objects.all():
            # Get most recent temp value
            _ = TemperatureInRoom.objects.filter(room=r).last()

            if _ is None:
                # Generate a first value on no record
                tmp = TemperatureInRoom(
                    room=r,
                    time=timezone.now(),
                    temp=random.choice([15, 16, 17, 18, 19]),
                )
            else:
                # Update value randomly
                tmp_val = decimal.Decimal(
                    random.choices(
                        population=[-0.7, -0.3, -0.1, 0, 0.1, 0.3, 0.7],
                        weights=[1, 2, 3, 5, 3, 2, 1],
                    )[0]
                )
                tmp_val += _.temp

                # Update values "realistically"
                if tmp_val < -20:
                    tmp = TemperatureInRoom(room=r, time=timezone.now(), temp=-20)
                elif tmp_val > 70:
                    tmp = TemperatureInRoom(room=r, time=timezone.now(), temp=70)
                else:
                    tmp = TemperatureInRoom(room=r, time=timezone.now(), temp=tmp_val)
            tmp.save()


class ApiConfig(AppConfig):
    """
    This class specifies the configuration of storm's REST API.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def handle(self, *_):
        """
        Graceful shutdown method for the data generation thread.
        """
        # self.thread.stopped.set()
        # sys.exit(0)
        pass

    def ready(self):
        """
        Creates a data-generation thread, executed at start-up time. Implies
        the need for the --no-reload flag when starting the server.
        """
        # self.thread = RealTimeModelUpdater()
        # self.thread.start()
        # signal.signal(signal.SIGINT, self.handle)
        pass
