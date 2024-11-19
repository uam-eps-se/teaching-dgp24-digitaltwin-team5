"""
This module defines unit tests for the application.
"""

import decimal
import json

from rest_framework import status

from api.tests.base import Base, ROOMS
from api.models import Room, Ventilator, Light, Window, Door
from api.models import DoorConnectsRoom, Alert


class RoomsTest(Base):
    """
    This class defines a series of unit tests to be performed on various REST
    API endpoints.
    """

    def test01_rooms_get(self):
        """Test Case 01: Rooms GET request"""
        url = "/v1/rooms"
        response = self.client.get(url)

        response_ = []
        for room in self.rooms:
            response_.append(
                {
                    "id": room.id,
                    "name": room.name,
                    "size": room.size,
                    "temperature_status": Alert.AlertType.INFO,
                    "co2_status": Alert.AlertType.INFO,
                    "devices": {
                        "doors": {"total": 2, "open": 0},
                        "windows": {"total": ROOMS, "open": 0},
                        "ventilators": {"total": ROOMS, "on": 0},
                        "lights": {"total": ROOMS, "on": 0},
                    },
                    "metrics": {
                        "people": 3,
                        "co2": 500,
                        "temperature": decimal.Decimal("22.10"),
                    },
                }
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, response_)

    def test02_rooms_post_fail(self):
        """Test Case 02: Rooms failed POST request"""
        url = "/v1/rooms"

        # Missing parameters (BAD REQUEST)
        self.assertEqual(
            self.client.post(url, {}).status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.client.post(url, {"name": "Room IV"}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            self.client.post(url, {"size": 104}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Incorrect field type
        with self.assertRaises(ValueError):
            self.client.post(url, {"name": 101, "size": 101})
            self.client.post(url, {"name": "Room IV", "size": "pepe"})

    def test03_rooms_post_empty(self):
        """Test Case 03: Rooms POST request with no devices"""
        url = "/v1/rooms"

        self.assertEqual(
            self.client.post(url, {"name": "Room IV", "size": 104}).status_code,
            status.HTTP_200_OK,
        )

    def test04_rooms_post_devices_fail(self):
        """Test Case 04: Rooms POST request with incorrect device info"""
        url = "/v1/rooms"
        data = {"name": "Room IV", "size": 104}
        data["devices"] = "test"

        # Incorrect 'devices' datatype
        with self.assertRaises(json.decoder.JSONDecodeError):
            self.client.post(url, data)

        # Incorrect key in 'devices' dict
        data["devices"] = json.dumps({"pepe": 1})
        self.assertEqual(
            self.client.post(url, data, format="json").status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test05_rooms_post_add_doors(self):
        """Test Case 05: Rooms POST request with doors"""
        url = "/v1/rooms"
        data = {"name": "Room IV", "size": 104}

        # Incorrect datatype in 'doors' dict
        with self.assertRaises(AttributeError):
            data["devices"] = json.dumps({"doors": ["uh-oh", "this-wrong"]})
            self.client.post(url, data, format="json")
            data["devices"] = json.dumps({"doors": "uh-oh"})
            self.client.post(url, data, format="json")

        # Incorrect field type
        with self.assertRaises(ValueError):
            data["devices"] = json.dumps({"doors": [{"id": "patata"}]})
            self.client.post(url, data, format="json")

        # Correct creation, Incorrect connection
        data["devices"] = json.dumps(
            {"doors": [{"name": "Door 4"}, {"id": self.doors[0].id}]}
        )
        conns = DoorConnectsRoom.objects.filter(door=self.doors[0]).count()

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            DoorConnectsRoom.objects.filter(door=self.doors[0]).count(), conns
        )

        # Correct connection
        door = Door(name="API TestDoor")
        door.save()
        data["devices"] = json.dumps({"doors": [{"id": door.id}]})
        conns = DoorConnectsRoom.objects.filter(door=door).count()

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertEqual(DoorConnectsRoom.objects.filter(door=door).count(), conns + 1)

    def test06_rooms_post_add_windows(self):
        """Test Case 06: Rooms POST request with windows"""
        url = "/v1/rooms"
        data = {"name": "Room IV", "size": 104}

        # Incorrect datatype in 'windows' dict
        with self.assertRaises(AttributeError):
            data["devices"] = json.dumps({"windows": ["uh-oh", "this-wrong"]})
            self.client.post(url, data, format="json")
            data["devices"] = json.dumps({"windows": "uh-oh"})
            self.client.post(url, data, format="json")

        # Incorrect field type
        with self.assertRaises(ValueError):
            data["devices"] = json.dumps({"windows": [{"id": "patata"}]})
            self.client.post(url, data, format="json")

        # Window Creation
        data["devices"] = json.dumps({"windows": [{"name": "Window 27"}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )

        # Incorrect Window connection
        data["devices"] = json.dumps({"windows": [{"id": self.windows[0].id}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertNotEqual(
            data["name"], Window.objects.filter(id=self.windows[0].id).first().room.name
        )

        # Correct Window connection
        window = Window(name="API TestWindow")
        window.save()
        data["devices"] = json.dumps({"windows": [{"id": window.id}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data["name"], Window.objects.filter(id=window.id).first().room.name
        )

    def test07_rooms_post_add_ventilators(self):
        """Test Case 07: Rooms POST request with ventilators"""
        url = "/v1/rooms"
        data = {"name": "Room IV", "size": 104}

        # Incorrect datatype in 'ventilators' dict
        with self.assertRaises(AttributeError):
            data["devices"] = json.dumps({"ventilators": ["uh-oh", "this-wrong"]})
            self.client.post(url, data, format="json")
            data["devices"] = json.dumps({"ventilators": "uh-oh"})
            self.client.post(url, data, format="json")

        # Incorrect field type
        with self.assertRaises(ValueError):
            data["devices"] = json.dumps({"ventilators": [{"id": "patata"}]})
            self.client.post(url, data, format="json")

        # Ventilator Creation
        data["devices"] = json.dumps({"ventilators": [{"name": "Ventilator 27"}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )

        # Incorrect Ventilator connection
        data["devices"] = json.dumps({"ventilators": [{"id": self.ventilators[0].id}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertNotEqual(
            data["name"],
            Ventilator.objects.filter(id=self.ventilators[0].id).first().room.name,
        )

        # Correct Ventilator connection
        ventilator = Ventilator(name="API TestVentilator")
        ventilator.save()
        data["devices"] = json.dumps({"ventilators": [{"id": ventilator.id}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data["name"], Ventilator.objects.filter(id=ventilator.id).first().room.name
        )

    def test08_rooms_post_add_lights(self):
        """Test Case 08: Rooms POST request with lights"""
        url = "/v1/rooms"
        data = {"name": "Room IV", "size": 104}

        # Incorrect datatype in 'lights' dict
        with self.assertRaises(AttributeError):
            data["devices"] = json.dumps({"lights": ["uh-oh", "this-wrong"]})
            self.client.post(url, data, format="json")
            data["devices"] = json.dumps({"lights": "uh-oh"})
            self.client.post(url, data, format="json")

        # Incorrect field type
        with self.assertRaises(ValueError):
            data["devices"] = json.dumps({"lights": [{"id": "patata"}]})
            self.client.post(url, data, format="json")

        # Light Creation
        data["devices"] = json.dumps({"lights": [{"name": "Light 27"}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )

        # Incorrect Light connection
        data["devices"] = json.dumps({"lights": [{"id": self.lights[0].id}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertNotEqual(
            data["name"], Light.objects.filter(id=self.lights[0].id).first().room.name
        )

        # Correct Light connection
        light = Light(name="API TestLight")
        light.save()
        data["devices"] = json.dumps({"lights": [{"id": light.id}]})

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data["name"], Light.objects.filter(id=light.id).first().room.name
        )

    def test09_rooms_delete(self):
        """Test Case 09: Rooms DELETE request"""
        url = "/v1/rooms"
        room = Room(name="API TestRoom")
        room.save()

        # No id supplied
        self.assertEqual(
            self.client.delete(url, {}).status_code, status.HTTP_404_NOT_FOUND
        )

        # Wrong parameter supplied in request
        self.assertEqual(
            self.client.delete(url, {"pepe": "pepe"}).status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # Wrong parameter type supplied in request
        self.assertEqual(
            self.client.delete(url, {"id": "pepe"}).status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # Correct deletion
        self.assertEqual(
            self.client.delete(url, {"id": room.id}).status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertIsNone(
            Room.objects.filter(id=room.id).first(),
        )
