"""

This module will do the "on fly" conversion for 
In Real Time Preview, since there are three major
types of Textures, this module must be flexible and fast

"""
from tkinter import messagebox
from PIL import Image
import io


class PreviewTexture:
    def __init__(self) -> bytes:
        self.self = PreviewTexture
        self.preview_texture()
        
    def preview_texture(texture_type=str, rgba_data=bytes, size_w=int, size_h=int, align_w=int, align_h=int):
        img_byte_arr = b''
        tim_list = []
        if texture_type == 'TIM':
            total_files = len(rgba_data)
            for current_file in range(0, total_files):
                this_file = rgba_data.get(f'IMAGE_{current_file}')
                img = Image.frombytes('RGBA', (size_w, size_h), this_file)
                img_byte_arr_tim = io.BytesIO()
                img.save(img_byte_arr_tim, format='png')
                img_byte_arr_tim = img_byte_arr_tim.getvalue()
                tim_list.append(img_byte_arr_tim)
            return tim_list

        elif texture_type == 'MCQ':
            if size_h == 256:
                img = Image.frombytes('RGBA', (size_w, size_h), rgba_data)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='png')
                img_byte_arr = img_byte_arr.getvalue()
            else:
                img = Image.frombytes('RGBA', (align_w, align_h), rgba_data)
                unshuffled_img = Image.new('RGBA', (size_w, size_h), None)
                img_tile_list = []
                for x in range(0, align_w, 16):
                    for y in range(0, align_h, 16):
                        img_tile_list.append(img.crop((x, y, x+16, y+16)))
                for x in range(0, size_w, 16):
                    for y in range(0, size_h, 16):
                        tile = img_tile_list.pop(0)
                        unshuffled_img.paste(tile, (x, y, x+16, y+16))
                img_byte_arr = io.BytesIO()
                unshuffled_img.save(img_byte_arr, format='png')
                img_byte_arr = img_byte_arr.getvalue()
        
        elif texture_type == 'PXL':

            for keyname in rgba_data:
                data_to_png = rgba_data.get(f'{keyname}')
                img = Image.frombytes('RGBA', (64, 112), data_to_png)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='png')
                img_byte_arr = img_byte_arr.getvalue()
                tim_list.append(img_byte_arr)

        else:
            error_msg_00 = f'Texture can\'t be previewed into PNG, {texture_type} is not a supported type of Texture'
            error_box_00 = messagebox.showerror(title=f'Critical!!!', message=error_msg_00)
            raise ValueError(error_msg_00)
        
        if tim_list != []:
            return tim_list
        elif img_byte_arr != b'':
            return img_byte_arr