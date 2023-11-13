"""

Database to Listbox(Dict):
This Algorithm will create a dict from the database,
to be sure that the content loaded to the Sub List
and the Object List is the correct

Copyright (C) 2023 DooMMetaL

"""

import os

ARCHIVE_FOLDER = f'[FOLDER]'
ARCHIVE_FILE = f'[Single-File]'

class DatabaseDict:
    """Database to Listbox(Dict):
    This Algorithm will create a dict from the database,
    to be sure that the content loaded to the Sub List
    and the Object List is the correct"""
    def __init__(self, database_path) -> dict:
        self.self = DatabaseDict
        self.database_path = database_path
        self.process_database(database_path_str=self.database_path)
    
    def process_database(self, database_path_str=str) -> dict:
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
        database_dict = {'Battle_Stages': {}, 'Bosses': {}, 'Characters': {}, 'CutScenes': {}, 'Enemies': {}, 'Menu_Misc': {}, 'Skyboxes': {}, 'THE_END': {}, 'Tutorial': {}, 'World_Map_Field': {}, 'World_Map_Thumbnails': {}}
        for db_file in database_files:
            if f'Battle_Stages' in db_file:
                reading_text_bs = self.process_text_file(text_file=db_file)
                reading_db_bs = self.process_database_from_text(text_file=reading_text_bs)
                for load_to_dict_bs in reading_db_bs:
                    database_dict['Battle_Stages'][f'{load_to_dict_bs[0]}'] = load_to_dict_bs[1]
            elif f'Bosses' in db_file:
                reading_text_bosses = self.process_text_file(text_file=db_file)
                reading_db_bosses = self.process_database_from_text(text_file=reading_text_bosses)
                for load_to_dict_bosses in reading_db_bosses:
                    database_dict['Bosses'][f'{load_to_dict_bosses[0]}'] = load_to_dict_bosses[1]
            elif f'Characters' in db_file:
                reading_text_characters = self.process_text_file(text_file=db_file)
                reading_db_characters = self.process_database_from_text(text_file=reading_text_characters)
                for load_to_dict_char in reading_db_characters:
                    database_dict['Characters'][f'{load_to_dict_char[0]}'] = load_to_dict_char[1]
            elif f'CutScenes' in db_file:
                reading_text_cutscenes = self.process_text_file(text_file=db_file)
                reading_db_cutscenes = self.process_database_from_text_cu(text_file=reading_text_cutscenes)
                for load_to_dict_cutscenes in reading_db_cutscenes:
                    database_dict['CutScenes'][f'{load_to_dict_cutscenes[0]}'] = [load_to_dict_cutscenes[1]]
            elif f'Enemies' in db_file:
                reading_text_enemies = self.process_text_file(text_file=db_file)
                reading_db_enemies = self.process_database_from_text(text_file=reading_text_enemies)
                for load_to_dict_enemies in reading_db_enemies:
                    database_dict['Enemies'][f'{load_to_dict_enemies[0]}'] = load_to_dict_enemies[1]
            elif f'Menu_Misc' in db_file:
                reading_text_menu = self.process_text_file(text_file=db_file)
                reading_db_menu = self.process_database_from_text(text_file=reading_text_menu)
                for load_to_dict_logo in reading_db_menu:
                    database_dict['Menu_Misc'][f'{load_to_dict_logo[0]}'] = load_to_dict_logo[1]
            elif f'Skyboxes' in db_file:
                reading_text_skyboxes = self.process_text_file(text_file=db_file)
                reading_db_skyboxes = self.process_database_from_text(text_file=reading_text_skyboxes)
                for load_to_dict_skyboxes in reading_db_skyboxes:
                    database_dict['Skyboxes'][f'{load_to_dict_skyboxes[0]}'] = load_to_dict_skyboxes[1]
            elif f'THE_END' in db_file:
                reading_text_theend = self.process_text_file(text_file=db_file)
                reading_db_theend = self.process_database_from_text(text_file=reading_text_theend)
                for load_to_dict_theend in reading_db_theend:
                    database_dict['THE_END'][f'{load_to_dict_theend[0]}'] = load_to_dict_theend[1]
            elif f'Tutorial' in db_file:
                reading_text_tutorial = self.process_text_file(text_file=db_file)
                reading_db_tutorial = self.process_database_from_text(text_file=reading_text_tutorial)
                for load_to_dict_tutorial in reading_db_tutorial:
                    database_dict['Tutorial'][f'{load_to_dict_tutorial[0]}'] = load_to_dict_tutorial[1]
            elif f'World_Map_Field' in db_file:
                reading_text_worldmap_f = self.process_text_file(text_file=db_file)
                reading_db_worldmap_f = self.process_database_from_text(text_file=reading_text_worldmap_f)
                for load_to_dict_worldmap_f in reading_db_worldmap_f:
                    database_dict['World_Map_Field'][f'{load_to_dict_worldmap_f[0]}'] = load_to_dict_worldmap_f[1]
            elif f'World_Map_Thumbnails' in db_file:
                reading_text_worldmap_t = self.process_text_file(text_file=db_file)
                reading_db_worldmap_t = self.process_database_from_text(text_file=reading_text_worldmap_t)
                for load_to_dict_worldmap_t in reading_db_worldmap_t:
                    database_dict['World_Map_Thumbnails'][f'{load_to_dict_worldmap_t[0]}'] = load_to_dict_worldmap_t[1]
        return database_dict

    def process_text_file(text_file=str) -> str:
        text_read = None
        with open(text_file, 'r') as text_to_read:
            text_read = text_to_read.readlines()
        return text_read

    def process_database_from_text(text_file=str) -> list:
        name_objects = []
        for text in text_file:
            cleaning_text = text.strip()
            find_colon = cleaning_text.find(f':')
            location_object = cleaning_text[:find_colon].strip()
            name_object = cleaning_text[(find_colon + 2):].strip()
            object_complete = name_object, location_object
            name_objects.append(object_complete)
        return name_objects

    def process_database_from_text_cu(text_file=str) -> list:
        name_scene = []
        name_objects = []
        index_insert = []
        index_place = 0
        for text in text_file:
            if f'[/' in text:
                name_scene_original = text.strip()
                find_start = name_scene_original.find(f'[')
                find_end = name_scene_original.find(f']')
                name_scene_for_listbox = name_scene_original[find_start + 2: find_end]
                name_scene.append(name_scene_for_listbox)
                index_insert.append(index_place)
                name_objects.append(f'index_placeholder')
            else:
                cleaning_text = text.strip()
                find_colon = cleaning_text.find(f':')
                name_object_cu = cleaning_text[:find_colon].strip()
                texture_loc = cleaning_text[(find_colon + 2):]
                objects_complete = name_object_cu, texture_loc
                name_objects.append(objects_complete)
            index_place += 1
        
        combined_index = []
        for index_combine in range(0, len(index_insert)):
            if index_combine == 0:
                pass
            else:
                start_index = index_insert[index_combine - 1]
                end_index = index_insert[index_combine]
                comb_ind = start_index, end_index
                combined_index.append(comb_ind)
        
        final_cutscene_list = []
        slice_name_scene = 0
        for get_segments in combined_index:
            start_segment = get_segments[0]
            end_segment = get_segments[1]
            segment = name_objects[start_segment + 1 :end_segment]
            name_scene_current = name_scene[slice_name_scene]
            final_current_scene = name_scene_current, segment
            final_cutscene_list.append(final_current_scene)
            slice_name_scene += 1

        return final_cutscene_list