"""
This module defines the `v1/room` endpoint for the API.
"""

# django imports
from django.http import Http404

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# API imports
from api.serializers.room_details import RoomDetailSerializer
from api.models import Room


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

        Raises:
            Http404: Room does not exist.

        Returns:
            Room: Record in the database.
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
        """
        post = self.get_object(identifier)
        serializer = RoomDetailSerializer(post)
        return Response(serializer.data)

    def put(self, request, identifier):
        """
        Updates room information. Used on EDITION. This method expects to
        receive the parameters specified in `jsons/rooms/put.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        post = self.get_object(identifier)
        serializer = RoomDetailSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
