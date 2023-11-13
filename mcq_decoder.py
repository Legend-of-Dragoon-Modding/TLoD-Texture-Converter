"""

This Module have the MCQ Decoder:
First of all, what's MCQ?, well MCQ
is a file used in TLoD to generate the Skyboxes,
this files are processed by the Engine to be a Dome/Cylinder shape,
while in the file actually is a 2D Image split into Rectanle/Quads
Anyhow the 3D Processing and building is done entirely Engine Side

Specs:
[MCQ Header] ==> 0x 2C
[MCQ Data] ==> 0x NN

--MCQ Header--
MAGIC ==> \x4D\x43\x51\x02 or \x4D\x43\x51\x01 -> MCQ_  >>> Fixed
Data Offset ==> 4 Bytes >>> INT
VRAMWidth ==> 2 Bytes||VRAMHeight ==> 2 Byes    >>> 2 Short
CLUT_X ==> 2 Bytes||CLUT_Y ==> 2 Bytes  >>> 2 Unsigned Short
UV ==> U: 2 Bytes ||V: 2 Bytes  >>> 2 Unsigned Short
ScreenWidth ==> 2 Bytes|| ScreenHeigth ==> 2 Bytes >>> 2 Unsigned Short
Color_0 ==> 2 Bytes || Color_1 ==> 2 Bytes  >>> Color Data
ScreenOffset_X ==> 2 Bytes||ScreenOffset_Y ==> 2 Bytes  >>> 2 Short

ScreenWidth and ScreenHeight is actually the size in pixels of the MCQ Texture

--MCQ Data--
Image data is like PXL files, but
CLUT Data is on the left of each row
and each CLUT applies to one tile.

This code is pretty much a copy'n'paste of the TFZ original code
so all the credits to him!:
TheFlyingZamboni => https://github.com/theflyingzamboni

"""
from tkinter import messagebox
import preview_textures

MCQ_MAGIC_1 = b'\x4D\x43\x51\x01'
MCQ_MAGIC_2 = b'\x4D\x43\x51\x02'

class McqDecoder:
    def __init__(self, file_to_decode=str, ispreview=str):
        self.self = McqDecoder
        self.file_to_decode = file_to_decode
        self.is_preview = ispreview
        self.decode_mcq_data(file_path=self.file_to_decode)
    
    def decode_mcq_data(self, file_path=str, ispreview=str) -> bytes:
        image_data = b''
        image_properties = {'CLUT_WIDTH': 0, 'X': 0, 'Y': 0}
        with open(file_path, 'rb') as mcq_binary_data:
            read_mcq = mcq_binary_data.read()
            read_mcq_magic = read_mcq[0:4]

            if (read_mcq_magic != MCQ_MAGIC_1) and (read_mcq_magic != MCQ_MAGIC_2):
                error_msg_00 = f'Critical!!: {file_path} is not a MCQ TLoD File!'
                error_folder_window = messagebox.showerror(title='System Error...', message=error_msg_00)
                raise TypeError(error_msg_00)
            
            data_start_bin = read_mcq[4:8]
            data_start = int.from_bytes(data_start_bin, byteorder='little', signed=False)
            data_image_get = read_mcq[data_start:]
            image_data = data_image_get
            image_width = int.from_bytes(read_mcq[20:22], 'little', signed=False)
            image_height = int.from_bytes(read_mcq[22:24], 'little', signed=False)
            image_properties['X'] = image_width
            image_properties['Y'] = image_height
            image_properties['CLUT_WIDTH'] = int.from_bytes(read_mcq[16:18], 'little', signed=False)
        decoded_mcq_data, w_int, h_int, aw, ah = self.split_data_image(mcq_binary=image_data, img_prop=image_properties)
        png_file = self.processed_mcq(rgba_data=decoded_mcq_data, w=w_int, h=h_int, align_width=aw, align_height=ah, image_output_type=ispreview)
        return png_file
    
    @classmethod
    def split_data_image(cls, mcq_binary=bytes, img_prop=dict):
        image_width = img_prop.get(f'X')
        image_height = img_prop.get(f'Y')
        clut_width = img_prop.get('CLUT_WIDTH')
        
        # We need some alignments before start working, this side no matters if Y > X, since we need to work always as Y < X
        align_width = (image_width * image_height) // 256
        align_height = 256
        align_width = tile_count = align_width + (align_width % 16) if align_width > 16 else 16
        # In this block get the CLUTs and the Image Data
        image_data_rows = []
        clut_1 = []
        clut_2 = []
        clut_3 = []
        move_slice = 0
        for i in range(0, 256):
            clut_1_get = mcq_binary[move_slice:(move_slice + 32)]
            clut_1.append(clut_1_get)
            move_slice += 32
            if clut_width > 16:
                clut_2_get = mcq_binary[move_slice:(move_slice + 32)]
                clut_2.append(clut_2_get)
                move_slice += 32
                if clut_width > 32:
                    clut_3_get = mcq_binary[move_slice:(move_slice + 32)]
                    clut_3.append(clut_3_get)
                    move_slice += 32
            row = []
            for j in range(align_width // 16):
                r = mcq_binary[move_slice: (move_slice + 8)]
                move_slice += 8
                if r == b'':
                    r = b'\x00' * 8
                row.append(r)
            image_data_rows.append(row)
        concatenate_clut = clut_1 + clut_2 + clut_3
        final_clut = concatenate_clut[:tile_count]
        # Now we do some operations over the rows of data
        row_data_combined = []
        offset_clut = 0
        for i, row in enumerate(image_data_rows):
            clut_index = 0

            if (i % 16 == 0) and (i > 0):
                offset_clut += 1

            for tile_row in row:
                current_clut = final_clut[clut_index + offset_clut]
                new_combined_row = b''
                for pixel in tile_row:
                    byte1 = pixel & 0x0f
                    byte2 = pixel >> 0x04
                    byte_pair1 = current_clut[byte1 * 2:byte1 * 2 + 2]
                    new_combined_row += byte_pair1
                    byte_pair2 = current_clut[byte2 * 2:byte2 * 2 + 2]
                    new_combined_row += byte_pair2
                row_data_combined.append(new_combined_row)
                clut_index += 16
        
        joined_data_combined = b''.join(row_data_combined)
        byte_pixel_list = []
        while len(joined_data_combined) != 0:
            get_this_join = joined_data_combined[:2]
            byte_pixel_list.append(get_this_join)
            joined_data_combined = joined_data_combined[2:]
        
        rgba_data = []
        for bytepixel in byte_pixel_list:
            bp = int.from_bytes(bytepixel, 'little')
            a = 0b11111111 if (bp >> 15 == 0) else 0b01111111
            b = ((bp >> 10) & 0b11111) << 3
            g = ((bp >> 5) & 0b11111) << 3
            r = (bp & 0b11111) << 3
            rgba = [int.to_bytes(x, 1, 'big') for x in (r, g, b, a)]
            rgba_data.extend(rgba)
        
        final_rgba = b''.join(rgba_data)

        return final_rgba, image_width, image_height, align_width, align_height
    
    @classmethod
    def processed_mcq(cls, rgba_data=bytes, w=int, h=int, align_width=int, align_height=int, image_output_type=str):
        if image_output_type == f'preview':
            img_byte_arr = preview_textures.PreviewTexture.preview_texture(texture_type='MCQ', rgba_data=rgba_data, size_w=w, size_h=h, align_w=align_width, align_h=align_height)
            return img_byte_arr