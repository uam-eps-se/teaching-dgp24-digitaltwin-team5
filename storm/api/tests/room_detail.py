"""
This module defines unit tests for the `v1/room` endpoint.
"""

import decimal
from django.urls import reverse
from rest_framework import status
from api.tests.base import Base
from api.models import Alert


class RoomDetailTest(Base):
    """
    Class representation of unit tests to run.
    """

    def test01_get(self):
        """Test Case 01: Room GET request"""
        url = reverse("room", kwargs={"identifier": -90})

        # Invalid identifier
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Correct request
        url = f"/v1/room/{self.rooms[0].id}/"
        response = self.client.get(url)
        response_ = {
            "id": self.rooms[0].id,
            "name": self.rooms[0].name,
            "size": self.rooms[0].size,
            "temperature_status": Alert.AlertType.INFO,
            "co2_status": Alert.AlertType.INFO,
            "devices": {
                "doors": {
                    self.doors[0].id: {
                        "name": "Door 0",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                    self.doors[-1].id: {
                        "name": "Door 2",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                },
                "windows": {
                    self.windows[0].id: {
                        "name": "Window 0",
                        "current": True,
                        "times": [self.time.timestamp()],
                        "values": [True],
                    },
                    self.windows[1].id: {
                        "name": "Window 1",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                    self.windows[2].id: {
                        "name": "Window 2",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                },
                "ventilators": {
                    self.ventilators[0].id: {
                        "name": "Ventilator 0",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                    self.ventilators[1].id: {
                        "name": "Ventilator 1",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                    self.ventilators[2].id: {
                        "name": "Ventilator 2",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                },
                "lights": {
                    self.lights[0].id: {
                        "name": "Light 0",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                    self.lights[1].id: {
                        "name": "Light 1",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                    self.lights[2].id: {
                        "name": "Light 2",
                        "current": False,
                        "times": [],
                        "values": [],
                    },
                },
            },
            "metrics": {
                "people": {"times": [self.time.timestamp()], "values": [3]},
                "co2": {"times": [self.time.timestamp()], "values": [500]},
                "temperature": {
                    "times": [self.time.timestamp()],
                    "values": [decimal.Decimal("22.10")],
                },
            },
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, response_)

    def test02_put(self):
        """Test Case 01: Room PUT request"""
        url = f"/v1/room/{self.rooms[0].id}/"
        self.assertEqual(
            self.client.put(url, {"name": "RoomRoom", "size": 90}).status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            self.client.put(url, {"size": "Room"}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )
