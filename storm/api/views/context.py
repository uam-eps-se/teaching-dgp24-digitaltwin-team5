"""
This module defines the `v1/devices` endpoint for the API.
"""

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status

# API imports
from api.models import Room, Alert


class ContextAPIView(APIView):
    """
    Defines views for all end-points associated to room context extraction,
    usually for alerts of various kinds.
    """

    allowed_devices = ["GET", "PUT"]

    def get(self, *_):
        """
        Retrieves base room information and unread alerts.

        """
        return Response(
            {
                "rooms": [
                    {"id": room.id, "name": room.name} for room in Room.objects.all()
                ],
                "alerts": [
                    {
                        "id": alert.id,
                        "type": alert.type,
                        "content": alert.content,
                        "time": alert.time.timestamp(),
                        "roomId": alert.room.id,
                        "roomName": alert.room.name,
                    }
                    for alert in Alert.objects.filter(received=False)
                ],
            }
        )

    def put(self, request: Request):
        """
        Marks a set of alerts as received. This method expects to receive the
        parameters specified in`jsons/context/put.json`.

        Args:
            request (dict): A JSON-like dictionary
        """

        ids = request.data.get("ids", None)

        if ids is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        alerts = Alert.objects.filter(id__in=ids)
        for alert in alerts:
            alert.received = True
            alert.save()

        return Response("Alerts received successfully!")
