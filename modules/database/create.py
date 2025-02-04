import sqlite3
import json
import re
from typing import Any
from modules.config import Config
from modules.logging import console_log
from modules.globals import DATABASE_INSERT_TO_MAIN
from modules.database.database_functions import get_database_table_name

def assign_data_type(element: Any) -> str:
    data_type = ''

    if isinstance(element, list): data_type = 'list'
    elif isinstance(element, bool): data_type = 'bool'
    elif isinstance(element, float): data_type = 'float'
    elif isinstance(element, str): data_type = 'string'
    elif isinstance(element, int): data_type = 'int'
    elif isinstance(element, object): data_type = 'object'

    #Exception for null in value
    if element is None: data_type = 'string'

    #Exception for datetime values
    if isinstance(element, str):
        r = re.compile('\d\d\d\d-\d\d-\d\d')
        if r.match(element) is not None:
            data_type = 'datetime'

    return data_type

def get_column_names_and_types() -> dict:
    config = Config()

    with open(f"./{config.get_value('FOLDER', 'downloads')}/{config.get_value('BULK', 'data_type')}.json", 'r', encoding='utf8') as f:
        j = json.load(f)
        names_and_types = {}
        for card in j:
            try:
                for key in card.keys():
                    if key not in names_and_types:
                        names_and_types[key] = assign_data_type(card[key])
                        if key == 'set':
                            names_and_types['"set"'] = names_and_types.pop('set')
            except KeyError:
                pass
        return names_and_types

def create_database_main_table(connection: sqlite3.Connection) -> None:
    console_log('info', f"Creating {get_database_table_name()} in database")
    main_column_names_and_types = get_column_names_and_types()

    query = f'CREATE TABLE IF NOT EXISTS {get_database_table_name()} (\nid TEXT NOT NULL PRIMARY KEY,'

    for element in main_column_names_and_types:
        if element == 'id': continue

        match main_column_names_and_types[element]:
            case 'string' | 'list' | 'object': query += f'\n{element} TEXT,'
            case 'float': query += f'\n{element} FLOAT,'
            case 'bool': query += f'\n{element} BOOL,'
            case 'int': query += f'\n{element} INT,'
            case 'datetime': query += f'\n{element} DATETIME,'

        DATABASE_INSERT_TO_MAIN.append(element)

    query += '\nsort_key TEXT)'

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()