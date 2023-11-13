"""

This module contains TIM Decoder:
TIMs is the "Standard" Texture/Image format for PSX,
TIM could be 4bpp + CLUT, 8 bpp + CLUT, 16-bit Direct Color,
24-bit Direct Color.
This type of files can hold up to 64 CLUT (for 4bbp Textures) plus the Image data,
for each CLUT group, there is one Texture.
In TLoD CLUT Size seems to be 2048 Bytes.
For Combat Textures, the file size seems to be "fixed" to 32768 Bytes.
Summary:
4bpp + CLUT, 64 CLUTs (of 2048 Bytes), file size always 32768

In my code i'm assuming that all the TIMs have CLUT
since it's TLoD way, i'm doing THAT way, anyhow for support in other
TIM configurations, have to wait

"""
from tkinter import messagebox
import preview_textures

TIM_MAGIC = b'\x10\x00\x00\x00'
CONVERT_5_TO_8_BIT = [0, 8, 16, 25, 33, 41, 49, 58,
                      66, 74, 82, 90, 99, 107, 115, 123,
                      132, 140, 148, 156, 165, 173, 181, 189,
                      197, 206, 214, 222, 230, 239, 247, 255]

class TimDecoder:
    def __init__(self, file_to_decode=str, ispreview=str, special_flag=int):
        self.self = TimDecoder
        self.file_to_decode = file_to_decode
        is_preview = ispreview
        self.decode_tim_data(file_path=file_to_decode, is_preview=is_preview, special_flag=special_flag)

    def decode_tim_data(self, file_path=str, is_preview=str, special_flag=int) -> list:
        png_file = []
        tim_flag = {'Pixel_Mode': '', 'is_CLUT': ''}
        tim_data = {'CLUT': [], 'Pixel_Data': []}
        with open(file_path, 'rb') as tim_binary_data:
            read_all_tim = None
            if special_flag == 0:
                read_all_tim = tim_binary_data.read()
            elif special_flag == 1:
                tim_binary_data.seek(57116)
                read_all_tim = tim_binary_data.read()
            this_tim_magic = read_all_tim[0:4]
            if this_tim_magic != TIM_MAGIC:
                raise ValueError(f'File: {file_path}, is not a Standard TIM File!')
            
            flag_data = read_all_tim[4:8]
            flag_data_int = int.from_bytes(flag_data, byteorder='little', signed=False)
            flag_data_bin = bin(flag_data_int)
            split_pixeldata_check = int(flag_data_bin[3:], base=2)
            split_clut_check = int(flag_data_bin[2:3])
            
            if split_pixeldata_check == 0:
                tim_flag['Pixel_Mode'] = '4-bit CLUT'
            elif split_pixeldata_check == 1:
                tim_flag['Pixel_Mode'] = '8-bit CLUT'
            elif split_pixeldata_check == 2:
                tim_flag['Pixel_Mode'] = '16-bit Direct'
            elif split_pixeldata_check == 3:
                tim_flag['Pixel_Mode'] = '24-bit Direct'
            elif split_pixeldata_check == 4:
                tim_flag['Pixel_Mode'] = 'Mixed MODE'
            
            if split_clut_check == 1:
                #print(f'Find a {tim_flag["Pixel_Mode"]} TIM File') # ||---> Debug Print
                tim_flag['is_CLUT'] = 'CLUT'
                read_clut_length = read_all_tim[8:12]
                clut_length = int.from_bytes(read_clut_length, byteorder='little', signed=False)
                tim_data_clut = read_all_tim[8:(clut_length + 8)]
                tim_data['CLUT'] = tim_data_clut
                tim_pixel_data = read_all_tim[(clut_length + 8):]
                tim_data['Pixel_Data'] = tim_pixel_data
                len_all_taken= len(tim_pixel_data) + len(tim_data_clut) + 8 # This 8 represent the header + flag
                len_all_file = len(read_all_tim)
                if len_all_taken != len_all_file:
                    raise ValueError(f'Critical!!: Some Calculations in file length went wrong! Expected: {len_all_file}, Obtained: {len_all_taken}')
            else:
                #print(f'Find a {tim_flag["Pixel_Mode"]} TIM File') # ||---> Debug Print
                tim_flag['is_CLUT'] = 'NO-CLUT'
                read_pixel_data_len = read_all_tim[8:12]
                pd_noclut_len_int = int.from_bytes(read_pixel_data_len, byteorder='little', signed=False)
                read_pd_noclut = read_all_tim[8: pd_noclut_len_int]
                tim_data['Pixel_Data'] = read_pd_noclut
        
        rgba_data, size_img = self.split_data(get_flags=tim_flag, get_tim_data=tim_data)
        png_file = self.process_tim(image_data_rgba=rgba_data, size_image=size_img, preview_flag=is_preview)
        return png_file
    
    @classmethod
    def split_data(cls, get_flags=dict, get_tim_data=dict) -> dict:
        rgba_data = {}
        img_size = {}
        get_clut = get_tim_data.get('CLUT')
        get_pixel_mode = get_flags.get('Pixel_Mode')
        get_img_data = get_tim_data.get('Pixel_Data')
        if get_clut != []:
            processed_clut = TimDecoder.split_clut(clut_data=get_clut, type_clut=get_pixel_mode)
            processed_image_data, img_size_got = TimDecoder.combine_image(image_data=get_img_data, clut_data=processed_clut, pixel_mode=get_pixel_mode)
            rgba_data = processed_image_data
            img_size = img_size_got
        else:
            raise ValueError(f'Critical!!: CLUTless TIM Type not supported at the moment')
        
        return rgba_data, img_size
    
    @staticmethod
    def split_clut(clut_data=bytes, type_clut=str) -> dict:
        split_clut = {}
        #clut_header = clut_data[0:12] # can i ignore this?
        clut_data_itself = clut_data[12:]
        
        if type_clut == f'4-bit CLUT':
            total_clut_entries = len(clut_data_itself) // 32
            next_clut = 0
            clut_entry_num = 0
            for dummy_clut_entry in range(total_clut_entries):
                this_clut = clut_data_itself[next_clut:(next_clut + 32)]
                if this_clut != (b'\x00' * 32):
                    split_clut[f'CLUT_{clut_entry_num}'] = this_clut
                    clut_entry_num += 1
                next_clut += 32
        
        elif type_clut == f'8-bit CLUT':
            total_clut_entries = len(clut_data_itself) // 512
            next_clut = 0
            clut_entry_num = 0
            for dummy_clut_entry in range(total_clut_entries):
                this_clut = clut_data_itself[next_clut:(next_clut + 512)]
                if this_clut != (b'\x00' * 512):
                    split_clut[f'CLUT_{clut_entry_num}'] = this_clut
                    clut_entry_num += 1
                next_clut += 512
        else: # Should i elaborate more in the different types for TLoD?
            raise ValueError(f'Critical!!: {type_clut} not supported')

        return split_clut
    
    @staticmethod
    def combine_image(image_data=bytes, clut_data=dict, pixel_mode=str) -> dict:
        rgba_data_combined = {}
        img_header = image_data[0:12]
        width_image = int.from_bytes(img_header[8:10], byteorder='little', signed=False)
        height_image = int.from_bytes(img_header[10:12], byteorder='little', signed=False)
        # Size Factors
        if pixel_mode == f'4-bit CLUT':
            intended_width = width_image * 4
        elif pixel_mode == f'8-bit CLUT':
            intended_width = width_image * 2
        
        image_size = {'X': intended_width, 'Y': height_image}
        
        image_data_itself = image_data[12:]
        if pixel_mode == f'4-bit CLUT':
            for clut_num in range(0, len(clut_data)):
                current_clut = clut_data.get(f'CLUT_{clut_num}')
                current_rgba = []
                for current_pixel in image_data_itself:
                    unfold_byte_1 = current_pixel & 15
                    unfold_byte_2 = current_pixel >> 4
                    for byte in (unfold_byte_1, unfold_byte_2):
                        byte_pixel = current_clut[(byte*2):(byte*2+2)]
                        byte_pixel_int_4bit = int.from_bytes(byte_pixel, 'little')
                        rgba = b''.join([int.to_bytes(x, 1, 'big') for x in (TimDecoder.convert_5_to_8(byte_pair=byte_pixel_int_4bit))])
                        current_rgba.append(rgba)
                joined_rgba = b''.join(current_rgba)
                rgba_data_combined[f'IMAGE_{clut_num}'] = joined_rgba
        
        elif pixel_mode == f'8-bit CLUT':
            for clut_num in range(0, len(clut_data)):
                current_clut = clut_data.get(f'CLUT_{clut_num}')
                current_rgba = []
                for current_pixel in image_data_itself:
                    byte_pixel = current_clut[(current_pixel*2):(current_pixel*2+2)]
                    byte_pixel_int_8bit = int.from_bytes(byte_pixel, 'little')
                    rgba = b''.join([int.to_bytes(x, 1, 'big') for x in (TimDecoder.convert_5_to_8(byte_pair=byte_pixel_int_8bit))])
                    current_rgba.append(rgba)
                joined_rgba = b''.join(current_rgba)
                rgba_data_combined[f'IMAGE_{clut_num}'] = joined_rgba
        
        return rgba_data_combined, image_size
    
    @staticmethod
    def convert_5_to_8(byte_pair):
        b = CONVERT_5_TO_8_BIT[(byte_pair >> 10) & 0b11111]
        g = CONVERT_5_TO_8_BIT[(byte_pair >> 5) & 0b11111]
        r = CONVERT_5_TO_8_BIT[byte_pair & 0b11111]
        a = byte_pair >> 15
        if b == 0 and g == 0 and r == 0:
            if a == 1:
                a = 255 
            else:
                a = 0
        else:
            if a == 0:
                a = 255 
            else:
                a = 127

        return r, g, b, a

    @classmethod
    def process_tim(cls, image_data_rgba=dict, size_image=dict, preview_flag=str):
        size_width = size_image.get('X')
        size_height = size_image.get('Y')
        img_byte_arr = []
        if preview_flag == f'preview':
            img_byte_arr = preview_textures.PreviewTexture.preview_texture(texture_type='TIM', rgba_data=image_data_rgba, size_w=size_width, size_h=size_height, align_w=0, align_h=0)
            return img_byte_arr