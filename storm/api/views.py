"""
This module defines the views returned by all urls in the application
"""

# regular imports
from datetime import datetime
from io import BytesIO
import json
import pandas as pd

# django imports
from django.utils import timezone
from django.http import Http404, HttpResponse
from django.db import models
from django.db.models import Count

# restframework imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request

# API imports
from api.serializers import RoomDashboardSerializer, RoomDetailSerializer
from api.serializers import WindowSerializer, DoorSerializer
from api.serializers import VentilatorSerializer, LightSerializer
from api.models import Room, Door, Ventilator, Light, Window
from api.models import DoorConnectsRoom
from api.models import PeopleInRoom
from api.models import DoorOpen, VentilatorOn, LightOn, WindowOpen


class DevicesAPIView(APIView):
    """
    Defines views for all end-points associated to `individual` devices,
    which are only owned by one room.
    """

    allowed_devices = ["GET", "POST", "DELETE", "PUT", "PATCH"]

    def get(self, *_):
        """
        Retrieves all `individual` devices not owned by empty room.
        A non-associated device is the product of a non-empty room deletion.

        Used on room CREATION and EDITION.
        """

        # Dictionary with classes and serializers for all devices
        dmodels = {
            "windows": (Window, WindowSerializer),
            "ventilators": (Ventilator, VentilatorSerializer),
            "lights": (Light, LightSerializer),
        }
        data = {}

        # Serialize non-associated devices
        for key, (model, serializer) in dmodels.items():
            devs = model.objects.filter(room=None)
            data[key] = serializer(devs, many=True).data

        return Response(data)

    def post(self, request: Request):
        """
        Creates a new device of a given type. Used on EDITION.

        This method expects to receive the parameters specified in
        `jsons/devices/post.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """
        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        # Obtain request parameters
        name = request.data.get("name", None)
        room_id = request.data.get("room_id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if name is None or room_id is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {", ".join(dtypes.keys())}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        # Create and save device
        dev = dtypes[dtype](name=name, room=room)
        dev.save()

        return Response(f"Device {name} for room {room.name} succesfully created!")

    def put(self, request: Request):
        """
        Assigns a device to a room. Used on CREATION and EDITION.

        This method expects to receive the parameters specified in
        `jsons/devices/put.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """

        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        # Obtain request parameters
        identifier = request.data.get("id", None)
        room_id = request.data.get("room_id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if identifier is None or room_id is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {", ".join(dtypes.keys())}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        dev = dtypes[dtype].objects.filter(id=identifier).first()

        # Error case: Invalid device
        if dev is None:
            return Response("Invalid device id!", status=status.HTTP_400_BAD_REQUEST)
        if dev.room is not None:
            return Response(
                "Device already belongs to a room!", status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save device
        dev.room = room
        dev.save()

        return Response(f"Device {dev.name} assigned to room {room.name}!")

    def delete(self, request: Request):
        """
        Deletes a new device of a given type. Used on EDITION.

        This method expects to receive the parameters specified in
        `jsons/devices/delete.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """
        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        # Obtain request parameters
        identifier = request.data.get("id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if identifier is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {dtypes}", status=status.HTTP_400_BAD_REQUEST
            )

        # Remove device from the database
        dev = dtypes[dtype].objects.filter(id=identifier).first()

        # Error case: Invalid device
        if dev is None:
            return Response("Invalid device id!", status=status.HTTP_400_BAD_REQUEST)

        dev.delete()

        return Response("Device succesfully removed!")

    def patch(self, request: Request):
        """
        Updates a device status. Used on CONTROL PANEL.

        This method expects to receive the parameters specified in
        `jsons/devices/patch.json`, where "type" can be either "window",
        "ventilator" or "light".

        Args:
            request (dict): A JSON-like dictionary
        """
        # Dictionary with classes for all devices
        dtypes: dict[str, models.Model] = {
            "window": Window,
            "ventilator": Ventilator,
            "light": Light,
        }

        dstatus: dict[str, models.Model] = {
            "window": WindowOpen,
            "ventilator": VentilatorOn,
            "light": LightOn,
        }

        dactions: dict[str, str] = {
            "window": "is_open",
            "ventilator": "is_on",
            "light": "is_on",
        }

        # Obtain request parameters
        identifier = request.data.get("id", None)
        dtype = request.data.get("type", None)
        action = request.data.get("action", None)

        # Error Case: Missing Parameters
        if identifier is None or action is None or dtype is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(
                f"type field must be {", ".join(dtypes.keys())}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        dev = dtypes[dtype].objects.filter(id=identifier).first()

        # Error case: Invalid device
        if dev is None:
            return Response("Invalid device id!", status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(action, bool):
            return Response("Invalid action!", status=status.HTTP_400_BAD_REQUEST)

        # Create new dev status
        ds = dstatus[dtype](time=timezone.now())
        setattr(ds, dtype, dev)
        setattr(ds, dactions[dtype], action)
        ds.save()
        return Response(f"Device {dev.name} assigned the status {action}!")


class DoorsAPIView(APIView):
    """
    Defines views for all end-points associated to doors, which chan be owned
    by up to two rooms.
    """

    allowed_methods = ["GET", "PUT", "POST", "DELETE", "PATCH"]

    def get(self, *_):
        """
        Retrieves all doors with less than two rooms. Used on CREATION and
        EDITION. This method expects to receive the parameters specified in
        `jsons/doors/get.json`.
        """
        ids = (
            DoorConnectsRoom.objects.values("door")
            .annotate(rc=Count("room"))
            .filter(rc__lt=2)
            .values("door")
        )
        doors = Door.objects.filter(id__in=ids)

        serializer = DoorSerializer(doors, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        """
        Creates a new door. Used on EDITION. This method expects to receive the
        parameters specified in `jsons/doors/post.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        # Obtain request parameters
        name = request.data.get("name", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if name is None or room_id is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door(name=name)
        door.save()
        droom = DoorConnectsRoom(door=door, room=room)
        droom.save()

        return Response(f"Door {door.name} created successfully!")

    def put(self, request: Request):
        """
        Connects a door to a room new door. Used on EDITION and CREATION.
        This method expects to receive the parameters specified in
        `jsons/doors/put.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        # Obtain request parameters
        identifier = request.data.get("id", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if identifier is None or room_id is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=identifier).first()

        # Error Case: Invalid door
        if door is None:
            return Response("Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        connected_rooms = DoorConnectsRoom.objects.filter(door=door).values_list(
            "room", flat=True
        )

        # Error Case: Invalid connections
        if room_id in connected_rooms:
            return Response(
                f"Given room id {room_id} is already connected to this door!"
            )
        if connected_rooms.count() >= 2:
            return Response(f"Given door id {identifier} is connected to two rooms!")

        droom = DoorConnectsRoom(door=door, room=room)
        droom.save()

        return Response(f"Door {door.name} updated successfully!")

    def delete(self, request: Request):
        """
        Deletes a door. Used on EDITION. This method expects to receive the
        parameters specified in `jsons/doors/put.json`.

        Args:
            request (dict): A JSON-like dictionary
        """
        # Obtain request parameters
        identifier = request.data.get("id", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if identifier is None or room_id is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response("Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=identifier).first()

        # Error Case: Invalid door
        if door is None:
            return Response("Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        connected_rooms = DoorConnectsRoom.objects.filter(door=door).values()
        droom = DoorConnectsRoom.objects.filter(door=door, room=room)

        # Error Case: Not connected door
        if droom is None:
            return Response(
                "Given door is not connected to the room!",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete Door on last connection
        if connected_rooms.count() == 1:
            door.delete()
        else:
            droom.delete()
        return Response(f"Door {door.name} updated successfully!")

    def patch(self, request: Request):
        """
        Updates a door status. Used on CONTROL PANEL.

        This method expects to receive the parameters specified in
        `jsons/doors/patch.json`.

        Args:
            request (dict): A JSON-like dictionary
        """
        # Obtain request parameters
        identifier = request.data.get("id", None)
        action = request.data.get("action", None)

        # Error Case: Missing Parameters
        if identifier is None or action is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(action, bool):
            return Response("Invalid action!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=identifier).first()

        # Error Case: Invalid door
        if door is None:
            return Response("Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        door_open = DoorOpen(door=door, time=timezone.now(), is_open=action)
        door_open.save()

        return Response(f"Door {door.name} assigned the status {action}!")


class RoomsAPIView(APIView):
    """
    Defines views for all end-points associated to generic room information
    that is shown on the dashboard.
    """

    allowed_methods = ["GET", "POST", "DELETE"]

    def get_object(self, pk):
        """
        Retrieves a room with the given pk.

        Args:
            pk (int): Room identifier.

        Raises:
            Http404: Room does not exist.

        Returns:
            Room: Record in the database.
        """
        try:
            return Room.objects.get(pk=pk)
        except Exception as exc:
            raise Http404(f"Room with id {pk} does not exist!") from exc

    def get(self, *_):
        """
        Retrieves a list of all existent rooms for the main dashboard.
        """
        rooms = Room.objects.all()
        serializer = RoomDashboardSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        """
        Creates a new room from the given request. Used on CREATION.

        This method expects to receive the parameters specified in
        `jsons/rooms/post.json`. Devices sent via this endpoint can be either
        of the following:

        "devices": ["type": [{"name": str}, {"id": int}, ...], ...]

        An entry with the "name" field signifies the creation of a new
        device, and an entry with the "id" field signifies the association of
        an existent device with the room. For "type", it can be "windows",
        "ventilators", "lights" or "doors".

        Args:
            request (dict): A JSON-like dictionary.

        """

        # Dictionary with methods for all devices
        device_manager = {
            "windows": self._add_windows,
            "doors": self._add_doors,
            "ventilators": self._add_ventilators,
            "lights": self._add_lights,
        }

        # Obtain request parameters
        name = request.data.get("name", None)
        size = request.data.get("size", None)
        devices = request.data.get("devices", None)

        # Error Case: Missing Parameters
        if name is None or size is None:
            return Response("Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Create the room before appending devices
        room = Room(name=name, size=size)
        room.save()

        devices = json.loads(devices)

        # Append devices to room
        for key in devices:
            device_manager[key](devices[key], room)

        return Response(f"Room {room.name} created successfully with id {room.id}!")

    def delete(self, request: Request):
        """
        Removes a room from the database. This method expects to receive
        the parameters specified in `jsons/rooms/delete.json`.

        Args:
            request (dict): A JSON-like dictionary.

        """
        room = self.get_object(request.data.get("id", None))
        room.delete()
        return Response(
            f"Room with id {request.data.get("id", None)} successfully deleted!",
            status=status.HTTP_204_NO_CONTENT,
        )

    def _add_doors(self, doors: list[dict], room):
        """
        Handler method to add a set of doors to the database.

        Args:
            doors (list[dict]): List of doors associated to room.
            room: Room which contains doors.
        """
        # Process each door in request
        for d in doors:
            identifier = d.get("id", None)
            name = d.get("name", None)
            # If no id is received, create new door and connection
            if identifier is None:
                if name is not None:
                    d_ = Door(name=name)
                    d_.save()
                    d__ = DoorConnectsRoom(door=d_, room=room)
                    d__.save()

            # If an id is received, create a connection when possible
            else:
                d_ = Door.objects.filter(id=identifier).first()
                if (
                    d_ is not None
                    and DoorConnectsRoom.objects.filter(door=d_).count() < 2
                ):
                    d__ = DoorConnectsRoom(door=d_, room=room)
                    d__.save()

    def _add_windows(self, windows: list[dict], room):
        """
        Handler method to add a set of windows to the database.

        Args:
            windows (list[dict]): List of windows associated to room.
            room: Room which contains windows.
        """
        # Process each window in request
        for w in windows:
            identifier = w.get("id", None)
            name = w.get("name", None)

            # If no id is received, create new window for the room
            if identifier is None:
                if name is not None:
                    w_ = Window(name=name, room=room)
                    w_.save()
            # If an id is received, update ownership for an empty window
            else:
                w_ = Window.objects.filter(id=identifier).first()

                if w_ is not None:
                    w_.room = room if w_.room is None else w_.room
                    w_.save()

    def _add_ventilators(self, ventilators: list[dict], room):
        """
        Handler method to add a set of ventilators to the database.

        Args:
            ventilators (list[dict]): List of ventilators associated to room.
            room: Room which contains ventilators.
        """
        # Process each ventilator in request
        for v in ventilators:
            identifier = v.get("id", None)
            name = v.get("name", None)

            # If no id is received, create new window for the room
            if identifier is None:
                if name is not None:
                    v_ = Ventilator(name=name, room=room)
                    v_.save()
            # If an id is received,
            # update ownership for an empty ventilator when possible
            else:
                v_ = Ventilator.objects.filter(id=identifier).first()

                if v_ is not None:
                    v_.room = room if v_.room is None else v_.room
                    v_.save()

    def _add_lights(self, lights: list[dict], room):
        """
        Handler method to add a set of lights to the database.

        Args:
            lights (list[dict]): List of lights associated to room.
            room: Room which contains lights.
        """
        # Process each light in request
        for light in lights:
            identifier = light.get("id", None)
            name = light.get("name", None)

            # If no id is received, create new window for the room
            if identifier is None:
                if name is not None:
                    l_ = Light(name=light["name"], room=room)
                    l_.save()
            # If an id is received,
            # update ownership for an empty ventilator when possible
            else:
                l_ = Light.objects.filter(id=identifier).first()
                if l_ is not None:
                    l_.room = room if l_.room is None else l_.room
                    l_.save()


class RoomDetailAPIView(APIView):
    """
    Defines views for all end-points associated to real-time room information
    that is shown on the room details page.
    """

    allowed_methods = ["GET", "PUT"]

    def get_object(self, pk):
        """
        Retrieves a room with the given pk.

        Args:
            pk (int): Room identifier.

        Raises:
            Http404: Room does not exist.

        Returns:
            Room: Record in the database.
        """
        try:
            return Room.objects.get(pk=pk)
        except Exception as exc:
            raise Http404(f"Room with id {pk} does not exist!") from exc

    def get(self, _, identifier):
        """
        Retrieve detailed room information.

        Args:
            identifier (int): Room identifier.
        """
        post = self.get_object(identifier)
        serializer = RoomDetailSerializer(post)
        return Response(serializer.data)

    def put(self, request, identifier):
        """
        Updates room information. Used on EDITION. This method expects to
        receive the parameters specified in `jsons/rooms/put.json`.

        Args:
            request (dict): A JSON-like dictionary.
        """
        post = self.get_object(identifier)
        serializer = RoomDetailSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
