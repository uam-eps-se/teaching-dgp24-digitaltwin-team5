from api.models import *
from rest_framework import serializers

#
#   BASE MODELS
#


class RoomSerializer(serializers.ModelSerializer):
    devices = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "name", "size", "devices", "metrics"]

    def get_devices(self, obj):
        devs = {
            "doors": self._get_doors,
            "windows": self._get_windows,
            "ventilators": self._get_ventilators,
            "lights": self._get_lights,
        }
        return {k: devs[k](obj) for k in devs}

    def get_metrics(self, obj):
        mets = {
            "people": self._get_people,
            "co2": self._get_co2,
            "temperature": self._get_temperature,
        }
        return {k: mets[k](obj) for k in mets}

    def _get_doors():
        pass

    def _get_windows():
        pass

    def _get_ventilators():
        pass

    def _get_lights():
        pass

    def _get_people():
        pass

    def _get_co2():
        pass

    def _get_temperature():
        pass


class RoomDashboardSerializer(RoomSerializer):
    def _get_doors(self, obj):
        doors: dict = {"total": 0, "open": 0}

        for d in DoorConnectsRoom.objects.filter(room=obj.id):
            doors["total"] += 1
            _ = DoorOpen.objects.filter(door=d.door).last()
            if _ is not None and _.is_open:
                doors["open"] += 1

        return doors

    def _get_windows(self, obj):
        windows: dict = {"total": 0, "open": 0}

        for w in Window.objects.filter(room=obj.id):
            windows["total"] += 1
            _ = WindowOpen.objects.filter(window=w).last()
            if _ is not None and _.is_open:
                windows["open"] += 1

        return windows

    def _get_ventilators(self, obj):
        ventilators: dict = {"total": 0, "on": 0}

        for v in Ventilator.objects.filter(room=obj.id):
            ventilators["total"] += 1
            _ = VentilatorOn.objects.filter(ventilator=v).last()
            if _ is not None and _.is_on:
                ventilators["on"] += 1

        return ventilators

    def _get_lights(self, obj):
        lights: dict = {"total": 0, "on": 0}

        for light in Light.objects.filter(room=obj.id):
            lights["total"] += 1
            _ = LightOn.objects.filter(light=light).last()
            if _ is not None and _.is_on:
                lights["on"] += 1

        return lights

    def _get_people(self, obj):
        _ = PeopleInRoom.objects.filter(room=obj).last()
        return 0 if _ is None else _.no_people_in_room

    def _get_co2(self, obj):
        _ = Co2InRoom.objects.filter(room=obj).last()
        return 0 if _ is None else _.co2

    def _get_temperature(self, obj):
        _ = TemperatureInRoom.objects.filter(room=obj).last()
        return 0 if _ is None else _.temp


class RoomDetailSerializer(RoomSerializer):
    def _get_doors(self, obj):
        doors: dict = {}

        for d in DoorConnectsRoom.objects.filter(room=obj):
            data = DoorOpen.timescale.filter(door=d.door).time_bucket("time", "1 hour")

            doors[d.door.name] = {
                "id": d.door.id,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_open", flat=True)),
            }

        return doors

    def _get_windows(self, obj):
        windows: dict = {}

        for w in Window.objects.filter(room=obj):
            data = WindowOpen.timescale.filter(window=w).time_bucket("time", "1 hour")

            windows[w.name] = {
                "id": w.id,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_open", flat=True)),
            }

        return windows

    def _get_ventilators(self, obj):
        ventilators: dict = {}

        for v in Ventilator.objects.filter(room=obj):
            data = VentilatorOn.timescale.filter(ventilator=v).time_bucket(
                "time", "1 hour"
            )

            ventilators[v.name] = {
                "id": v.id,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_on", flat=True)),
            }

        return ventilators

    def _get_lights(self, obj):
        lights: dict = {}

        for light in Light.objects.filter(room=obj):
            data = LightOn.timescale.filter(light=light).time_bucket("time", "1 hour")

            lights[light.name] = {
                "id": light.id,
                "times": [
                    date.timestamp() for date in data.values_list("time", flat=True)
                ],
                "values": list(data.values_list("is_on", flat=True)),
            }

        return lights

    def _get_people(self, obj):

        data = PeopleInRoom.timescale.filter(room=obj).time_bucket("time", "1 hour")

        people = {
            "times": [date.timestamp() for date in data.values_list("time", flat=True)],
            "values": list(data.values_list("no_people_in_room", flat=True)),
        }

        return people

    def _get_temperature(self, obj):

        data = TemperatureInRoom.timescale.filter(room=obj).time_bucket(
            "time", "1 hour"
        )

        temps = {
            "times": [date.timestamp() for date in data.values_list("time", flat=True)],
            "values": list(data.values_list("temp", flat=True)),
        }

        return temps

    def _get_co2(self, obj):

        data = Co2InRoom.timescale.filter(room=obj).time_bucket("time", "1 hour")

        co2 = {
            "times": [date.timestamp() for date in data.values_list("time", flat=True)],
            "values": list(data.values_list("co2", flat=True)),
        }

        return co2


class WindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Window
        fields = ["id", "name"]


class LightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Light
        fields = ["id", "name"]


class VentilatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ventilator
        fields = ["id", "name"]


class DoorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Door
        fields = ["id", "name", "rooms"]
