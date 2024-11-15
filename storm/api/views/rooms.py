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
from api.serializers.room_dashboard import RoomDashboardSerializer
from api.models import Room, Door, Ventilator, Light, Window
from api.models import DoorConnectsRoom


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

        Returns:
            Room: Record in the database.
        """
        try:
            return Room.objects.get(pk=pk)
        except Exception as exc:
            raise Http404(f"Room with id {pk} does not exist!") from exc

    def get(self, *_):
        """
        Retrieves a list of all existent rooms for the main dashboard.
        """
        rooms = Room.objects.all()
        serializer = RoomDashboardSerializer(rooms, many=True)
        return Response(serializer.data)

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

        devices = json.loads(devices)

        # Append devices to room
        for key in devices:
            device_manager[key](devices[key], room)

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
        # Process each door in request
        for d in doors:
            identifier = d.get("id", None)
            name = d.get("name", None)
            # If no id is received, create new door and connection
            if identifier is None:
                if name is not None:
                    d_ = Door(name=name)
                    d_.save()
                    d__ = DoorConnectsRoom(door=d_, room=room)
                    d__.save()

            # If an id is received, create a connection when possible
            else:
                d_ = Door.objects.filter(id=identifier).first()
                if (
                    d_ is not None
                    and DoorConnectsRoom.objects.filter(door=d_).count() < 2
                ):
                    d__ = DoorConnectsRoom(door=d_, room=room)
                    d__.save()

    def _add_windows(self, windows: list[dict], room):
        """
        Handler method to add a set of windows to the database.

        Args:
            windows (list[dict]): List of windows associated to room.
            room: Room which contains windows.
        """
        # Process each window in request
        for w in windows:
            identifier = w.get("id", None)
            name = w.get("name", None)

            # If no id is received, create new window for the room
            if identifier is None:
                if name is not None:
                    w_ = Window(name=name, room=room)
                    w_.save()
            # If an id is received, update ownership for an empty window
            else:
                w_ = Window.objects.filter(id=identifier).first()

                if w_ is not None:
                    w_.room = room if w_.room is None else w_.room
                    w_.save()

    def _add_ventilators(self, ventilators: list[dict], room):
        """
        Handler method to add a set of ventilators to the database.

        Args:
            ventilators (list[dict]): List of ventilators associated to room.
            room: Room which contains ventilators.
        """
        # Process each ventilator in request
        for v in ventilators:
            identifier = v.get("id", None)
            name = v.get("name", None)

            # If no id is received, create new window for the room
            if identifier is None:
                if name is not None:
                    v_ = Ventilator(name=name, room=room)
                    v_.save()
            # If an id is received,
            # update ownership for an empty ventilator when possible
            else:
                v_ = Ventilator.objects.filter(id=identifier).first()

                if v_ is not None:
                    v_.room = room if v_.room is None else v_.room
                    v_.save()

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
