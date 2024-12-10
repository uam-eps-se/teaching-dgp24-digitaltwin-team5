"""
This module defines the `v1/devices` endpoint for the API.
"""

# django imports
from django.utils import timezone
from django.db import models

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request

# API imports
from api.serializers.devices import WindowSerializer
from api.serializers.devices import VentilatorSerializer, LightSerializer
from api.models import Room, Ventilator, Light, Window
from api.models import VentilatorOn, LightOn, WindowOpen
from api.views.utils import send
from api.views.utils import CHANNEL_ROOM, CHANNEL_SUMMARY, CHANNEL_DEVICES
from api.views.utils import DEVS


class DevicesAPIView(APIView):
    """
    Defines views for all end-points associated to `individual` devices,
    which are only owned by one room.
    """

    allowed_devices = ["GET", "POST", "DELETE", "PUT", "PATCH"]

    def get(self, *_):
        """
        Retrieves all `individual` devices not owned by empty room.
        A non-associated device is the product of a non-empty room deletion.

        Used on room CREATION and EDITION.
        """

        # Dictionary with classes and serializers for all devices
        dmodels = {
            "windows": (Window, WindowSerializer),
            "ventilators": (Ventilator, VentilatorSerializer),
            "lights": (Light, LightSerializer),
        }
        data = {}

        # Serialize non-associated devices
        for key, (model, serializer) in dmodels.items():
            devs = model.objects.filter(room=None)
            data[key] = serializer(devs, many=True).data

        return Response(data)

    def post(self, request: Request):
        """
        Creates a new device of a given type. Used on EDITION.

        This method expects to receive the parameters specified in
        `jsons/devices/post.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """
        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        # Obtain request parameters
        name = request.data.get("name", None)
        room_id = request.data.get("room_id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if name is None or room_id is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {", ".join(dtypes.keys())}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        # Create and save device
        dev = dtypes[dtype](name=name, room=room)
        dev.save()

        send(CHANNEL_SUMMARY)
        send(f"{CHANNEL_ROOM}-{room.id}")
        return Response(f"Device {name} for room {room.name} succesfully created!")

    def put(self, request: Request):
        """
        Assigns a device to a room. Used on CREATION and EDITION.

        This method expects to receive the parameters specified in
        `jsons/devices/put.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """

        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        # Obtain request parameters
        identifier = request.data.get("id", None)
        room_id = request.data.get("room_id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if identifier is None or room_id is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {", ".join(dtypes.keys())}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        dev = dtypes[dtype].objects.filter(id=identifier).first()

        # Error case: Invalid device
        if dev is None:
            return Response("Invalid device id!", status=status.HTTP_400_BAD_REQUEST)
        if dev.room is not None:
            return Response(
                "Device already belongs to a room!", status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save device
        dev.room = room
        dev.save()

        send(CHANNEL_DEVICES, event=DEVS)
        send(CHANNEL_SUMMARY)
        send(f"{CHANNEL_ROOM}-{room.id}")
        return Response(f"Device {dev.name} assigned to room {room.name}!")

    def delete(self, request: Request):
        """
        Deletes a new device of a given type. Used on EDITION.

        This method expects to receive the parameters specified in
        `jsons/devices/delete.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """
        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        # Obtain request parameters
        identifier = request.data.get("id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if identifier is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {dtypes}", status=status.HTTP_400_BAD_REQUEST
            )

        # Remove device from the database
        dev = dtypes[dtype].objects.filter(id=identifier).first()

        # Error case: Invalid device
        if dev is None:
            return Response("Invalid device id!", status=status.HTTP_400_BAD_REQUEST)

        room_id = dev.room.id
        dev.delete()

        send(CHANNEL_SUMMARY)
        send(f"{CHANNEL_ROOM}-{room_id}")
        return Response("Device succesfully removed!")

    def patch(self, request: Request):
        """
        Updates a device status. Used on CONTROL PANEL.

        This method expects to receive the parameters specified in
        `jsons/devices/patch.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """
        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        dstatus: dict[str, models.Model] = {
            "window": WindowOpen,
            "ventilator": VentilatorOn,
            "light": LightOn,
        }

        dactions: dict[str, str] = {
            "window": "is_open",
            "ventilator": "is_on",
            "light": "is_on",
        }

        # Obtain request parameters
        identifier = request.data.get("id", None)
        dtype = request.data.get("type", None)
        action = request.data.get("action", None)

        # Error Case: Missing Parameters
        if identifier is None or action is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {", ".join(dtypes.keys())}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        dev = dtypes[dtype].objects.filter(id=identifier).first()

        # Error case: Invalid device
        if dev is None:
            return Response("Invalid device id!", status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(action, bool):
            return Response("Invalid action!", status=status.HTTP_400_BAD_REQUEST)

        # Create new dev status
        ds = dstatus[dtype](time=timezone.now())
        setattr(ds, dtype, dev)
        setattr(ds, dactions[dtype], action)
        ds.save()

        send(CHANNEL_SUMMARY)
        send(f"{CHANNEL_ROOM}-{dev.room.id}")
        return Response(f"Device {dev.name} assigned the status {action}!")
