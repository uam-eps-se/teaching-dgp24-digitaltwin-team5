"""
This module defines unit tests for the `v1/metrics` endpoint.
"""

# restframework imports
from rest_framework import status

# API imports
from api.tests.base import Base


class MetricsTest(Base):
    """
    Class representation of unit tests to run.
    """

    def test01_post(self):
        """Test Case 01: Metrics POST request"""
        url = "/v1/metrics"

        # Default values
        data = {
            self.rooms[0].id: {
                "people": {"value": 5, "time": self.time},
                "co2": {"value": 500, "time": self.time},
                "temperature": {
                    "value": 23,
                    "time": self.time,
                },
            }
        }

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )

        # Trigger warnings
        data[self.rooms[0].id]["co2"] = {"value": 805, "time": self.time}
        data[self.rooms[0].id]["temperature"] = {"value": 43, "time": self.time}

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )

        # Trigger danger
        data[self.rooms[0].id]["co2"] = {"value": 1001, "time": self.time}
        data[self.rooms[0].id]["temperature"] = {"value": 71, "time": self.time}

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )

        # Turn off cooling and lights
        data[self.rooms[0].id]["people"] = {"value": 0, "time": self.time}

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )

        # Turn on lights
        data[self.rooms[0].id]["people"] = {"value": 5, "time": self.time}

        self.assertEqual(
            self.client.post(url, data, format="json").status_code, status.HTTP_200_OK
        )
