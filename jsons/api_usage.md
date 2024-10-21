# STORM API


## Rooms
- GET: Obtiene todos los cuartos. Dashboard.
- POST: Crea un cuarto nuevo y sus dispositivos. Creacion.
    Asigna aquellos dispositivos "sin dueño" elegidos al cuarto.
- DELETE: Borra un cuarto. Edición.

## Room
- GET: Obtiene un cuarto. Dashboard
- PUT: Actualiza info del cuarto. Edición.

## Devices
- GET: Obtiene dispositivos sin dueño. Creación y Edición.
    En edición, "quitarlos" de la lista no debería borrarlos de la DB
- POST: Crea un dispositivo nuevo. Edición.
- PUT: Asigna un dispositivo sin dueño. Edición.
    Por si se había olvidado de agregarlo en creación, también se puede en edición.
- DELETE: Borra un dispositivo. Edición.

## Doors
- GET: Obtiene puertas con menos de dos conexiones. Creación y Edición.
    En edición, "quitarlos" de la lista no debería borrarlos de la DB
- POST: Crea una puerta nueva. Edición.
- PUT: Asigna una puerta con menos de dos conexiones. Edición.
    Por si se había olvidado de agregarlo en creación, también se puede en edición.
- DELETE: Borra una conexión de puerta. Edición.