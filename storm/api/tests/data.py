"""
This module defines unit tests for the `v1/data` endpoint.
"""

# regular imports
from io import BytesIO
import pandas as pd

# restframework imports
from rest_framework import status

# API imports
from api.tests.base import Base, ROOMS, DEVS_PER_ROOM


class DataTest(Base):
    """
    Class representation of unit tests to run.
    """

    def test01_get(self):
        """Test Case 01: Data GET request"""
        url = "/v1/data"
        expected = [
            ("Room", ROOMS),
            ("Ventilator", ROOMS * DEVS_PER_ROOM),
            ("Door", ROOMS),
            ("Window", ROOMS * DEVS_PER_ROOM),
            ("DoorConnectsRoom", ROOMS * 2),
            ("Light", ROOMS * DEVS_PER_ROOM),
        ]
        response = self.client.get(url)
        xls = pd.ExcelFile(BytesIO(response.content))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response["Content-Type"], "application/vnd.ms-excel")

        self.assertCountEqual(
            [sheet_name for sheet_name, _ in expected], xls.sheet_names
        )

        for sheet_name, rows in expected:
            df = pd.read_excel(xls, sheet_name)
            self.assertEqual(len(df), rows)

    def test02_post(self):
        """Test Case 02: Data POST request"""
        url = "/v1/data"

        with open("api/tests/exampledata.xlsx", "rb") as database:
            response = self.client.post(url, data={"database": database})

            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
