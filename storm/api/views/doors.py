"""
This module defines the `v1/doors` endpoint for the API.
"""

# django imports
from django.utils import timezone

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request

# API imports
from api.serializers import DataSerializer
from api.models import Room, Door
from api.models import DoorConnectsRoom
from api.models import DoorOpen
from api.views.utils import send
from api.views.utils import CHANNEL_ROOM, CHANNEL_SUMMARY, CHANNEL_DEVICES
from api.views.utils import DOORS


class DoorsAPIView(APIView):
    """
    Defines views for all end-points associated to doors, which chan be owned
    by up to two rooms.
    """

    allowed_methods = ["GET", "PUT", "POST", "DELETE", "PATCH"]

    def get(self, *_):
        """
        Retrieves all doors with less than two rooms. Used on CREATION and
        EDITION. This method expects to receive the parameters specified in
        `jsons/doors/get.json`.
        """
        return Response(DataSerializer.doors())

    def post(self, request: Request):
        """
        Creates a new door. Used on EDITION. This method expects to receive the
        parameters specified in `jsons/doors/post.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        # Obtain request parameters
        name = request.data.get("name", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if name is None or room_id is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door(name=name)
        door.save()
        droom = DoorConnectsRoom(door=door, room=room)
        droom.save()

        send(CHANNEL_DEVICES, event=DOORS)
        send(CHANNEL_SUMMARY)
        send(f"{CHANNEL_ROOM}-{room.id}")
        return Response(f"Door {door.name} created successfully!")

    def put(self, request: Request):
        """
        Connects a door to a room new door. Used on EDITION and CREATION.
        This method expects to receive the parameters specified in
        `jsons/doors/put.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        # Obtain request parameters
        identifier = request.data.get("id", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if identifier is None or room_id is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=identifier).first()

        # Error Case: Invalid door
        if door is None:
            return Response("Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        connected_rooms = DoorConnectsRoom.objects.filter(door=door).values_list(
            "room", flat=True
        )

        # Error Case: Invalid connections
        if room_id in connected_rooms:
            return Response(
                f"Given room id {room_id} is already connected to this door!",
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if connected_rooms.count() >= 2:
            return Response(
                f"Given door id {identifier} is connected to two rooms!",
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        droom = DoorConnectsRoom(door=door, room=room)
        droom.save()

        send(CHANNEL_DEVICES, event=DOORS)
        send(CHANNEL_SUMMARY)
        send(f"{CHANNEL_ROOM}-{room.id}")
        return Response(f"Door {door.name} updated successfully!")

    def delete(self, request: Request):
        """
        Deletes a door. Used on EDITION. This method expects to receive the
        parameters specified in `jsons/doors/put.json`.

        Args:
            request (dict): A JSON-like dictionary
        """
        # Obtain request parameters
        identifier = request.data.get("id", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if identifier is None or room_id is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=identifier).first()

        # Error Case: Invalid door
        if door is None:
            return Response("Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        connected_rooms = DoorConnectsRoom.objects.filter(door=door).values()
        droom = DoorConnectsRoom.objects.filter(door=door, room=room).first()

        # Error Case: Not connected door
        if droom is None:
            return Response(
                "Given door is not connected to the room!",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete Door on last connection
        if connected_rooms.count() == 1:
            door.delete()
        else:
            droom.delete()

        send(CHANNEL_DEVICES, DOORS)
        send(CHANNEL_SUMMARY)
        for droom in connected_rooms:
            send(f"{CHANNEL_ROOM}-{droom['room_id']}")
        return Response(f"Door {door.name} updated successfully!")

    def patch(self, request: Request):
        """
        Updates a door status. Used on CONTROL PANEL.

        This method expects to receive the parameters specified in
        `jsons/doors/patch.json`.

        Args:
            request (dict): A JSON-like dictionary
        """
        # Obtain request parameters
        identifier = request.data.get("id", None)
        action = request.data.get("action", None)

        # Error Case: Missing Parameters
        if identifier is None or action is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(action, bool):
            return Response("Invalid action!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=identifier).first()

        # Error Case: Invalid door
        if door is None:
            return Response("Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        door_open = DoorOpen(door=door, time=timezone.now(), is_open=action)
        door_open.save()

        connected_rooms = DoorConnectsRoom.objects.filter(door=door).values()

        send(CHANNEL_SUMMARY)
        for droom in connected_rooms:
            send(f"{CHANNEL_ROOM}-{droom['room_id']}")
        return Response(f"Door {door.name} assigned the status {action}!")
