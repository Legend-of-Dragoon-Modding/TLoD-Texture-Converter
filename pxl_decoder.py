"""

This Module contains TLoD PXL file format Decoder:
PXL files are a bunch of image data directly dump
to the VRAM in PSX, in TLoD workaround, instead of
using a single PXL for a single Texture, they use a single
sheet to put more textures on it, TFZ and his awesome work
show that a single texture always is 64*128 (X*Y) in which
the lower part of the image have the CLUT. So the Texture
is 64 * 112 and 64 * 16 for CLUT.

In TLoD there are two PXL files Length:
32780 (0x800C) Bytes
16396 (0x400C) Bytes

[Header = 0x11 00 00 00] --> PXL File Header
[FLAG = 0x nn nn nn nn] --> PXL Flag (LSB = PMode = 0 {4-bit}; 1 {8-bit} -> CLUT)
[Pixel Data]
||
++
Pixel Data:
{[bnum = length of the sheet in bytes]
[DY ; DX = Framebuffer Coordinates in 16 bit U_INT]
[H ; W = Size data in (Vertical; Horizontal) Position. 16 bit U_INT] -> Height = H * 4
[Data N; Data N-1 = VRAM 16 bit Data]
||
++
VRAM Data (length always 16 bit):
4-bit MODE -> {pix3, pix2, pix1, pix0}
pix(n): 4-bit each pixel data

8-bit MODE -> {pix1, pix0}
pix(n): 8-bit each pixel data

16-bit MODE -> {STP, B, G, R} 
STP: Transparency Control Bit
R: Red 5-bit
G: Green 5-bit
B: Blue 5-bit
}

"""
import os
import preview_textures

PXL_HEADER = b'\x11\x00\x00\x00'

class PxlFileDecoder:
    def __init__(self, file_to_decode=str):
        self.self = PxlFileDecoder
        self.file_to_decode = file_to_decode
        self.decode_pxl_data(file_path=self.file_to_decode)
    
    def decode_pxl_data(self, file_path=str):
        binary_image_data = []
        with open(file_path, 'rb') as pxl_data:
            read_file_pxl = pxl_data.read()
            read_pxl_header = read_file_pxl[0:4]
            
            if read_pxl_header != PXL_HEADER:
                raise TypeError(f'Critical!!: {file_path} is not a PXL TLoD File!')
            
            read_pxl_flag = read_file_pxl[4:8]
            flag_type = f''
            pxl_flag_int = int.from_bytes(bytes=read_pxl_flag, byteorder='little', signed=False)
            if pxl_flag_int == 0:
                flag_type = '4-bit'
            elif pxl_flag_int == 1:
                flag_type = '8-bit'
            else:
                raise ValueError(f'Critical!: imposible flag type {pxl_flag_int}, expected 0 or 1')
            
            binary_image_data.append(read_file_pxl[8:])
        rgba_process = self.split_data_image(pxl_binary=binary_image_data, file_name=file_path)
        png = self.processed_pxl(rgba_data=rgba_process)
        return png
    
    @classmethod
    def split_data_image(cls, pxl_binary=list, file_name=str):
        read_length_init = pxl_binary[0]
        read_length = read_length_init[0:4]
        read_file = pxl_binary[0]
        length_int = int.from_bytes(read_length, byteorder='little', signed=False)
        precalc_length_pxl_block = len(read_length_init)
        
        if precalc_length_pxl_block != length_int:
            raise ValueError(f'Critical!!: Length of byte array don\'t match, pre-calculated: {precalc_length_pxl_block}, wrote in file: {length_int}')
        
        image_size = read_length_init[8:12]
        size_width_bin = image_size[0:2]
        size_height_bin = image_size[2:4]
        size_width = int.from_bytes(size_width_bin, byteorder='little', signed=False) * 4 # the Y is halved by 4 in file specification
        size_height = int.from_bytes(size_height_bin, byteorder='little', signed=False)
        
        start_image_data = 12
        image_data = read_file[start_image_data:]
        image_data_size = len(image_data) // 128
        # Getting the row of data
        start_row = 0
        image_rows = []
        for current_row in range(0, image_data_size):
            get_row = image_data[start_row: (start_row + 128)]
            image_rows.append(get_row)
            #print(current_row, get_row) -> Debug Print
            #print(f'Current_slice: {start_row}') -> Debug Print
            start_row += 128
        # Split the Column at half
        length_rows = len(image_rows)
        images_split = {'Image_0': [], 'Image_1': [], 'Image_2': [], 'Image_3': [], 'Image_4': [], 'Image_5': [], 'Image_6': [], 'Image_7': []}
        for current_number_row in range(0, length_rows):
            if current_number_row <= 127:
                current_image_row = image_rows[current_number_row]
                row_left_left = current_image_row[0:32]
                row_left_mid = current_image_row[32:64]
                row_right_mid = current_image_row[64:96]
                row_right_right = current_image_row[96:128]
                images_split['Image_0'].append(row_left_left)
                images_split['Image_1'].append(row_left_mid)
                images_split['Image_2'].append(row_right_mid)
                images_split['Image_3'].append(row_right_right)
            else:
                current_image_row_down = image_rows[current_number_row]
                row_left_left_down = current_image_row_down[0:32]
                row_left_mid_down = current_image_row_down[32:64]
                row_right_mid_down = current_image_row_down[64:96]
                row_right_right_down = current_image_row_down[96:128]
                images_split['Image_4'].append(row_left_left_down)
                images_split['Image_5'].append(row_left_mid_down)
                images_split['Image_6'].append(row_right_mid_down)
                images_split['Image_7'].append(row_right_right_down)
        
        image_len = None
        if length_rows == 256:
            image_len = 8
        elif length_rows == 128:
            image_len = 4
        else:
            raise ValueError(f'Unsupported length of file for PXL file {file_name}')
        
        image_split_final = {}
        image_number_fill = 0
        for current_image_number in range(0, image_len):
            image_key = f'Image_{current_image_number}'
            get_current_image_data = images_split.get(f'{image_key}')

            # The Image data goes from Row 0 to 111, CLUT data goes from 112 to 128
            length_row_image = (len(get_current_image_data))
            current_image_to_join = []
            current_cluts_row = []
            for current_row in range(0, length_row_image):
                if current_row <= 111:
                    this_image_row = get_current_image_data[current_row]
                    current_image_to_join.append(this_image_row)
                else:
                    this_clut_row = get_current_image_data[current_row]
                    if this_clut_row != (b'\x00' * 32):
                        current_cluts_row.append(this_clut_row)
            
            joined_curr_img = b''.join(current_image_to_join)
            if joined_curr_img != (b'\x00' * 3584):
                image_split_final[f'IMG_{image_number_fill}'] = {'DATA': joined_curr_img, 'CLUT': current_cluts_row}
                image_number_fill += 1

        rgba_data = {}
        length_data = len(image_split_final)
        for current_img_num in range(0, length_data):
            current_img = image_split_final.get(f'IMG_{current_img_num}')
            current_img_data = current_img.get(f'DATA')
            current_clut_data = current_img.get(f'CLUT')
            clut_number = 0
            for current_clut in current_clut_data:
                this_data_combined = []
                for pixel in current_img_data:
                    pixel_unfold_1 = pixel & 15
                    pixel_unfold_2 = pixel >> 4
                    for byte_change in (pixel_unfold_1, pixel_unfold_2):
                        bp = current_clut[byte_change * 2 : byte_change * 2 + 2]
                        bp = int.from_bytes(bp, 'little')
                        alpha = 0b00000000 if not bp else 0b01111111 if (bp >> 15 == 1) else 0b11111111
                        blue = ((bp >> 10) & 0b11111) << 3
                        green = ((bp >> 5) & 0b11111) << 3
                        red = (bp & 0b11111) << 3
                        rgba_byte_obtained = []
                        for byte_formed in (red, green, blue, alpha):
                            byte_converted = int.to_bytes(byte_formed, length=1, byteorder='big')
                            rgba_byte_obtained.append(byte_converted)
                        rgba_byte_joined = b''.join(rgba_byte_obtained)
                        this_data_combined.append(rgba_byte_joined)
                this_data_combined_join = b''.join(this_data_combined)
                rgba_data[f'IMG_{current_img_num}_Layer_{clut_number}'] = this_data_combined_join
                clut_number += 1
        return rgba_data
        
    @classmethod
    def processed_pxl(cls, rgba_data=bytes, image_output_type=str):
        image_output_type = f'preview'
        if image_output_type == f'preview':
            img_byte_arr = preview_textures.PreviewTexture.preview_texture(texture_type='PXL', rgba_data=rgba_data, size_w=64, size_h=112)
            return img_byte_arr