"""
This module defines unit tests for the `v1/doors` endpoint.
"""

from rest_framework import status
from api.tests.base import Base
from api.models import Door, DoorConnectsRoom


class DoorsTest(Base):
    """
    Class representation of unit tests to run.
    """

    def test01_get(self):
        """Test Case 01: Doors GET Request"""
        url = "/v1/doors"

        # Empty GET
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # GET request with available doors
        door1 = Door(name="Door A")
        door2 = Door(name="Door B")
        door1.save()
        door2.save()

        DoorConnectsRoom(door=door1, room=self.rooms[0]).save()

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data,
            [
                {"id": door1.id, "name": door1.name, "rooms": [self.rooms[0].id]},
                {"id": door2.id, "name": door2.name, "rooms": []},
            ],
        )

    def test02_post(self):
        """Test Case 02: Doors POST Request"""
        url = "/v1/doors"

        # Incorrect number of parameters
        self.assertEqual(
            self.client.post(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            self.client.post(url, {"room_id": self.rooms[1].id}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            self.client.post(url, {"name": "Puerta"}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect room identifier
        self.assertEqual(
            self.client.post(url, {"name": "Puerta", "room_id": -1}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Correct door creation
        self.assertEqual(
            self.client.post(
                url, {"name": "Puerta", "room_id": self.rooms[0].id}
            ).status_code,
            status.HTTP_200_OK,
        )

    def test03_put(self):
        """Test Case 03: Doors PUT Request"""
        url = "/v1/doors"

        # Incorrect number of parameters
        self.assertEqual(
            self.client.put(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            self.client.put(url, {"room_id": self.rooms[1].id}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect door identifier
        self.assertEqual(
            self.client.put(url, {"id": -1, "room_id": self.rooms[1].id}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect room identifier
        self.assertEqual(
            self.client.put(url, {"id": self.doors[0].id, "room_id": -1}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Assignation to door with two connections
        self.assertEqual(
            self.client.put(
                url,
                {
                    "id": self.doors[0].id,
                    "room_id": self.rooms[2].id,
                },
            ).status_code,
            status.HTTP_406_NOT_ACCEPTABLE,
        )

        # Assignation to door with the same room
        self.assertEqual(
            self.client.put(
                url,
                {
                    "id": self.doors[0].id,
                    "room_id": self.rooms[0].id,
                },
                format="json",
            ).status_code,
            status.HTTP_406_NOT_ACCEPTABLE,
        )

        # # Correct door connection
        door1 = Door(name="Door A")
        door2 = Door(name="Door B")
        door1.save()
        door2.save()

        DoorConnectsRoom(door=door1, room=self.rooms[0]).save()

        self.assertEqual(
            self.client.put(
                url, {"id": door1.id, "room_id": self.rooms[2].id}
            ).status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.put(
                url, {"id": door2.id, "room_id": self.rooms[2].id}
            ).status_code,
            status.HTTP_200_OK,
        )

    def test04_delete(self):
        """Test Case 04: Doors DELETE Request"""
        url = "/v1/doors"

        # Incorrect number of parameters
        self.assertEqual(
            self.client.delete(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            self.client.delete(url, {"room_id": self.rooms[0].id}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect door identifier
        self.assertEqual(
            self.client.delete(
                url, {"id": -1, "room_id": self.rooms[0].id}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect room identifier
        self.assertEqual(
            self.client.delete(
                url, {"id": self.doors[0].id, "room_id": -1}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect door-room connection
        self.assertEqual(
            self.client.delete(
                url, {"id": self.doors[0].id, "room_id": self.rooms[2].id}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Deletion of door with 2 connections
        self.assertEqual(
            self.client.delete(
                url, {"id": self.doors[0].id, "room_id": self.rooms[0].id}
            ).status_code,
            status.HTTP_200_OK,
        )

        # Deletion of door with only one connection
        door1 = Door(name="Puerta")
        door1.save()
        DoorConnectsRoom(door=door1, room=self.rooms[0]).save()

        self.assertEqual(
            self.client.delete(
                url, {"id": door1.id, "room_id": self.rooms[0].id}
            ).status_code,
            status.HTTP_200_OK,
        )

    def test05_patch(self):
        """Test Case 04: Doors DELETE Request"""
        url = "/v1/doors"

        # Missing parameters
        self.assertEqual(
            self.client.patch(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )

        # Invalid id
        self.assertEqual(
            self.client.patch(
                url, {"id": -1, "action": True}, format="json"
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Invalid action
        self.assertEqual(
            self.client.patch(
                url, {"id": self.doors[1].id, "action": "mass-destruction"}
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Valid patch
        self.assertEqual(
            self.client.patch(
                url, {"id": self.doors[1].id, "action": True}, format="json"
            ).status_code,
            status.HTTP_200_OK,
        )
