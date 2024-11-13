"""
This module defines the `v1/doors` endpoint for the API.
"""

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request

# API imports
from api.models.metrics import PeopleInRoom, TemperatureInRoom, Co2InRoom
from api.models.base import Room


class MetricsAPIView(APIView):
    """
    Defines views for all end-points associated to sensor generated metrics.
    """

    allowed_methods = ["POST", "POST"]

    def post(self, request: Request):
        """
        Creates new metrics for rooms. This method expects to receive the
        parameters specified in `jsons/metrics/post.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        mets = {
            "people": (PeopleInRoom, "no_people_in_room"),
            "co2": (Co2InRoom, "co2"),
            "temperature": (TemperatureInRoom, "temp"),
        }

        for key, data in request.data.items():
            room = Room.objects.filter(id=int(key)).first()

            for metric, readings in data.items():
                model, attr = mets[metric]
                for time, value in zip(readings["times"], readings["values"]):
                    model(**{"time": time, attr: value, "room": room}).save()

        return Response("Metrics updated successfully!")
