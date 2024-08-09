"""

Texture Type Interface: This module do the link between the selection done by user
in the Treeview and the "In Real Time" Previewing, using a simple interface to check
which type of file is being selected

"""

from tim_decoder import TimPng
from mcq_decoder import McqPng

class PngTexture:
    def __init__(self, texture_path=str, texture_type=str, flag=str) -> dict:
        self.texture_path = texture_path
        self.texture_type = texture_type
        self.flag = flag
        self.png_texture: dict = {}
        self.texture_file_decoded()
    
    def texture_file_decoded(self) -> None:
        png_file: dict = {}
        
        if self.texture_type != 'MCQ':
            conversion_tim = TimPng(file_to_decode=self.texture_path, flag=self.flag)
            png_file = conversion_tim.tim_decoded
        elif self.texture_type == 'MCQ':
            conversion_mcq = McqPng(file_to_decode=self.texture_path)
            png_file = conversion_mcq.mcq_decoded
        else:
            pass # IF IN THE FUTURE WE SUPPORT PXL FROM SUBMAPS {NEED FILE MAPPING DONE FOR THIS}, IT WILL BE HERE

        self.png_texture = png_file