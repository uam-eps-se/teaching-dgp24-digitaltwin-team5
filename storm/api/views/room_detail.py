"""
This module defines the `v1/room` endpoint for the API.
"""

# django imports
from django.http import Http404

# restframework imports
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status

# API imports
from api.serializers import DataSerializer
from api.models import Room

import api.views.utils as sse


class RoomDetailAPIView(APIView):
    """
    Defines views for all end-points associated to real-time room information
    that is shown on the room details page.
    """

    allowed_methods = ["GET", "PUT"]

    def get_object(self, pk):
        """
        Retrieves a room with the given pk.

        Args:
            pk (int): Room identifier.

        """
        try:
            return Room.objects.get(pk=pk)
        except Exception as exc:
            raise Http404(f"Room with id {pk} does not exist!") from exc

    def get(self, _, identifier):
        """
        Retrieve detailed room information.

        Args:
            identifier (int): Room identifier.

        Raises:
            Http404: Room does not exist.
        """
        try:
            return Response(DataSerializer.room(identifier=identifier))
        except Exception as exc:
            raise Http404(f"Room with id {identifier} does not exist!") from exc

    def put(self, request: Request, identifier):
        """
        Updates room information. Used on EDITION. This method expects to
        receive the parameters specified in `jsons/rooms/put.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        room = self.get_object(identifier)

        name = request.data.get("name", None)
        size = request.data.get("size", None)

        room.name = name if name is not None else room.name
        room.size = size if size is not None else room.size
        room.save()
        sse.send(sse.CHANNEL_SUMMARY)
        sse.send(sse.CHANNEL_CONTEXT)
        sse.send(f"{sse.CHANNEL_ROOM}-{room.id}")

        return Response(status=status.HTTP_200_OK)
