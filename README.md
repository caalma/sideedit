# SideEdit

Utilidad para edición lateral/remota (y en tiempo real) de documentos javascript en aplicaciones web.

Pensado para funcionar, en modo local, con [Hydra](https://hydra.ojack.xyz/), pero es flexible para usarlo en otros projectos.


## Requerimientos

+ Python >= 3.9
+ Flask
+ Flask-SocketIO


## Modo de uso

### 0. Instalar requerimientos

+ Si no está disponible en el sistema operativo, instalar: python y python-venv
+ Instalar dependencias con: `./0_instalar.sh `

### 1. Activar el server

+ Activar servidor en local: `./1_activar.sh`

### 2. Vincular con Hydra (o el projecto en uso).

Por ejemplo en Hydra:

+ Cargar el script de control con: `await loadScript("http://127.0.0.1:5555/sideedit.js")`
+ Setear el codigo a editar con: `setWatchFile('script_editable.js')`

### 3. Editar y guardar para ejecutar
+ Con el editor de texto preferido modificar el documento y guardar.
+ Automaticamente se actualiza y ejecuta el nuevo código en el projecto en uso.


## Importante !

Solamente testeado bajo GNU/Linux.
