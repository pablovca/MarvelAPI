import requests
import time
import hashlib
import sys
from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.engine import URL


public_key = ""
private_key = ""

class Collection(Enum):
    characters = 1
    events = 2

characters_table_name = 'public.characters'
events_table_name = 'public.events'
characters_events_table_name = 'public.characters_events'

total_characters = 0
total_events = 0


def main():
    password = sys.argv[1]
    global public_key
    public_key = sys.argv[2]
    global private_key
    private_key = sys.argv[3]
    engine = connect_to_database(password)
    metadata = MetaData(schema='public')
    metadata.reflect(engine, schema='public')

    with engine.connect() as connection:
        create_tables(metadata, engine, connection)

#This function get all the data fron the Marvel API, then creates the tables and inserts the data
def create_tables(metadata, engine, connection):
    characters_data = get_all_json_data(Collection.characters)
    characters_table = create_table(metadata, engine, connection, 'characters', define_characters_table)
    clear_table(metadata, connection, characters_table_name)
    insert(characters_data, characters_table, connection, get_character_values)

    events_data = get_all_json_data(Collection.events)
    events_table = create_table(metadata, engine, connection, 'events', define_events_table)
    clear_table(metadata, connection, events_table_name)
    insert(events_data, events_table, connection, get_event_values)

    characters_events_table = create_table(metadata, engine, connection, 'characters_events', define_characters_events_table)
    clear_table(metadata, connection, characters_events_table_name)
    
    ids_array = []
    for result in characters_data:
        character_id = result['id']
        items = result['events']['items']

        for item in items: 
            uri = item['resourceURI']
            splitted_uri = uri.split('/')
            event_id = splitted_uri[len(splitted_uri)- 1]
            ids_array.append({'character_id': character_id, 'event_id': event_id})
 
    insert(ids_array, characters_events_table, connection, get_characters_events_values)

#Definition of the characters table
def define_characters_table(metadata):
    return Table('characters', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(200)),
        Column('description', String)
    )

#Definition of the events table
def define_events_table(metadata):
    return Table('events', metadata,
        Column('id', Integer, primary_key=True),
        Column('title', String(200)),
        Column('description', String),
        Column('next', String),
        Column('previous', String)
    )

#Definition of the characters_events table
def define_characters_events_table(metadata):
    return Table('characters_events', metadata,
        Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
        Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    )

#Function that creates a new table if it does not exists
def create_table(metadata, engine, connection, table_name, define_function):
    if not engine.dialect.has_table(connection, table_name):
        new_table = define_function(metadata)
        metadata.create_all(engine)
        return new_table
    return metadata.tables['public.' + table_name]


#Helper functions that allows the abstraction of the insertion of values from diferent tables
#to avoid code repetition while with diferent inser functions for every table
def get_character_values(character, characters_table):
    return characters_table.insert().values(id=character["id"], name=character["name"], description=character["description"])


def get_event_values(event, events_table):
    return events_table.insert().values(id=event['id'], title=event['title'], description=event['description'], next=['next'], previous=['previous'])


def get_characters_events_values(characters_events, characters_events_table):
    print(characters_events['character_id'], characters_events['event_id'])
    return characters_events_table.insert().values(character_id=characters_events['character_id'], event_id=characters_events['event_id'])


#This function insert the array of data in the specified table
def insert(data_array, table, connection, values_function):
    for data in data_array:
        insert_statement = values_function(data, table)
        connection.execute(insert_statement)
    connection.commit()


#This function clear the specified table 
def clear_table(metadata, connection, table_name):
    table = metadata.tables[table_name]
    delete_statement = table.delete()
    connection.execute(delete_statement)
    connection.commit()


def get_data(collection, offset=0):
    json_response = get_json_data(collection, offset)
    return json_response["data"]["results"]
    

#This function gets the data from the specified endpoint and returns a json response
def get_json_data(collection, offset=0):
    time_stamp = str(time.time())
    long_string = (time_stamp + private_key + public_key)
    result = hashlib.md5(long_string.encode())
    api_url = "https://gateway.marvel.com" + "/v1/public/" + collection.name + "?ts=" + time_stamp + \
    "&apikey=" + public_key + "&hash=" + result.hexdigest() + "&limit=100" + "&offset=" + str(offset)

    response = requests.get(api_url)
    json_response = response.json()
    match collection:
        case Collection.characters:
            global total_characters
            total_characters = json_response['data']['total']
        case Collection.events:
            global total_events
            total_events = json_response['data']['total']
    return json_response


#This function gets all the data fron the end point, because the Marvel API only allows to get
# 100 objects at a time, we need to increase the offset and append the new data
# in cases like the Characters endpoint (1562 objects) 
def get_all_json_data(collection):
    data_collection = get_data(collection)
    counter = 100
    limit = 0
    match collection:
        case Collection.characters:
            limit = total_characters
        case Collection.events:
            limit = total_events
    while counter < limit: 
        data_collection.extend(get_data(collection, offset=counter))
        counter += 100

    return data_collection


#Function to create the connection to the postgresql database
def connect_to_database(password):
    url = URL.create(
        drivername="postgresql",
        username="postgres",
        password=password,
        host="localhost",
        database="postgres"
    )
    engine = create_engine(url, future=True)
    return engine


if __name__ == "__main__":
    main()