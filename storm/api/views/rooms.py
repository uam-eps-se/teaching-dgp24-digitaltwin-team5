"""
This module defines the `v1/rooms` endpoint for the API.
"""

# regular imports
import json

# django imports
from django.http import Http404

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request

# API imports
from api.serializers import DataSerializer
from api.models import Room, Door, Ventilator, Light, Window
from api.models import DoorConnectsRoom

import api.views.utils as sse


class RoomsAPIView(APIView):
    """
    Defines views for all end-points associated to generic room information
    that is shown on the dashboard.
    """

    allowed_methods = ["GET", "POST", "DELETE"]

    def get_object(self, pk):
        """
        Retrieves a room with the given pk.

        Args:
            pk (int): Room identifier.

        Raises:
            Http404: Room does not exist.
        """
        try:
            return Room.objects.get(pk=pk)
        except Exception as exc:
            raise Http404(f"Room with id {pk} does not exist!") from exc

    def get(self, *_):
        """
        Retrieves a list of all existent rooms for the main dashboard.
        """
        return Response(DataSerializer.rooms())

    def post(self, request: Request):
        """
        Creates a new room from the given request. Used on CREATION.

        This method expects to receive the parameters specified in
        `jsons/rooms/post.json`. Devices sent via this endpoint can be either
        of the following:

        "devices": ["type": [{"name": str}, {"id": int}, ...], ...]

        An entry with the "name" field signifies the creation of a new
        device, and an entry with the "id" field signifies the association of
        an existent device with the room. For "type", it can be "windows",
        "ventilators", "lights" or "doors".

        Args:
            request (dict): A JSON-like dictionary.

        """

        # Dictionary with methods for all devices
        device_manager = {
            "windows": self._add_windows,
            "doors": self._add_doors,
            "ventilators": self._add_ventilators,
            "lights": self._add_lights,
        }

        # Obtain request parameters
        name = request.data.get("name", None)
        size = request.data.get("size", None)
        devices = request.data.get("devices", None)

        # Error Case: Missing Parameters
        if name is None or size is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Create the room before appending devices
        room = Room(name=name, size=size)
        room.save()

        # Append devices to room
        if devices is not None:
            devices = json.loads(devices)

            for key in devices:
                func = device_manager.get(key, None)
                if not func:
                    return Response(
                        f"Incorrect device type: {key}",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                func(devices[key], room)

        sse.send(sse.CHANNEL_SUMMARY)
        sse.send(sse.CHANNEL_CONTEXT)

        return Response(f"Room {room.name} created successfully with id {room.id}!")

    def delete(self, request: Request):
        """
        Removes a room from the database. This method expects to receive
        the parameters specified in `jsons/rooms/delete.json`.

        Args:
            request (dict): A JSON-like dictionary.

        """
        room = self.get_object(request.data.get("id", None))
        room.delete()

        sse.send(sse.CHANNEL_SUMMARY)
        sse.send(sse.CHANNEL_CONTEXT)
        sse.send(sse.CHANNEL_DEVICES, event=sse.DEVS)
        sse.send(sse.CHANNEL_DEVICES, event=sse.DOORS)

        return Response(
            f"Room with id {request.data.get("id", None)} successfully deleted!",
            status=status.HTTP_204_NO_CONTENT,
        )

    def _add_doors(self, doors: list[dict], room):
        """
        Handler method to add a set of doors to the database.

        Args:
            doors (list[dict]): List of doors associated to room.
            room: Room which contains doors.
        """

        for d in doors:
            identifier = d.get("id", None)
            name = d.get("name", None)

            if identifier is None:  # New door and connection
                if name is not None:
                    door = Door(name=name)
                    door.save()
                    conn = DoorConnectsRoom(door=door, room=room)
                    conn.save()

            else:  # Create connection if possible
                door = Door.objects.filter(id=identifier).first()
                if (
                    door is not None
                    and DoorConnectsRoom.objects.filter(door=door).count() < 2
                ):
                    conn = DoorConnectsRoom(door=door, room=room)
                    conn.save()

    def _add_windows(self, windows: list[dict], room):
        """
        Handler method to add a set of windows to the database.

        Args:
            windows (list[dict]): List of windows associated to room.
            room: Room which contains windows.
        """
        for w in windows:
            identifier = w.get("id", None)
            name = w.get("name", None)

            if identifier is None:  # New window
                if name is not None:
                    window = Window(name=name, room=room)
                    window.save()

            else:  # Update ownership on unassigned window
                window = Window.objects.filter(id=identifier).first()
                if window is not None:
                    window.room = room if window.room is None else window.room
                    window.save()

    def _add_ventilators(self, ventilators: list[dict], room):
        """
        Handler method to add a set of ventilators to the database.

        Args:
            ventilators (list[dict]): List of ventilators associated to room.
            room: Room which contains ventilators.
        """
        for v in ventilators:
            identifier = v.get("id", None)
            name = v.get("name", None)

            if identifier is None:  # New ventilator
                if name is not None:
                    vent = Ventilator(name=name, room=room)
                    vent.save()

            else:  # Update ownership on unassigned ventilator
                vent = Ventilator.objects.filter(id=identifier).first()
                if vent is not None:
                    vent.room = room if vent.room is None else vent.room
                    vent.save()

    def _add_lights(self, lights: list[dict], room):
        """
        Handler method to add a set of lights to the database.

        Args:
            lights (list[dict]): List of lights associated to room.
            room: Room which contains lights.
        """
        # Process each light in request
        for light in lights:
            identifier = light.get("id", None)
            name = light.get("name", None)

            # If no id is received, create new window for the room
            if identifier is None:
                if name is not None:
                    l_ = Light(name=light["name"], room=room)
                    l_.save()
            # If an id is received,
            # update ownership for an empty ventilator when possible
            else:
                l_ = Light.objects.filter(id=identifier).first()
                if l_ is not None:
                    l_.room = room if l_.room is None else l_.room
                    l_.save()
