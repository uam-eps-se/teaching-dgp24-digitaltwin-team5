"""
This module defines unit tests for the `v1/devices` endpoint.
"""

# restframework imports
from rest_framework import status

# API imports
from api.tests.base import Base
from api.models import Window


class DevicesTest(Base):
    """
    Class representation of unit tests to run.
    """

    def test01_get(self):
        """Test Case 01: Devices GET Request"""
        url = "/v1/devices"

        # Empty GET
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data, {"windows": [], "ventilators": [], "lights": []}
        )

        # GET request with free device
        window = Window(name="Ventana")
        window.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data,
            {
                "windows": [{"id": window.id, "name": window.name}],
                "ventilators": [],
                "lights": [],
            },
        )

    def test02_post(self):
        """Test Case 02: Devices POST Request"""
        url = "/v1/devices"

        # Incorrect number of parameters
        self.assertEqual(
            self.client.post(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            self.client.post(url, {"room_id": self.rooms[0].id}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            self.client.post(
                url, {"name": "Ventana", "room_id": self.rooms[0].id}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect device type
        self.assertEqual(
            self.client.post(
                url, {"name": "Ventana", "room_id": self.rooms[0].id, "type": "patata"}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect room identifier
        self.assertEqual(
            self.client.post(
                url, {"name": "Ventana", "room_id": -1, "type": "window"}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Correct device creation
        self.assertEqual(
            self.client.post(
                url, {"name": "Ventana", "room_id": self.rooms[0].id, "type": "window"}
            ).status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            self.client.post(
                url, {"name": "Luz", "room_id": self.rooms[0].id, "type": "light"}
            ).status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            self.client.post(
                url,
                {
                    "name": "Ventilador",
                    "room_id": self.rooms[0].id,
                    "type": "ventilator",
                },
            ).status_code,
            status.HTTP_200_OK,
        )

    def test03_put(self):
        """Test Case 03: Devices PUT Request"""
        url = "/v1/devices"

        # Incorrect number of parameters
        self.assertEqual(
            self.client.put(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            self.client.put(url, {"room_id": self.rooms[0].id}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            self.client.put(url, {"id": -1, "room_id": self.rooms[0].id}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect device type
        self.assertEqual(
            self.client.put(
                url,
                {
                    "id": self.windows[0].id,
                    "room_id": self.rooms[0].id,
                    "type": "patata",
                },
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect room identifier
        self.assertEqual(
            self.client.put(
                url, {"id": self.windows[0].id, "room_id": -1, "type": "window"}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect device identifier
        self.assertEqual(
            self.client.put(
                url, {"id": -1, "room_id": self.rooms[0].id, "type": "window"}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Device assignation to existent room
        self.assertEqual(
            self.client.put(
                url,
                {
                    "id": self.windows[0].id,
                    "room_id": self.rooms[2].id,
                    "type": "window",
                },
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Correct device assignation
        window = Window(name="Ventana")
        window.save()

        self.assertEqual(
            self.client.put(
                url, {"id": window.id, "room_id": self.rooms[0].id, "type": "window"}
            ).status_code,
            status.HTTP_200_OK,
        )

    def test04_delete(self):
        """Test Case 04: Devices DELETE Request"""
        url = "/v1/devices"

        # Missing parameters
        self.assertEqual(
            self.client.delete(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        # Invalid type
        self.assertEqual(
            self.client.delete(url, {"id": 1, "type": "ventanation"}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Invalid id
        self.assertEqual(
            self.client.delete(url, {"id": -1, "type": "window"}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Correct deletion
        self.assertEqual(
            self.client.delete(
                url, {"id": self.windows[0].id, "type": "window"}
            ).status_code,
            status.HTTP_200_OK,
        )

    def test05_patch(self):
        """Test Case 05: Devices PATCH Request"""
        url = "/v1/devices"

        # Missing parameters
        self.assertEqual(
            self.client.patch(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        # Invalid type
        self.assertEqual(
            self.client.patch(
                url, {"id": 1, "type": "ventanation", "action": True}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Invalid id
        self.assertEqual(
            self.client.patch(
                url, {"id": -1, "type": "window", "action": True}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Invalid action
        self.assertEqual(
            self.client.patch(
                url, {"id": self.windows[0].id, "type": "window", "action": "potato"}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Valid patch
        self.assertEqual(
            self.client.patch(
                url,
                {"id": self.windows[0].id, "type": "window", "action": True},
                format="json",
            ).status_code,
            status.HTTP_200_OK,
        )
