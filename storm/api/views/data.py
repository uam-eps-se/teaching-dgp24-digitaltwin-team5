"""
This module defines the `v1/data` endpoint for the API.
"""

# regular imports
from datetime import datetime
from io import BytesIO
import pandas as pd

# django imports
from django.http import HttpResponse
from django.db import models

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request

# API imports
from api.models import Room, Door, Ventilator, Light, Window
from api.models import DoorConnectsRoom
from api.models import PeopleInRoom
from api.models import DoorOpen, VentilatorOn, WindowOpen

import api.views.utils as sse


class DataAPIView(APIView):
    """
    Defines views for all end-points associated to database import and export
    operations done by the user.
    """

    def get(self, *_):
        """
        Exports the database as an Excel file with existent rooms, door and
        devices. Metrics and events are not exported.
        """
        mods: list[models.Model] = [
            Room,
            Window,
            Ventilator,
            Light,
            Door,
            DoorConnectsRoom,
        ]
        b = BytesIO()
        writer = pd.ExcelWriter(b)
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "attachment;filename=database.xlsx"

        for model in mods:
            df = pd.DataFrame(list(model.objects.all().values()))
            df.to_excel(writer, sheet_name=model.__name__)

        writer.close()
        response.write(b.getvalue())

        return response

    def post(self, request: Request):
        """
        Imports database entries from a given xlsx file. Expects to receive
        rooms, devices, doors, events and people metrics.

        Args:
            request (Request): _description_

        Returns:
            _type_: _description_
        """
        file = request.data.get("database", None)
        xls = pd.ExcelFile(file)
        room_ids = self.import_rooms(xls)
        self.import_windows(xls, room_ids)
        self.import_ventilators(xls, room_ids)
        self.import_doors(xls, room_ids)
        self.import_people(xls, room_ids)

        sse.send(sse.CHANNEL_SUMMARY)
        sse.send(sse.CHANNEL_CONTEXT)
        return Response("Import database finished!", status=status.HTTP_202_ACCEPTED)

    def import_rooms(self, xls: pd.ExcelFile):
        """
        Import rooms from an excel worksheet in the database. All 'id' fields are
        discarded, as this worksheet will be appended to an existent database.

        This method expects the worksheet to be called 'Room', which should contain
        two fields 'name' and 'size (m2)'.

        Args:
            xls (pd.ExcelFile): Excel File.
        Returns:
            A dictionary with the previous room ids.
        """
        room_ids = {}

        # Read worksheet
        df = pd.read_excel(xls, "Room")
        df.columns = df.columns.str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            room = Room(name=row["name"], size=row["size (m2)"])
            room.save()

            # Map ids for future dependencies
            room_ids[room.name.lower()] = room

        return room_ids

    def import_ventilators(self, xls: pd.ExcelFile, room_ids: dict):
        """
        Import ventilators from an excel worksheet in the database. All 'id' fields are
        repurposed as names, as this worksheet will be appended to an existent database.

        This method expects to use the worksheets 'Ventilator' and 'VentilatorOn', which
        should contain the following fields:

        - Ventilator: ID, Room_Id
        - VentilatorOn: Timestamp, Ventilator_Id, isOn


        Args:
            xls (pd.ExcelFile): Excel File.
            room_ids (dict): Previous room ids in the file.
        """
        vent_ids = {}

        # Read ventilator worksheet
        df = pd.read_excel(xls, "Ventilator")
        df.columns = df.columns.str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            vent = Ventilator(
                name=f"Ventilator {row['ID']}", room=room_ids[row["Room_Id"].lower()]
            )
            vent.save()

            # Map ids for ventilator-on dependencies
            vent_ids[row["ID"]] = vent

        # Read ventilator-on worksheet
        df = pd.read_excel(xls, "VentilatorOn")
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            vent_on = VentilatorOn(
                ventilator=vent_ids[row["VentilatorId"]],
                is_on=row["isOn"],
                time=datetime.strptime(row["Timestamp"], "%Y-%m-%dT%H:%M:%S%z"),
            )
            vent_on.save()

    def import_windows(self, xls: pd.ExcelFile, room_ids: dict):
        """
        Import windows from an excel worksheet in the database. All 'id' fields are
        repurposed as names, as this worksheet will be appended to an existent database.

        This method expects to use the worksheets 'Window' and 'WindowOpen', which
        should contain the following fields:

        - Window: ID, Room_Id
        - WindowOpen: Timestamp, Window_ID, isOpen

        Args:
            xls (pd.ExcelFile): Excel File.
            room_ids (dict): Previous room ids in the file.
        """
        win_ids = {}

        # Read window worksheet
        df = pd.read_excel(xls, "Window")
        df.columns = df.columns.str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            win = Window(
                name=f"Window {row['ID']}", room=room_ids[row["Room_Id"].lower()]
            )
            win.save()

            # Map ids for window-open dependencies
            win_ids[row["ID"]] = win

        # Read window-open worksheet
        df = pd.read_excel(xls, "WindowOpen")
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            win_open = WindowOpen(
                window=win_ids[row["Window_ID"]],
                is_open=row["isOpen"],
                time=datetime.strptime(row["Timestamp"], "%Y-%m-%dT%H:%M:%S%z"),
            )
            win_open.save()

    def import_doors(self, xls: pd.ExcelFile, room_ids: dict):
        """
        Import doors from an excel worksheet in the database. All 'id' fields are
        repurposed as names, as this worksheet will be appended to an existent database.

        This method expects to use the worksheets 'Door', 'DoorOpen' and
        'Door_Connects_Room', which should contain the following fields:

        - Door: ID, Room_Id.
        - DoorOpen: Timestamp, Window_ID, isOpen.
        - Door_Connects_Room: Door_ID, Room_ID.

        Args:
            xls (pd.ExcelFile): Excel File.
            room_ids (dict): Previous room ids in the file.
        """
        door_ids = {}

        # Read door worksheet
        df = pd.read_excel(xls, "Door")
        df.columns = df.columns.str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            door = Door(name=f"Door {row['ID']}")
            door.save()

            # Map ids for door-open dependencies
            door_ids[row["ID"]] = door

        # Read door-open worksheet
        df = pd.read_excel(xls, "DoorOpen")
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            door_open = DoorOpen(
                door=door_ids[row["Door_Id"]],
                is_open=row["isOpen"],
                time=datetime.strptime(row["Timestamp"], "%Y-%m-%dT%H:%M:%S%z"),
            )
            door_open.save()

        # Read door-connections worksheet
        df = pd.read_excel(xls, "Door_Connects_Room")
        df.columns = df.columns.str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            door_connection = DoorConnectsRoom(
                door=door_ids[row["Door_ID"]], room=room_ids[row["Room_ID"].lower()]
            )
            door_connection.save()

    def import_people(self, xls: pd.ExcelFile, room_ids: dict):
        """
        Import people metrics from an excel worksheet in the database. All 'id'
        fields are repurposed as names, as this worksheet will be appended to
        an existent database.

        This method expects to use the 'PeopleInRoom', which contains the
        fields "Timestamp", "Room_Id" and "NOPeopleInRoom".

        Args:
            xls (pd.ExcelFile): Excel File.
            room_ids (dict): Previous room ids in the file.
        """
        # Read people worksheet
        df = pd.read_excel(xls, "PeopleInRoom")
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].str.strip()

        # Add rows to the database
        for _, row in df.iterrows():
            np = PeopleInRoom(
                time=datetime.strptime(row["Timestamp"], "%Y-%m-%dT%H:%M:%S%z"),
                room=room_ids[row["Room_Id"].lower()],
                no_people_in_room=row["NOPeopleInRoom"],
            )
            np.save()
