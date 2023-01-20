# Manual del servicio Main de IceFlix.
A continuación se exponen brevemente los pasos a seguir para ejecutar el Main.

## Instalación
El primer paso es crear un entorno virtual y activarlo sobre un directorio en el que clonaremos el repositorio con el programa. Primero debemos instalar lo necesario:

```bash
sudo apt install python3-virtualenv
```

Ahora ya podemos ubicamos en el directorio donde queramos crearlo y ejecutamos lo siguiente para crearlo:

```bash
virtualenv <nombre_deseado>
```
Y para activarlo:
```bash
source <nombre_de_mi_entorno>/bin/activate
```

Tras crear el entorno virtual, podemos clonar el repositorio sobre el directorio creado.

El segundo paso es comprender las opciones que nos ofrece el Makefile:
* ***install:*** instala las dependencias necesarias para la ejecución del programa.
* ***icestorm:*** se debe ejecutar esta opción para que se creen los topics necesarios para los servicios
* ***main:*** lanza la ejecución del servicio Main
* ***clean:*** destruye los topics que se creacron con icestorm

## Ejecución
Para ejecutar el main, debemos ubicarnos en el directorio raiz del repositorio, abrir un terminal y escribir:
```bash
make install
make icestorm
```

En otro terminal ejecutaremos:
```bash
make main
```