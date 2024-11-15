"""
This module defines the `v1/devices` endpoint for the API.
"""

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request

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
                        "id": a.id,
                        "type": a.type,
                        "content": a.content,
                        "time": a.time.timestamp(),
                        "roomId": a.room.id,
                        "roomName": a.room.name,
                    }
                    for a in Alert.objects.filter(received=False)
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

        ids = request.data.get("ids")

        alerts = Alert.objects.filter(id__in=ids)

        for alert in alerts:
            alert.received = True
            alert.save()

        return Response("Alerts received successfully!")
