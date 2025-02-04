import os
from datetime import datetime, timedelta
import configparser

class Config:
    '''Class which stores all settable variables as strings in .ini file using ConfigParser library. Use 'set_value' and 'get_x', where x can be 'bool', 'int', 'float' or 'value'.'''
    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        self.load()

    def create_default_config_file(self):
        self.config_parser['DEFAULT'] = {}
        self.config_parser['FLAG'] = {
            'downloaded_from_scryfall': 'false',
            'database_was_created': 'false',
            'collections_was_created': 'false',
            'decks_was_created': 'false'
        }
        self.config_parser['FOLDER'] = {
            'collections': 'collections',
            'database': 'database',
            'decks': 'decks',
            'downloads': 'downloads',
            'images': 'images',
            'cards': 'images/cards',
            'symbols': 'images/symbols',
            'sets': 'images/sets'
        }
        self.config_parser['FILE'] = {
            'database': f"./{self.config_parser['FOLDER']['database']}/database.db",
            'collections': f"./{self.config_parser['FOLDER']['database']}/collections.db",
            'decks': f"./{self.config_parser['FOLDER']['database']}/decks.db"
        }
        self.config_parser['TIME'] = {
            'format_full': '%H:%M:%S %d/%m/%Y'.replace('%','%%')
        }
        self.config_parser['BULK'] = {
            'url': 'https://api.scryfall.com/bulk-data',
            'data_type': 'Default Cards',
            'time_period': str((60*60*24*7)),
            'last_updated': str((datetime.now() - timedelta(8)).strftime(self.config_parser['TIME']['format_full']))
        }
        self.config_parser['APP'] = {
            'name': 'Python Magic Collection',
            'style': 'Fusion',
            'font': 'MS Shell Dlg 2',
            'font_size': str(13),
            'collection': 'Collection',
            'decks': 'Decks',
            'add_cards': 'Add cards',
            'wishlist': "Wishlist",
            'import_export': 'Import/export',
            'settings': 'Settings'
        }
        self.config_parser['COLLECTION'] = {
            'image_type': 'normal',
            'grid_number_of_cards': '18',
            'grid_number_of_rows': '3',
            'current_page': '1',
            'current_collection': 'maincollection'
        }
        self.save()
        self.load()

    def save(self):
        with open(f'config.ini', 'w') as f: self.config_parser.write(f)

    def load(self):
        self.config_parser.read(f'config.ini')

    def get_boolean(self, section: str, option:str) -> bool:
        self.load()
        return self.config_parser.getboolean(section.upper(), option.lower())

    def get_int(self, section: str, option: str) -> int:
        self.load()
        return self.config_parser.getint(section.upper(), option.lower())
        
    def get_float(self, section: str, option: str) -> float:
        self.load()
        return self.config_parser.getfloat(section.upper(), option.lower())

    def get_value(self, section: str, option: str) -> str:
        self.load()
        return self.config_parser[section.upper()][option.lower().lower()]

    def set_value(self, section: str, option: str, value: str) -> None:
        self.config_parser[section.upper()][option.lower()] = value
        self.save()

    def build_folder_structure(self) -> None:
        for folder in self.config_parser['FOLDER']:
            if not os.path.exists(f"./{self.config_parser['FOLDER'][folder]}"):
                os.mkdir(f"./{self.config_parser['FOLDER'][folder]}")
    
    def build_file_structure(self) -> None:
         for file in self.config_parser['FILE']:
            if file != 'config':
                if not os.path.exists(self.config_parser['FILE'][file]):
                    with open(self.config_parser['FILE'][file], 'w'): pass
                    self.set_value('FLAG', f'{file}_was_created', 'true')
                else:
                    self.set_value('FLAG', f'{file}_was_created', 'false')