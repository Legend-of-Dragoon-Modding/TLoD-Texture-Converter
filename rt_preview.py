"""

RT_Preview: This module do the link between the selection done by user
in the Treeview and the "In Real Time" Previewing

"""

import tim_decoder
import mcq_decoder
import tim_embedded_decoder

TIM_TYPES = ['TIM: 4-Bit CLUT', 'TIM: 8-Bit CLUT', 'TIM: Various Configs']

class PreviewTexture:
    def __init__(self, t_filepath=str, t_type=str, sp_flag=int) -> dict:
        self.self = PreviewTexture
        self.texture_file_decoded(path=t_filepath, text_type=t_type, sp_flag=sp_flag)
    
    def texture_file_decoded(self, path, text_type, sp_flag, texture_number):
        png_file = b''
        preview_texture = 'preview'
        
        if text_type == 'MCQ':
            png_file = mcq_decoder.McqDecoder.decode_mcq_data(mcq_decoder.McqDecoder, file_path=path, ispreview=preview_texture)
        elif text_type in TIM_TYPES:
            png_file = []
            if sp_flag == 0 or sp_flag == 1:
                png_file = tim_decoder.TimDecoder.decode_tim_data(tim_decoder.TimDecoder, file_path=path, is_preview=preview_texture, special_flag=sp_flag)
            elif sp_flag == 2:
                png_file = tim_embedded_decoder.TimEmbeddedDecoder.handle_embedded_tims(tim_embedded_decoder.TimEmbeddedDecoder, file_path=path, is_preview=preview_texture, number_of_file=texture_number)
        else:
            pass # IF IN THE FUTURE WE SUPPORT PXL FROM SUBMAPS {NEED FILE MAPPING DONE FOR THIS}, IT WILL BE HERE
        
        return png_file