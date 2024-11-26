"""
This module defines unit tests for the `v1/context` endpoint.
"""

from rest_framework import status

from api.tests.base import Base, ROOMS
from api.models import Alert


class ContextTest(Base):
    """
    Class representation of unit tests to run.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.alerts = [
            Alert(
                type=i, content="test", received=False, room=cls.rooms[i], time=cls.time
            )
            for i in range(ROOMS)
        ]
        Alert.objects.bulk_create(cls.alerts)

    def test01_get(self):
        """Test Case 01: Context GET request"""
        url = "/v1/context"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data["rooms"],
            [{"id": room.id, "name": room.name} for room in self.rooms],
        )

        self.assertEqual(
            response.data["alerts"],
            [
                {
                    "content": alert.content,
                    "id": alert.id,
                    "roomId": alert.room.id,
                    "roomName": alert.room.name,
                    "time": self.time.timestamp(),
                    "type": alert.type,
                }
                for alert in self.alerts
            ],
        )

    def test02_put(self):
        """Test Case 01: Context PUT request"""
        url = "/v1/context"

        # Incorrect parameter label
        self.assertEqual(
            self.client.put(url, {"id": [1, 3, 4, 5]}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Correct recv
        self.assertEqual(
            self.client.put(
                url, {"ids": [alert.id for alert in self.alerts]}, format="json"
            ).status_code,
            status.HTTP_200_OK,
        )

        alerts = list(
            Alert.objects.filter(
                id__in=[alert.id for alert in self.alerts]
            ).values_list("received")
        )

        self.assertTrue(alerts)
