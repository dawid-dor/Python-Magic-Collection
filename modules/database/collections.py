from sqlite3 import OperationalError
import sqlite3
from modules.logging import console_log
from modules.database.database_functions import query_get_table_columns, format_card_values
import string

def create_collections_main_table(connection: sqlite3.Connection) -> None:
    query = '''CREATE TABLE IF NOT EXISTS collection_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255),
        formatted_name VARCHAR(255))
        '''

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

def create_collection(connection: sqlite3.Connection, name: str) -> None:
    try:
        whitelist = string.ascii_letters + string.digits
        formatted_name = ''
        for char in name.lower():
            if char in whitelist:
                formatted_name += char
        column_names = query_get_table_columns(connection, 'collection_list')[1:]

        console_log('info', f'Creating {formatted_name} as collections subtable')

        placeholders = ', '.join('?' * len(column_names))
        query = f'''
        INSERT INTO collection_list({', '.join(column_names)}) VALUES ({placeholders})
        '''

        cursor = connection.cursor()
        cursor.execute(query, format_card_values([name, formatted_name]))
        connection.commit()
        
        query = f'''
        CREATE TABLE IF NOT EXISTS {formatted_name} (
                card_id VARCHAR(255) NOT NULL PRIMARY KEY,
                regular INT,
                foil INT,
                tags VARCHAR(255)
                )'''
                
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    except OperationalError:
        console_log('error', f'Failed to create "{name}" collection')

def get_all_collections_names_as_array(connection: sqlite3.Connection) -> list:
    query = "SELECT name FROM collection_list"
                
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    record = cursor.fetchall()
    
    collection_names = [element[0] for element in record]
    collection_names.sort()

    return collection_names

def get_card_ids_from_collection(connection: sqlite3.Connection, collection_name: str) -> list:
    query = f"SELECT card_id FROM {collection_name}"

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    record = cursor.fetchall()

    card_ids = [element[0] for element in record]
    card_ids.sort()

    return card_ids

def get_card_from_collection(connection: sqlite3.Connection, collection_name: str, id: str) -> dict:
    query = f"SELECT * FROM {collection_name} WHERE card_id = '{id}'"

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    record = cursor.fetchone()

    if record:
        return {'card_id': record[0], 'regular': record[1], 'foil': record[2], 'tags': record[3], 'sort_key': record[4]}
    else:
        return {'card_id': id, 'regular': 0, 'foil': 0, 'tags': '', 'sort_key': ''}

def add_card_to_collection(connection: sqlite3.Connection, collection_name: str, id: str, regular: int, foil: int, operation: str, sort_key: str) -> None:
    column = 'regular' if regular > 0 else 'foil'
    query = f"SELECT {column} FROM {collection_name} WHERE card_id = '{id}'"

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    record = cursor.fetchone()

    if record:
        record = record[0]
        if operation == 'add':
            new_value = record + regular + foil
        elif operation == 'set':
            new_value = regular + foil

        query = f'''            
            UPDATE {collection_name}
            SET {column} = {new_value}
            WHERE card_id = '{id}'
            '''
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

    else:
        column_names = query_get_table_columns(connection, collection_name)
        placeholders = ', '.join('?' * len(column_names))
        query = f'''
        INSERT INTO {collection_name} ({', '.join(column_names)}) VALUES ({placeholders})
        '''

        cursor = connection.cursor()
        cursor.execute(query, format_card_values([id, regular, foil, '', sort_key]))
        connection.commit()