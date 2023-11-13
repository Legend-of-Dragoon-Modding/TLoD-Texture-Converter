"""

Convert Advanced:
This module is for initially handly the loaded file,
and depending on the type result, will redirect to other modules.

"""

import os
from tkinter import messagebox
import pxl_decoder

TIM_MAGIC = b'\x10\x00\x00\x00'
MCQ_MAGIC_1 = b'\x4D\x43\x51\x01'
MCQ_MAGIC_2 = b'\x4D\x43\x51\x02'
PXL_MAGIC = b'\x11\x00\x00\x00'


class ConvertTextureFile:
    def __init__(self, file_to_decode=str):
        self.self = ConvertTextureFile
        self.file_to_decode = file_to_decode
        self.check_file_type(file_to_decode=file_to_decode)
    
    def check_file_type(self, file_to_decode=str):
        get_texture_type = ''
        file_decoded = []
        with open(file_to_decode, 'rb') as texture_file:
            read_all_file = texture_file.read()
            read_header = read_all_file[0:4]

            if (read_header == TIM_MAGIC):
                get_texture_type = 'TIM'
            elif (read_header == MCQ_MAGIC_1) or (read_header == MCQ_MAGIC_2):
                get_texture_type = 'MCQ'
            elif (read_header == PXL_MAGIC):
                get_texture_type = 'PXL'
            else:
                error_message_01 = f'{file_to_decode} is not a TLoD Texture File Type, can\'t continue the Conversion'
                messagebox.showerror(title='CRITICAL!!!', message=error_message_01)
        
        if get_texture_type == 'TIM':
            file_decoded = ['Nothing']
        elif get_texture_type == 'MCQ':
            file_decoded = ['Nothing']
        elif get_texture_type == 'PXL':
            converted_pxl_file = pxl_decoder.PxlFileDecoder.decode_pxl_data(pxl_decoder.PxlFileDecoder, file_path=file_to_decode)
            file_decoded = converted_pxl_file
        
        return file_decoded, get_texture_type
        
