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

TIM_MAGIC = b'\x10\x00\x00\x00'
CONVERT_5_TO_8_BIT = [0, 8, 16, 25, 33, 41, 49, 58,
                      66, 74, 82, 90, 99, 107, 115, 123,
                      132, 140, 148, 156, 165, 173, 181, 189,
                      197, 206, 214, 222, 230, 239, 247, 255]

class TimPng:
    def __init__(self, file_to_decode=str, flag=str):
        self.file_to_decode: str = file_to_decode
        self.flag: str = flag
        self.tim_decoded: dict = {}
        self.decode_tim_data()

    def decode_tim_data(self) -> None:

        tim_to_png: dict = {'SizeImg': {}, 'RGBA_Data': {}}

        tim_flag: dict = {'Pixel_Mode': '', 'is_CLUT': ''}
        tim_data: dict = {'CLUT': [], 'Pixel_Data': []}
        
        binary_data: bytes = None
        with open(self.file_to_decode, 'rb') as tim_binary_data:
            
            if self.flag == 'NONE':
                binary_data = tim_binary_data.read()
            elif self.flag == 'EMBEDDED':
                tim_binary_data.seek(57116)
                binary_data = tim_binary_data.read()
            this_tim_magic = binary_data[0:4]
            if this_tim_magic != TIM_MAGIC:
                raise ValueError(f'File: {self.file_to_decode}, is not a Standard TIM File!')
            tim_binary_data.close()
            
        # READ TIM FLAGs
        flag_data = binary_data[4:8]
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
            tim_flag['is_CLUT'] = 'CLUT'
            read_clut_length = binary_data[8:12]
            clut_length = int.from_bytes(read_clut_length, byteorder='little', signed=False)
            tim_data_clut = binary_data[8:(clut_length + 8)]
            tim_data['CLUT'] = tim_data_clut
            tim_pixel_data = binary_data[(clut_length + 8):]
            tim_data['Pixel_Data'] = tim_pixel_data
            len_all_taken= len(tim_pixel_data) + len(tim_data_clut) + 8 # This 8 represent the header + flag
            len_all_file = len(binary_data)
            if len_all_taken != len_all_file:
                raise ValueError(f'Critical!!: Some Calculations in file length went wrong! Expected: {len_all_file}, Obtained: {len_all_taken}')
        else:
            tim_flag['is_CLUT'] = 'NO-CLUT'
            read_pixel_data_len = binary_data[8:12]
            pd_noclut_len_int = int.from_bytes(read_pixel_data_len, byteorder='little', signed=False)
            read_pd_noclut = binary_data[8: pd_noclut_len_int]
            tim_data['Pixel_Data'] = read_pd_noclut

        rgba_data, size_img = self.split_data(get_flags=tim_flag, get_tim_data=tim_data)
        align_data = {'AX': 0, 'AY': 0}
        tim_to_png = {'SizeImg': size_img, 'RGBA_Data': rgba_data, 'alignData': align_data, 'textureType': 'TIM'}
        
        self.tim_decoded = tim_to_png
    
    def split_data(self, get_flags=dict, get_tim_data=dict) -> tuple[dict, dict]:
        rgba_data: dict = {}
        img_size: dict = {}
        get_clut_flag = get_flags.get('is_CLUT')
        get_pixel_mode = get_flags.get('Pixel_Mode')
        get_img_data = get_tim_data.get('Pixel_Data')
        get_clut = get_tim_data.get('CLUT')
        if get_clut_flag == 'CLUT':
            processed_clut = self.split_clut(clut_data=get_clut, type_clut=get_pixel_mode)
            processed_image_data, img_size_got = self.combine_image(image_data=get_img_data, clut_data=processed_clut, pixel_mode=get_pixel_mode)
            rgba_data = processed_image_data
            img_size = img_size_got
        else:
            raise ValueError(f'Critical!!: CLUTless TIM Type not supported at the moment')
        
        return rgba_data, img_size

    def split_clut(self, clut_data=bytes, type_clut=str) -> dict:
        split_clut = {}
        clut_data_itself = clut_data[12:]
        
        if type_clut == f'4-bit CLUT':
            total_clut_entries = len(clut_data_itself) // 32
            next_clut = 0
            clut_entry_num = 0
            for current_clut_entry in range(total_clut_entries):
                this_clut = clut_data_itself[next_clut:(next_clut + 32)]
                if this_clut != (b'\x00' * 32):
                    split_clut[f'CLUT_{clut_entry_num}'] = this_clut
                    clut_entry_num += 1
                next_clut += 32
        
        elif type_clut == f'8-bit CLUT':
            total_clut_entries = len(clut_data_itself) // 512
            next_clut = 0
            clut_entry_num = 0
            for current_clut_entry in range(total_clut_entries):
                this_clut = clut_data_itself[next_clut:(next_clut + 512)]
                if this_clut != (b'\x00' * 512):
                    split_clut[f'CLUT_{clut_entry_num}'] = this_clut
                    clut_entry_num += 1
                next_clut += 512
        else: # Should i elaborate more in the different types for TLoD?
            raise ValueError(f'Critical!!: {type_clut} not supported')

        return split_clut
    
    def combine_image(self, image_data=bytes, clut_data=dict, pixel_mode=str) -> tuple[dict, dict]:
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
        total_of_cluts = len(clut_data)
        unfolded_byte_pairs = []
        for current_pixel in image_data_itself: # EACH PIXEL from Pixel Data
            unfold_byte_1 = current_pixel & 15 # UNFOLD one PIXEL from Pixel Data
            unfold_byte_2 = current_pixel >> 4 # UNFOLD one PIXEL from Pixel Data
            both_unfold = [unfold_byte_1, unfold_byte_2]
            unfolded_byte_pairs.append(both_unfold)

        if pixel_mode == f'4-bit CLUT':
            # applying the 16bit to 32bit conversion before doing the CLUT selection... this is an awesome idea from Monoxide
            final_cluts = {}
            for clut_num in range(0, total_of_cluts):
                current_clut = clut_data.get(f'CLUT_{clut_num}')
                lenght_current_clut = len(current_clut) // 2
                start_pair = 0
                clut_converted = []
                for current_byte_number in range(0, lenght_current_clut):
                    current_byte = current_clut[start_pair : (start_pair + 2)]
                    convert_current_byte = int.from_bytes(current_byte, 'little')
                    rgba = b''.join(self.convert_5_to_8(byte_pair=convert_current_byte))
                    clut_converted.append(rgba)
                    start_pair += 2
                join_clut = b''.join(clut_converted)
                final_cluts[f'CLUT_{clut_num}'] = join_clut
            
            for clut_num in range(0, total_of_cluts): # IN RANGE OF CLUTS
                current_clut = final_cluts.get(f'CLUT_{clut_num}') # IN THIS CLUT
                current_rgba = [] # CURRENT RGBA OF THE IMAGE
                for current_pixel in unfolded_byte_pairs: # EACH PIXEL from Pixel Data
                    for byte in current_pixel: # EACH OF UNFOLD BYTE -> To apply the CLUT
                        byte_pixel = current_clut[(byte*4):(byte*4+4)] # THE BYTE INDICATE THE BYTE COLOR IN A PIXEL OF THE CLUT
                        current_rgba.append(byte_pixel) # APPEND THIS BYTE
                joined_rgba = b''.join(current_rgba) # JOIN THE PREVIOUS PROCESSED BYTES
                rgba_data_combined[f'IMAGE_{clut_num}'] = joined_rgba # ONCE ALL PROCESSED IS SENT TO THE FINAL IMAGE ARRAY
        
        elif pixel_mode == f'8-bit CLUT':
            for clut_num in range(0, total_of_cluts):
                current_clut = clut_data.get(f'CLUT_{clut_num}')
                current_rgba = []
                for current_pixel in image_data_itself:
                    byte_pixel = current_clut[(current_pixel*2):(current_pixel*2+2)]
                    this_current_byte = int.from_bytes(byte_pixel, 'little')
                    rgba = b''.join(self.convert_5_to_8(byte_pair=this_current_byte))
                    current_rgba.append(rgba)
                joined_rgba = b''.join(current_rgba)
                rgba_data_combined[f'IMAGE_{clut_num}'] = joined_rgba
        
        return rgba_data_combined, image_size
    
    def convert_5_to_8(self, byte_pair) -> tuple[bytes, bytes, bytes, bytes]:
        b_int = CONVERT_5_TO_8_BIT[(byte_pair >> 10) & 0b11111]
        g_int = CONVERT_5_TO_8_BIT[(byte_pair >> 5) & 0b11111]
        r_int = CONVERT_5_TO_8_BIT[byte_pair & 0b11111]
        a_int = byte_pair >> 15
        if b_int == 0 and g_int == 0 and r_int == 0:
            if a_int == 1:
                a_int = 255 
            else:
                a_int = 0
        else:
            if a_int == 0:
                a_int = 255 
            else:
                a_int = 127
        r = int.to_bytes(r_int, 1, 'big')
        g = int.to_bytes(g_int, 1, 'big')
        b = int.to_bytes(b_int, 1, 'big')
        a = int.to_bytes(a_int, 1, 'big')
        return r, g, b, a