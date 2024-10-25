from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request
from api.serializers import *
from api.models import *
from django.db.models import Count


class DevicesAPIView(APIView):
    allowed_devices = ['GET', 'POST', 'DELETE', 'PUT']

    def get(self, request, format=None):
        """
        Retrieves all devices (not doors) which are not associated to any  room.
        A non-associated device is the product of a non-empty room deletion.

        Used on both room CREATION and EDITION.

        """

        # Dictionary with classes and serializers for all devices
        dmodels = {
            "windows": [Window, WindowSerializer],
            "ventilators": [Ventilator, VentilatorSerializer],
            "lights": [Light, LightSerializer]
        }
        data = {}

        for key in dmodels:
            # Search for unasigned devices
            devs = dmodels[key][0].objects.filter(room=None)

            # Serialize devices
            data[key] = dmodels[key][1](devs, many=True).data

        return Response(data)

    def post(self, request: Request):
        """
        Creates a new device of a given type. This method endpoint should only
        be called from room EDITION, and not during room CREATION.

        This method  expects  to  receive  the  required  "name"  and  "room_id"
        parameters to create a new device, and an additional field "type", which
        must be one of the following:

        - "window"
        - "ventilator"
        - "light"

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
            return Response(f"Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(f"type field must be {", ".join(dtypes.keys())}", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response(f"Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        # Create and save device
        dev = dtypes[dtype](name=name, room=room)
        dev.save()

        return Response(f"Device {name} for room {room.name} succesfully created!")

    def put(self, request: Request):
        """
        Assigns a room to a device. Used on both room CREATION and EDITION.

        This method  expects  to  receive  the  required  "id"  and  "room_id"
        parameters to modify a device, and an additional field "type", which
        must be one of the following:

        - "window"
        - "ventilator"
        - "light"

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
        id = request.data.get("id", None)
        room_id = request.data.get("room_id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if id is None or room_id is None or dtype is None:
            return Response(f"Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(f"type field must be {", ".join(dtypes.keys())}", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response(f"Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        dev = dtypes[dtype].objects.filter(id=id).first()

        # Error case: Invalid device
        if dev is None:
            return Response(f"Invalid device id!", status=status.HTTP_400_BAD_REQUEST)
        if dev.room is not None:
            return Response(f"Device already belongs to a room!", status=status.HTTP_400_BAD_REQUEST)

        # Create and save device
        dev.room = room
        dev.save()

        return Response(f"Device {dev.name} assigned to room {room.name}!")

    def delete(self, request: Request):
        """
        Deletes a new device of a given type. This method endpoint  should  only
        be called from room edition, and not during room creation.

        This method expects to receive the device's id through  an  "id"  field,
        and an additional field "type", which must be one of the following:

        - "window"
        - "ventilator"
        - "light"

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
        id = request.data.get("id", None)
        dtype = request.data.get("type", None)

        # Error Case: Missing Parameters
        if id is None or dtype is None:
            return Response(f"Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Error Case: Wrong device kind
        if dtype not in dtypes:
            return Response(f"type field must be {dtypes}", status=status.HTTP_400_BAD_REQUEST)

        # Remove device from the database
        dev = dtypes[dtype].objects.filter(id=id).first()

        # Error case: Invalid device
        if dev is None:
            return Response(f"Invalid device id!", status=status.HTTP_400_BAD_REQUEST)

        dev.delete()

        return Response(f"Device succesfully removed!")


class DoorsAPIView(APIView):
    allowed_methods = ['GET', 'PUT', 'POST', 'DELETE']

    def get(self, request, format=None):
        """
        Retrieves all doors with less than two rooms.
        """
        ids = (
            DoorConnectsRoom.objects
            .values('door')
            .annotate(rc=Count('room'))
            .filter(rc__lt=2)
            .values('door')
        )
        doors = Door.objects.filter(id__in=ids)

        serializer = DoorSerializer(doors, many=True)
        return Response(serializer.data)

        # return Response(serializer.data)

    def post(self, request: Request):
        """
        Creates a new door. This method endpoint should only be called from room
        edition, and not during room creation.

        This method  expects  to  receive  the  required  "name"  and  "room_id"
        parameters to create a new door.

        Args:
            request (dict): A JSON-like dictionary.
        """
        # Obtain request parameters
        name = request.data.get("name", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if name is None or room_id is None:
            return Response(f"Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response(f"Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door(name=name)
        door.save()
        droom = DoorConnectsRoom(door=door, room=room)
        droom.save()

        return Response(f"Door {door.name} created successfully!")

    def put(self, request: Request):
        # Obtain request parameters
        id = request.data.get("id", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if id is None or room_id is None:
            return Response(f"Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response(f"Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=id).first()

        # Error Case: Invalid door
        if door is None:
            return Response(f"Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        connected_rooms = DoorConnectsRoom.objects.filter(
            door=door).values_list('room', flat=True)

        # Error Case: Invalid connections
        if room_id in connected_rooms:
            return Response(f"Given room id {room_id} is already connected to this door!")
        elif connected_rooms.count() >= 2:
            return Response(f"Given door id {id} is connected to two rooms!")
        else:
            droom = DoorConnectsRoom(door=door, room=room)
            droom.save()
        return Response(f"Door {door.name} updated successfully!")

    def delete(self, request: Request):
        """
        Deletes a new device of a given type. This method endpoint  should  only
        be called from room edition, and not during room creation.

        This method expects to receive the device's id through  an  "id"  field,
        and an additional field "type", which must be one of the following:

        - "window"
        - "ventilator"
        - "light"

        Args:
            request (dict): A JSON-like dictionary
        """
        # Obtain request parameters
        id = request.data.get("id", None)
        room_id = request.data.get("room_id", None)

        # Error Case: Missing Parameters
        if id is None or room_id is None:
            return Response(f"Missing field!", status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(id=room_id).first()

        # Error Case: Room does not exist
        if room is None:
            return Response(f"Invalid room id!", status=status.HTTP_400_BAD_REQUEST)

        door = Door.objects.filter(id=id).first()

        # Error Case: Invalid door
        if door is None:
            return Response(f"Invalid door id!", status=status.HTTP_400_BAD_REQUEST)

        connected_rooms = DoorConnectsRoom. objects.filter(door=door).values()
        droom = DoorConnectsRoom.objects.filter(door=door, room=room)

        # Error Case: Not connected door
        if droom is None:
            return Response(f"Given door is not connected to the room!", status=status.HTTP_400_BAD_REQUEST)

        # Delete Door on last connection
        if connected_rooms.count() == 1:
            door.delete()
        else:
            droom.delete()
        return Response(f"Door {door.name} updated successfully!")


class RoomsAPIView(APIView):
    allowed_methods = ['GET', 'POST', 'DELETE']

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise Http404

    def get(self, request: Request):
        """
        Retrieves a list of all existent rooms for the main dashboard.
        """
        rooms = Room.objects.all()
        serializer = RoomDashboardSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        """
        Creates a new room from the given request.

        This method expects to receive the required "name" and "size" values
        for creating a new room, and all initial devices from the "devices"
        key in the dictionary.

        Devices sent via this endpoint should follow the following format:

        "devices": [
            "type": [
                {"name": str},  # new device
                {"id": int}     # existent device
            ]
        ]

        Where an entry with the "name" field signifies the creation of a new
        device, and an entry with the "id" field signifies the association of
        an existent device with the room.

        Args:
            request (dict): A JSON-like dictionary.

        """

        # Dictionary with methods for all devices
        device_manager = {
            "windows": self._add_windows,
            "doors": self._add_doors,
            "ventilators": self._add_ventilators,
            "lights": self._add_lights
        }

        # Obtain request parameters
        name = request.data.get("name", None)
        size = request.data.get("size", None)
        devices = request.data.get("devices", None)

        # Error Case: Missing Parameters
        if name is None or size is None:
            return Response(f"Missing field!", status=status.HTTP_400_BAD_REQUEST)

        # Create the room before appending devices
        room = Room(name=name, size=size)
        room.save()

        # Append devices to room
        for key in devices:
            device_manager[key](devices[key], room)

        return Response(f"Room {room.name} created successfully with id {room.id}!")

    def delete(self, request: Request):
        """
        Removes a room from the database, from a given "id" field in the 
        Args:
            request (dict): A JSON-like dictionary.

        """
        room = self.get_object(request.data.get("id", None))
        room.delete()
        return Response(f"Room with id {id} successfully deleted!", status=status.HTTP_204_NO_CONTENT)

    def _add_doors(self, doors: list[dict], room):
        """
        Handler method to add a set of doors to the database.

        Args:
            doors (list[dict]): List of doors associated to room.
            room: Room which contains doors.
        """
        # Process each door in request
        for d in doors:
            id = d.get("id", None)
            name = d.get("name", None)
            # If no id is received, create new door and connection
            if id is None:
                if name is not None:
                    d_ = Door(name=name)
                    d_.save()
                    d__ = DoorConnectsRoom(door=d_, room=room)
                    d__.save()

            # If an id is received, create a connection when possible
            else:
                d_ = Door.objects.filter(id=id).first()
                if d_ is not None and DoorConnectsRoom.objects.filter(door=d_).count() < 2:
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
            id = w.get("id", None)
            name = w.get("name", None)

            # If no id is received, create new window for the room
            if id is None:
                if name is not None:
                    w_ = Window(name=name, room=room)
                    w_.save()
            # If an id is received, update ownership for an empty window
            else:
                w_ = Window.objects.filter(id=id).first()

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
            id = v.get("id", None)
            name = v.get("name", None)

            # If no id is received, create new window for the room
            if id is None:
                if name is not None:
                    v_ = Ventilator(name=name, room=room)
                    v_.save()
            # If an id is received, update ownership for an empty ventilator when possible
            else:
                v_ = Ventilator.objects.filter(id=id).first()

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
        for l in lights:
            id = l.get("id", None)
            name = l.get("name", None)

            # If no id is received, create new window for the room
            if id is None:
                if name is not None:
                    l_ = Light(name=l["name"], room=room)
                    l_.save()
            # If an id is received, update ownership for an empty ventilator when possible
            else:
                l_ = Light.objects.filter(id=id).first()
                if l_ is not None:
                    l_.room = room if l_.room is None else l_.room
                    l_.save()


class RoomDetailAPIView(APIView):
    allowed_methods = ['GET', 'PUT']

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise Http404

    def get(self, request, id):
        """
        Retrieve detailed room information.

        Args:
            id (int): Room identifier.
        """
        post = self.get_object(id)
        serializer = RoomDetailSerializer(post)
        return Response(serializer.data)

    def put(self, request, id):
        """
        Update base room information

        Args:
            request (dict): A JSON-like dictionary
        """
        post = self.get_object(id)
        serializer = RoomDetailSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DataAPIView(APIView):
    def get(self, request: Request):
        return Response("To-Do")

    def post(self, request: Request):
        return Response("To-Do")
