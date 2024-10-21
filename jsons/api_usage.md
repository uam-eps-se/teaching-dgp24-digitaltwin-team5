# STORM API

Se asume el uso de esta API en cinco escenarios principales: Visualización (Dashboard), Creación de Habitaciones, Edición de Habitaciones, Importado de Datos y Exportado de Datos. Los verbos destinados para cada escenario, así como su uso de caso esperado, son especificados más adelante.

## Creación
Este escenario asume la creación de una habitación por parte del usuario, y por tanto le corresponden las siguientes llamadas:

- **GET**: Permite obtener información de dispositivos (`v1/devices`) y puertas (`v1/doors`) sin dueño. 
- **POST**: Permite crear el cuarto nuevo con sus correspondientes dispositivos/puertas, así como la posibilidad de asignar aquellos sin dueño (`v1/rooms`). Se espera este comportamiento en una sola llamada.

## Edición
Este escenario asume que un usuario accederá a los detalles de una habitación por medio del dashboard, sobre la que editará **(i)** sus datos o **(ii)** sus dispositivos y puertas. Por tanto, le corresponden las siguientes llamadas:

- **GET**: Permite obtener la información de un cuarto y sus dispositivos/puertas/métricas (`v1/room/id`), así como dispositivos (`v1/devices`) y puertas (`v1/doors`) sin dueño.    
- **POST**: Permite crear dispositivos (`v1/devices`) o puertas (`v1/doors`) nuevas dentro de una habitación.
- **PUT**: Permite actualizar dispositivos (`v1/devices`) sin dueño o puertas (`v1/doors`) con menos de dos conexiones para asignarlos al cuarto.
- **DELETE**
    1. Permite borrar el cuarto (`v1/rooms`) sin afectar aquellos dispositivos que aún contenga (pasarán a ser "libres").
    2. Permite borrar un dispositivo (`v1/devices`) asignado a este cuarto. Este comportamiento no es esperado para aquellos obtenidos por GET que no hayan sido asignados.
    3. Permite borrar una conexión con una puerta (`v1/doors`) asignada al cuarto. En caso de ser conexión única, la puerta se borra


## Call List
### Rooms
- **GET**: Obtiene todos los cuartos. Dashboard.
- **POST**: Crea un cuarto nuevo y sus dispositivos. Asigna aquellos dispositivos "sin dueño" elegidos al cuarto. Creacion.
- **DELETE**: Borra un cuarto. Edición.

### Room
- **GET**: Obtiene un cuarto. Dashboard.
- **PUT**: Actualiza info del cuarto. Edición.

### Devices
- **GET**: Obtiene dispositivos sin dueño. Creación y Edición.
    En edición, "quitarlos" de la lista no debería borrarlos de la DB
- **POST**: Crea un dispositivo nuevo. Edición.
- **PUT**: Asigna un dispositivo sin dueño. Edición.
    Por si se había olvidado de agregarlo en creación, también se puede en edición.
- **DELETE**: Borra un dispositivo. Edición.

### Doors
- **GET**: Obtiene puertas con menos de dos conexiones. Creación y Edición.
    En edición, "quitarlos" de la lista no debería borrarlos de la DB
- **POST**: Crea una puerta nueva. Edición.
- **PUT**: Asigna una puerta con menos de dos conexiones. Edición.
    Por si se había olvidado de agregarlo en creación, también se puede en edición.
- **DELETE**: Borra una conexión de puerta. Edición.