from django.apps import AppConfig
import signal
import sys
from threading import Thread, Event
import random
from django.utils import timezone
import pytz

class RealTimeModelUpdater(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stopped = Event()

    def update_people(self):
        from api.models import PeopleInRoom, Room
        for r in Room.objects.all():

            # Get most recent people value
            _ = PeopleInRoom.objects.filter(room=r).last()

            if _ is None:
                # Generate a first value on no record
                people = PeopleInRoom(
                    room=r,
                    time=timezone.now(),
                    no_people_in_room=random.choice([0, 1, 2, 3, 4])
                )
            else:
                # Update value randomly
                np = random.choices(
                    population=[-3, -2, -1, 0, 1, 2, 3],
                    weights=[1, 2, 3, 5, 3, 2, 1]
                )[0]
                np += _.no_people_in_room

                # Assign value "realistically"
                if np < 0:
                    people = PeopleInRoom(
                        room=r, time=timezone.now(), no_people_in_room=0)
                elif np > 30:
                    people = PeopleInRoom(
                        room=r, time=timezone.now(), no_people_in_room=30)
                else:
                    people = PeopleInRoom(
                        room=r, time=timezone.now(), no_people_in_room=np)
            people.save()

    def update_co2(self):
        from api.models import Co2InRoom, Room
        for r in Room.objects.all():
            # Get most recent co2 value
            _ = Co2InRoom.objects.filter(room=r).last()

            if _ is None:
                # Generate a first value on no record
                co2 = Co2InRoom(
                    room=r,
                    time=timezone.now(),
                    co2=random.choice([400, 500, 600, 700, 800])
                )
            else:
                # Update value randomly
                co2_val = random.choices(
                    population=[-60, -30, -15, 0, 15, 30, 60],
                    weights=[1, 2, 3, 5, 3, 2, 1]
                )[0]
                co2_val += _.co2

                # Update values "realistically"
                if co2_val < 300:
                    co2 = Co2InRoom(
                        room=r, time=timezone.now(), co2=300)
                elif co2_val > 1200:
                    co2 = Co2InRoom(
                        room=r, time=timezone.now(), co2=1200)
                else:
                    co2 = Co2InRoom(
                        room=r, time=timezone.now(), co2=co2_val)
            co2.save()

    def update_temperature(self):
        from api.models import TemperatureInRoom, Room
        for r in Room.objects.all():
            # Get most recent temp value
            _ = TemperatureInRoom.objects.filter(room=r).last()

            if _ is None:
                # Generate a first value on no record
                tmp = TemperatureInRoom(
                    room=r,
                    time=timezone.now(),
                    temp=random.choice([15, 16, 17, 18, 19])
                )
            else:
                # Update value randomly
                tmp_val = random.choices(
                    population=[-0.7, -0.3, -0.1, 0, 0.1, 0.3, 0.7],
                    weights=[1, 2, 3, 5, 3, 2, 1]
                )[0]
                tmp_val += _.temp

                # Update values "realistically"
                if tmp_val < -20:
                    tmp = TemperatureInRoom(
                        room=r, time=timezone.now(), temp=-20)
                elif tmp_val > 70:
                    tmp = TemperatureInRoom(
                        room=r, time=timezone.now(), temp=70)
                else:
                    tmp = TemperatureInRoom(
                        room=r, time=timezone.now(), temp=tmp_val)
            tmp.save()

    def run(self):
        while not self.stopped.wait(5):
            self.update_people()
            self.update_co2()
            self.update_temperature()


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def handle(self, sig, frame):
        self.thread.stopped.set()
        sys.exit(0)

    def ready(self):
        self.thread = RealTimeModelUpdater()
        self.thread.start()
        signal.signal(signal.SIGINT, self.handle)
