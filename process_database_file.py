"""

Database Dictionary:
This Object will create a Dictionary Object from the database, using CSV files,
general format is listed below

Copyright (C) 2024 DooMMetaL

"""

import os
import csv

class DatabaseDict:
    """
    Database Dictionary:\n
    This Object will create a Dictionary Object from the database,\n
    using CSV, Format:\n
    dict: {mainFolder, inDiskType [Folder or Single-File], pathToFolder, files/s, fantasyName, formatType, flag [Optional: EMBEDDED/NONE]}
    """
    def __init__(self, database_path) -> None:
        self.self = DatabaseDict
        self.database_path = database_path
        self.database_processed: dict = {}
        self.process_database(database_path_str=self.database_path)
    
    def process_database(self, database_path_str=str):
        get_path = database_path_str

        database_files = []
        if os.path.isdir(get_path):
            total_files = os.walk(get_path)
            for root, dirs, files in total_files:
                for single_file in files:
                    new_path = os.path.join(root, single_file)
                    database_files.append(new_path)
        else:
            error_string = f'{get_path} is not a correct path, exiting...'
            print(error_string)
            exit()
        
        # First declare the full dictionary to avoid adding more code lines
        database_dict = {}
        for db_file in database_files:
            if 'CutScene' not in db_file:
                get_data_as_list: list = []
                this_dict_name = db_file.replace('Texture_Database/', '').replace('.csv', '').strip()

                with open(db_file, 'r') as csv_file:
                    csv_read = csv.reader(csv_file)
                    for csv_data in csv_read:
                        get_data_as_list.append(csv_data)
                    csv_file.close()
                
                this_parent_dict: dict = {}
                for data_list in get_data_as_list:
                    name_for_subdict = data_list[4]
                    this_dict_data = self.from_csv_to_dict(data=data_list)
                    new_subdict = {f'{name_for_subdict}': this_dict_data}
                    this_parent_dict.update(new_subdict)
                
                new_database = {f'{this_dict_name}': this_parent_dict}
                database_dict.update(new_database)
            elif 'CutScenes' in db_file:
                this_subdict_name = db_file.replace('Texture_Database/', '').replace('CutScenes\\', '').replace('.csv', '').strip()
                get_cu_data_as_list: list = []
                with open(db_file, 'r') as cutscene_csv_file:
                    csv_read_cu = csv.reader(cutscene_csv_file)
                    for csv_data_cu in csv_read_cu:
                        get_cu_data_as_list.append(csv_data_cu)
                    cutscene_csv_file.close()
                sub_dict_cu: dict = {}
                for data_list in get_cu_data_as_list:
                    this_object_name = data_list[4]
                    this_dict_cu_data = self.from_csv_to_dict(data=data_list)
                    new_cu_dict = {f'{this_object_name}': this_dict_cu_data}
                    sub_dict_cu.update(new_cu_dict)
                this_subdict_cu = {f'CutScene_{this_subdict_name}': sub_dict_cu}
                database_dict.update(this_subdict_cu)
        self.database_processed = database_dict
    
    def from_csv_to_dict(self, data=list) -> dict:
        formatted_dict: dict = {}
        main_folder = data[0].replace('/', '\\')
        in_disk_type = data[1]
        path_to_file = data[2].replace('/', '\\')
        files = data[3]
        fantasy_name = data[4]
        format_type = data[5]
        flag = data[6]
        
        file_path: list = []
        if in_disk_type != 'FOLDER':
            new_file_path = f'{main_folder}\\{path_to_file}\\{files}'
            file_path.append(new_file_path)
        else:
            file_list = list(files.split(", "))
            for this_file in file_list:
                new_file_path_files = f'{main_folder}\\{path_to_file}\\{this_file}'
                file_path.append(new_file_path_files)

        formatted_dict = {'filePath': file_path, 'inDiskType': in_disk_type, 'fantasyName': fantasy_name, 
                          'formatType': format_type, 'flag': flag}

        return formatted_dict