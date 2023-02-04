# Prueba de Desarrollo

Para esta prueba se escogió como tema el API de Marvel. Este API cuenta con los siguiente endpoints principales:
- Characters
- Comics
- Cretors
- Events
- Series
- Stories

Debido a la complejidad y el volumen de datos se escogieron los end points *Characters* y *Events*, donde *Characters* son todos los personajes de Marvel (1562) y *Events* (74) son historias a larga escala que tienen ramificaciones para los personajes o universos compartidos, en otras palabras un personaje puede participar en muchos eventos y en un evento pueden participar muchos personajes.

El programa se conecta a los endpoints y extrae información relevante para crear las tablas en la base de datos local de la siguiente manera:

Characters

- **id (Primary Key)**: identificador único del personaje
- name: nombre del personaje
- description: descripción del personaje

Además de Characters se utilizó la información de cada evento asociado, para obtener su número de identificación para crear la tabla de relación *characters_events*


Events
- **id (Primary Key)**: identificador único del evento 
- title: título del evento
- description: descripcion del evento
- next: siguiente evento
- previous: evento anterior

Characters_Events
- **character_id (Primary Key y Foreign Key)**: identifcador único del personaje de la tabla Characters
- **event_id (Primary Key y Foreign Key)**: identificador único del evento de la tabla Events

Esta tabla refleja la relacion que existe entre personajes y eventos, de manera que podemos consultar en cuales eventos aparece un personaje y cuales personajes aparecen en un evento.

### Bibliotecas de Python utilizadas:
- Requests: para acceder a los endpoints
- SQLAlchemy: para conectarse a la base de datos, crear tablas, insertar y borrar, se utilizadon las clases facilitadoras como Table, Column, Integer, String, MetaData, ForeignKey, en lugar de sentencias planas de SQL.


### Software utilizado:
- Python 3.10
- PostgreSQL 14.6
- Ubuntu 22.04


## Como ejecutarlo

1. Crear un ambiente con el comando: 

    `python3 -m venv .env`

2. Activar el ambiente con el comando: 
    
    `source .env/bin/activate`

3. Instalar las dependencias con el comando: 
    
    `pip install -r requirements.txt`

4. Ejecutar el programa con el comando:

    `python3 main.py <contraseña del usuario postgres> <public_key> <private_key>`

> Por facilidad el programa siempre utiliza el usuario *postgres*, localhost y el puerto 5432 para realizar la conexión a la base de datos.