"""

Main GUI module for TLoD Texture Converter:
This GUI it's split into Main Window,
Configuration Window,
Convert Previewed,
Convert Batch


"""
import os
from tkinter import CENTER, Tk, Frame, messagebox, Canvas, Label, Button, LabelFrame, Scrollbar, Toplevel, Spinbox, IntVar, Checkbutton, ttk, Entry, END, Text, StringVar
from tkinter.filedialog import askopenfile, askdirectory, asksaveasfilename
from tktooltip import ToolTip
from PIL import ImageTk, Image
import process_database_file as dtl
import webbrowser
from texture_type_interface import PngTexture
from preview_textures import TexturePreview
import convert_advanced
import io

class Options:
    def __init__(self):
        self.self = Options
        self.read_write_options()
    
    def read_write_options(self):
        self.option_file = f'Resources/converter_config.config'
        global size_x
        global size_y
        global sc_folder_def
        global dump_folder
        global first_run
        size_x = None
        size_y = None
        sc_folder_def = None
        dump_folder = None
        first_run = True

        little_root = Tk()
        little_root.iconbitmap(default='Resources/Lavitz_Painting.ico')
        little_root.wm_withdraw()
        with open(self.option_file, 'r') as read_config: # Reading the Config file to
            read_all_config = read_config.readlines()
            # First Run Check
            config_first_run = read_all_config[1]
            read_fr = config_first_run[12:].strip()
            if read_fr == f'True':
                start_config = messagebox.showinfo(title='First Time Configuration', message='Now we will do a Startup Configuration...')
            else:
                first_run = False

            # Size X, Y Check
            config_x_size = read_all_config[2]
            r_a_config_x = config_x_size[15:].strip()
            size_x = int(r_a_config_x)
            
            config_y_size = read_all_config[3]
            r_a_config_y = config_y_size[15:].strip()
            size_y = int(r_a_config_y)
            
            # Severed Chains Dump folder Check
            start_read_sc = read_all_config[4]
            read_sc = start_read_sc[11:].strip()
            if read_sc != f'None':
                sc_folder_def = read_sc
            else:
                messagebox.showinfo(title=f'SELECT SC FOLDER', message='Please select the folder called \"files\" in SC root folder')
                root_files_sc = askdirectory(title='Select files folder from SC')
                getting_all_folders = os.walk(root_files_sc)

                if root_files_sc == f'':
                    messagebox.showerror(title=f'Incorrect SC FOLDER', message='FATAL CRASH!: Folder not selected')
                    first_run = True
                    exit()

                for root, dirs, files in getting_all_folders:
                    if f'files' in root:
                        sc_folder_def = root_files_sc
                        break
                    else:
                        messagebox.showerror(title=f'Incorrect SC FOLDER', message=f'Something went wrong, this is not the SC root folder')
                        first_run = True
                        exit()
                
            # Conversion Dump Folder Check
            start_read_dump = read_all_config[5]
            read_dump = start_read_dump[13:].strip()
            if read_dump == f'None':
                messagebox.showinfo(title='SELECT A FOLDER TO DUMP', message='Please, select a folder to dump converted files.\nRecommendation: Do not create inside SC FOLDER')
                new_dump_folder = askdirectory(title='SELECT A FOLDER TO DUMP FILES')
                dump_folder = new_dump_folder
            else:
                dump_folder = read_dump
        
        self.write_options(self, path_cnf_file=self.option_file, first_run=False, size_x=size_x, size_y=size_y, sc_folder_def=sc_folder_def, dump_folder=dump_folder)
        little_root.destroy()
        return size_x, size_y
    
    def write_options(self, path_cnf_file=str, first_run=bool, size_x=int, size_y=int, sc_folder_def=str, dump_folder=str):
        
        if ((size_x == None) or (size_y == None) or (sc_folder_def == None) or (dump_folder == None)) and (first_run == True):
            return messagebox.showerror(title='FATAL CRASH!!', message='Unexpected condition of First Run, please report this error immediately')
        else:
            path_to_config_file = path_cnf_file
            with open(path_to_config_file, 'w') as writing_options:
                header = f'[CONFIG]\n'
                fr_flag = f'FIRST_RUN = {first_run}\n'
                def_res_x = f'DEFAULT_RES_X = {size_x}\n'
                def_res_y = f'DEFAULT_RES_Y = {size_y}\n'
                def_sc_folder = f'SC_FOLDER = {sc_folder_def}\n'
                dump_f = f'DUMP_FOLDER = {dump_folder}'
                grabbing_every_str = header + fr_flag + def_res_x + def_res_y + def_sc_folder + dump_f
                writing_options.write(grabbing_every_str)


class MainWindow(Frame):
    # Constructor
    def __init__(self, master=None, width=int, height=int):
        super().__init__(master, width=width, height=height)
        self.master = master
        self.pack()
        self.create_widget(width_mainframe=width, height_mainframe=height)
    
    def create_widget(self, width_mainframe=int, height_mainframe=int):
        #### Creation of Main widgets ####
        # Buttons - Labels - Frame - Text [Text Box Output]
        ## Image
        self.image_filename = "Resources/Savan_GUI.png"
        self.texture_database = "Texture_Database/"
        database_files = dtl.DatabaseDict(database_path=self.texture_database)
        self.create_dict_files = database_files.database_processed
        self.open_image = Image.open(self.image_filename)
        self.x_y_values = self.resize_window(width_mainframe_change=width_mainframe, height_mainframe_change=height_mainframe)
        self.resize_image = self.open_image.resize(self.x_y_values, Image.Resampling.LANCZOS)
        self.image_background = ImageTk.PhotoImage(image=self.resize_image)
        ## Canvas (Background image)
        self.background_canvas = Canvas(self, width=self.x_y_values[0], height=self.x_y_values[1])
        ## LabelFrame - Info and Conversion Result
        self.label_info = LabelFrame(self, text='General Information')
        ## Label - Parent Info LabelFrame
        self.texture_label = Label(self.label_info, text= f'Convert the Textures from TLoD into PNG file format, also Preview them\nSupported Formats: TIM, PXL, MCQ', justify=CENTER)
        ## Buttons - Main Frame
        self.texture_button = Button(self.label_info, text='Texture Preview/Conversion', command=self.preview_convert_texture, cursor='hand2')
        self.advanced_texture_button = Button(self.label_info, text='Advanced Texture Conversion', command=self.advanced_conversion, cursor='hand2')
        ToolTip(self.texture_button, msg='Preview and Convert Textures in Real Time or Batch convert them!')
        ToolTip(self.advanced_texture_button, msg='Recommended for advanced users, convert a single file of your choice!')
        ## About Button
        self.about_button = Button(self, text="About", command=self.execute_about, cursor='hand2')
        ## Configuration Button
        self.config_button = Button(self, text='CONFIG', cursor="hand2", command=self.configure_tool)
        ## Github Hyperlink
        self.github_page = Label(self, text='https://github.com/Legend-of-Dragoon-Modding/TLoD-Texture-Converter', font=('Calibri', 11), fg='#0000EE', cursor='hand2')

        #### Placing Methods ####
        self.background_canvas.place(relwidth=1, relheight=1, relx=-0.28, rely= -0.25)
        self.background_canvas.create_image(self.x_y_values[0], self.x_y_values[1], image=self.image_background)
        self.label_info.place(relx=0.26, rely=0.09, relwidth= 0.70, relheight= 0.80)
        self.texture_label.place(relx=0.01, rely=0.001, relwidth= 0.9, relheight= 0.3)
        self.texture_label.config(font=('Arial Black', 12), fg='#4578b0')
        self.texture_button.place(relwidth=0.3, relheight=0.3, relx=0.15, rely=0.30)
        self.advanced_texture_button.place(relwidth=0.3, relheight=0.3, relx=0.55, rely=0.30)
        self.about_button.place(relx=0.05, rely=0.69, relwidth= 0.15, relheight= 0.1)
        self.config_button.place(relx=0.05, rely=0.79, relwidth= 0.15, relheight= 0.1)
        self.github_page.place(relx=0.35, rely=0.93, relwidth= 0.4, relheight= 0.07)
        self.github_page.bind("<Button-1>", lambda e: self.callback_link('https://github.com/Legend-of-Dragoon-Modding/TLoD-Texture-Converter'))

    #### Main Window Callbacks ####
    def resize_window(self, width_mainframe_change=int, height_mainframe_change=int):
        self.image_width_changed = round((60 * width_mainframe_change) / 100)
        self.image_height_changed = round((60 * height_mainframe_change) / 100)
        self.tuple_xy_changed = self.image_width_changed, self.image_height_changed
        return self.tuple_xy_changed
    
    def execute_about(self): # About Button show
        message_about = f'TLoD Texture Converter BETA v0.1 \nCoded By DooMMetal (AKA DragoonSouls) 2023 ©\nThis Tool was made from fans to fans!, keep it as it is!\nVisit my Github for updates\nA Very big THANKS to theflyingzamboni, who shared almost all the Textures Conversion Logic and Codes!!'
        self.message_box_win = messagebox.showinfo('About TLoD Texture Converter', message_about)

    def callback_link(self, url=str):
        webbrowser.open_new_tab(url)

    #### Preview/Convert Textures Window ####
    def preview_convert_texture(self):
        Options.read_write_options(Options)
        # Create new Widget for the Select Box
        self.new_window_box = Toplevel(master=self)
        self.current_texture_path: str = ''
        self.current_texture_type: str = ''
        self.current_texture_name: str = ''
        self.current_texture_flag: str = ''
        self.parent_blacklist: list = []
        self.new_window_box.grab_set()
        self.new_window_box.focus_set()
        x_main = self.x_y_values[0]
        y_main = self.x_y_values[1]
        self.new_window_box.title(string=f'Select the Files you want to Preview')
        self.new_window_box.geometry(f'+%d+%d' %(x_main // 2, y_main // 2))
        self.new_window_box.geometry(f'{x_main + (x_main - 200)}x{y_main + (y_main - 125)}')

        # Labels for placing the Widgets
        self.label_treeview = LabelFrame(self.new_window_box, text='Texture List')
        self.label_preview = LabelFrame(self.new_window_box, text='Preview Texture')
        self.label_conversion_buttons = LabelFrame(self.new_window_box, text='Conversion Controls')

        # Tree View
        self.tree_list = ttk.Treeview(master=self.label_treeview)
        self.tree_list.column("#0", width = 20) # |--> THIS IS THE PLUS to get the list
        # Create and formatting Columns in Treeview Object
        self.tree_list['columns'] = ("Name", "File_Type")
        self.tree_list.column("#0", width=10, minwidth=10, anchor='w')
        self.tree_list.column("Name", width=200, minwidth=50, anchor='w')
        self.tree_list.column("File_Type", width=40, minwidth=30, anchor='w')
        # Create and formatting Headings in Treeview Object
        self.tree_list.heading("#0", text='', anchor='w')
        self.tree_list.heading("Name", text='Texture Name', anchor='w')
        self.tree_list.heading("File_Type", text='File Type', anchor='w')
        # Here i populate the Tree View
        self.populate_treeview()
        # ScrollBar for the Treewview
        self.treeview_scrollbar = Scrollbar(master=self.tree_list, orient ="vertical", command = self.tree_list.yview)
        self.tree_list.configure(yscrollcommand=self.treeview_scrollbar.set)

        # Canvas
        self.preview_canvas = Canvas(master=self.label_preview, background='skyblue')
        # Spinbox for controlling Texture CLUT
        self.current_val_spinbox = StringVar(master=self.label_preview)
        self.spinbox_clut = Spinbox(master=self.label_preview, text=f'Change CLUT', from_=0, textvariable=self.current_val_spinbox, command=self.change_spinbox_val)
        self.spinbox_clut.configure(state='disabled', cursor='arrow')
        ToolTip(self.spinbox_clut, msg='Current Pallete applied to the Texture,\ncan use Mousewheel to change it,\n or use F7 [UP] - F8 [DOWN]')

        # LabelFrame for CLUT Info
        self.clut_info = LabelFrame(master=self.label_preview, text=f'CLUT Info')
        ToolTip(self.clut_info, msg='Information about Texture Pallete, Current Pallete/Total Palletes')
        # Text Labels for CLUT Info
        self.total_cluts_label = Label(master=self.clut_info, text=f'Total Number of CLUTs: ...')
        self.total_cluts_label.configure(state='disabled')

        # Convert Current Texture Button
        self.convert_current_texture = Button(master=self.label_preview, text=f'Convert Texture', command=self.current_texture_convert)
        self.convert_current_texture.configure(state='disabled')
        ToolTip(self.convert_current_texture, msg='Convert Current Texture File...')

        # Save Placement Label
        self.converted_file_framelabel = LabelFrame(master=self.label_preview, text='Exported File Location')
        self.file_location_label = Label(master=self.converted_file_framelabel, text='Export File Path...', anchor='center')
        ToolTip(self.converted_file_framelabel, msg='Place in which the file is placed and exported')

        # Convert ALL Checkboxes
        self.check_convertall_var = IntVar()
        self.convert_all_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Select All', variable=self.check_convertall_var)
        self.convert_all_checkbox.bind('<ButtonRelease-1>', self.check_all_convert)

        # Convert From Parent Button
        self.enable_convert_parent_button = Button(master=self.label_conversion_buttons, text='Enable Parent Conversion', command=self.set_convert_parent)
        # Parent CheckBoxes
        self.check_battlestages_checkbox = IntVar()
        self.convert_battlestages_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Battle Stages', anchor='w', variable=self.check_battlestages_checkbox)
        self.convert_battlestages_checkbox.configure(state='disabled')
        self.check_bosses_checkbox = IntVar()
        self.convert_bosses_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Bosses', anchor='w', variable=self.check_bosses_checkbox)
        self.convert_bosses_checkbox.configure(state='disabled')
        self.check_characters_checkbox = IntVar()
        self.convert_characters_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Characters', anchor='w', variable=self.check_characters_checkbox)
        self.convert_characters_checkbox.configure(state='disabled')
        self.check_cutscenes_checkbox = IntVar()
        self.convert_cutscenes_checkbox = Checkbutton(master=self.label_conversion_buttons, text='CutScenes', anchor='w', variable=self.check_cutscenes_checkbox)
        self.convert_cutscenes_checkbox.configure(state='disabled')
        self.check_enemies_checkbox = IntVar()
        self.convert_enemies_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Enemies', anchor='w', variable=self.check_enemies_checkbox)
        self.convert_enemies_checkbox.configure(state='disabled')
        self.check_menumisc_checkbox = IntVar()
        self.convert_menumisc_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Menu Misc', anchor='w', variable=self.check_menumisc_checkbox)
        self.convert_menumisc_checkbox.configure(state='disabled')
        self.check_skyboxes_checkbox = IntVar()
        self.convert_skyboxes_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Skyboxes', anchor='w', variable=self.check_skyboxes_checkbox)
        self.convert_skyboxes_checkbox.configure(state='disabled')
        self.check_theend_checkbox = IntVar()
        self.convert_theend_checkbox = Checkbutton(master=self.label_conversion_buttons, text='THE END', anchor='w', variable=self.check_theend_checkbox)
        self.convert_theend_checkbox.configure(state='disabled')
        self.check_tutorial_checkbox = IntVar()
        self.convert_tutorial_checkbox = Checkbutton(master=self.label_conversion_buttons, text='Tutorial', anchor='w', variable=self.check_tutorial_checkbox)
        self.convert_tutorial_checkbox.configure(state='disabled')
        self.check_worldmapfield_checkbox = IntVar()
        self.convert_worldmapfield_checkbox = Checkbutton(master=self.label_conversion_buttons, text='World Map Field', anchor='w', variable=self.check_worldmapfield_checkbox)
        self.convert_worldmapfield_checkbox.configure(state='disabled')
        self.check_worldmapthumb_checkbox = IntVar()
        self.convert_worldmapthumb_checkbox = Checkbutton(master=self.label_conversion_buttons, text='World Map Thumbnails', anchor='w', variable=self.check_worldmapthumb_checkbox)
        self.convert_worldmapthumb_checkbox.configure(state='disabled')

        # Convert ALL Textures Button
        self.convert_all_textures = Button(master=self.label_conversion_buttons, text=f'Convert Textures', command=self.convert_textures_button)
        self.convert_all_textures.configure(state='disabled')
        ToolTip(self.convert_all_textures, msg='Convert Texture Files you selected,\n"Select All" for a FULL Conversion\n"Enable Parent Conversion" for selecting specific Parents')

        # Placing Labels
        self.label_treeview.place(relx=0.01, rely=0.01, relwidth=0.3, relheight= 0.97)
        self.label_preview.place(relx=0.32, rely=0.01, relwidth=0.5, relheight= 0.97)
        self.label_conversion_buttons.place(relx=0.825, rely=0.01, relwidth=0.17, relheight= 0.97)
        ## Canvas and Image (Background image)
        self.background_canvas_conversion_buttons = Canvas(master=self.label_conversion_buttons)
        self.background_canvas_conversion_buttons.place(relx=0.01, rely= 0.01, relwidth=0.99, relheight=0.48)
        self.background_canvas_conversion_buttons.update()
        x_label_width = self.background_canvas_conversion_buttons.winfo_width()
        y_label_height = self.background_canvas_conversion_buttons.winfo_height()
        xy_tuple = (x_label_width, y_label_height)
        self.image_filename_2 = "Resources/Savan_GUI_2.png"
        self.open_image_2 = Image.open(self.image_filename_2)
        self.resize_image_2 = self.open_image_2.resize(xy_tuple, Image.Resampling.LANCZOS)
        self.image_background_2 = ImageTk.PhotoImage(image=self.resize_image_2)
        self.background_canvas_conversion_buttons.create_image(x_label_width - 110, y_label_height - 170, image=self.image_background_2, anchor=CENTER)
        # Placing Treeview
        self.tree_list.place(relx=0.01, rely=0.01, relwidth=0.98, relheight= 0.98)
        # Placing ScrollBar (Treeview)
        self.treeview_scrollbar.place(relx=0.948, rely=0.026, relwidth=0.05, relheight= 0.973)
        # Placing Canvas
        self.preview_canvas.place(relx=0.001, rely=0.001, relwidth=0.999, relheight= 0.6)
        # Placing CLUT Spinbox
        self.spinbox_clut.place(relx=0.3, rely=0.65, relwidth=0.5, relheight= 0.05)
        # Placing CLUT Info
        self.clut_info.place(relx=0.3, rely=0.7, relwidth=0.5, relheight= 0.1)
        # Placing CLUT Info Text Label
        self.total_cluts_label.place(relx=0.1, rely=0.1, relwidth=0.8, relheight= 0.3)
        # Placing Save Placement Label
        self.converted_file_framelabel.place(relx=0.005, rely=0.9, relwidth=0.99, relheight= 0.1)
        self.file_location_label.place(relx=0.005, rely=0.1, relwidth=0.99, relheight= 0.8)
        # Placing Convert Current Texture Button
        self.convert_current_texture.place(relx=0.3, rely=0.8, relwidth=0.5, relheight= 0.1)
        # Placing Convert ALL Textures Main Checkbox
        self.convert_all_checkbox.place(relx=0.05, rely=0.5, relwidth=0.3, relheight=0.02)
        # Placing Convert From Parent Button
        self.enable_convert_parent_button.place(relx=0.05, rely=0.53, relwidth=0.7, relheight=0.04)
        # Placing Parent CheckBoxes
        self.convert_battlestages_checkbox.place(relx=0.06, rely=0.57, relwidth=0.8, relheight=0.03)
        self.convert_bosses_checkbox.place(relx=0.06, rely=0.60, relwidth=0.8, relheight=0.03)
        self.convert_characters_checkbox.place(relx=0.06, rely=0.63, relwidth=0.8, relheight=0.03)
        self.convert_cutscenes_checkbox.place(relx=0.06, rely=0.66, relwidth=0.8, relheight=0.03)
        self.convert_enemies_checkbox.place(relx=0.06, rely=0.69, relwidth=0.8, relheight=0.03)
        self.convert_menumisc_checkbox.place(relx=0.06, rely=0.72, relwidth=0.8, relheight=0.03)
        self.convert_skyboxes_checkbox.place(relx=0.06, rely=0.75, relwidth=0.8, relheight=0.03)
        self.convert_theend_checkbox.place(relx=0.06, rely=0.78, relwidth=0.8, relheight=0.03)
        self.convert_tutorial_checkbox.place(relx=0.06, rely=0.81, relwidth=0.8, relheight=0.03)
        self.convert_worldmapfield_checkbox.place(relx=0.06, rely=0.84, relwidth=0.8, relheight=0.03)
        self.convert_worldmapthumb_checkbox.place(relx=0.06, rely=0.87, relwidth=0.8, relheight=0.03)
        # Placing Convert ALL Textures Button
        self.convert_all_textures.place(relx=0.1, rely=0.9, relwidth=0.8, relheight=0.1)

        # Treeview Binds
        self.tree_list.bind('<ButtonRelease-1>', self.selected_treeview)

    # Preview/Convert Populate Treeview List
    def populate_treeview(self):
        for parent_name in self.create_dict_files:
            get_files_from = self.create_dict_files.get(f'{parent_name}')
            self.tree_list.insert(parent='', index='end', iid=f'Parent_{parent_name}', values=(parent_name, 'Parent'))
            self.parent_blacklist.append(parent_name)
            number_add = 0
            for this_files in get_files_from:
                this_files_data = get_files_from.get(f'{this_files}')
                in_disk_type = this_files_data.get('inDiskType')
                if in_disk_type == 'Single-File':
                    get_file_type = this_files_data.get('formatType')
                    get_file_path = this_files_data.get(f'filePath')
                    get_fantasy_name = this_files_data.get(f'fantasyName')
                    fantasy_name_change_underscore = get_fantasy_name.replace(' ', '_')
                    get_flag = this_files_data.get(f'flag')
                    internal_iid = f'{parent_name}#{this_files}${number_add}'
                    this_dump_file_path = f'{dump_folder}\\{parent_name}\\{fantasy_name_change_underscore}'
                    this_file_create = f'{fantasy_name_change_underscore}'
                    self.tree_list.insert(parent=f'Parent_{parent_name}', index='end', 
                                          iid=internal_iid, values=(this_files, get_file_type, get_file_path[0], 
                                                                    get_fantasy_name, get_flag, this_dump_file_path, this_file_create))
                elif in_disk_type == 'FOLDER':
                    get_nested_files = this_files_data.get('filePath')
                    number_add_nested = 0
                    get_file_type = this_files_data.get('formatType')
                    internal_iid = f'SubPar_{parent_name}#{this_files}#{number_add}'
                    self.tree_list.insert(parent=f'Parent_{parent_name}', index='end', iid=internal_iid, values=(this_files, 'FOLDER'))
                    self.parent_blacklist.append(this_files)
                    get_file_path = this_files_data.get(f'filePath')
                    get_fantasy_name = this_files_data.get(f'fantasyName')
                    get_flag = this_files_data.get(f'flag')
                    for texture_parent_folder in get_nested_files:
                        last_name_position = texture_parent_folder.rfind('\\')
                        new_fantasy_name = f'{parent_name}_{number_add_nested}'.replace(' ', '_')
                        file_name = texture_parent_folder[last_name_position + 1:]
                        this_files_change_underscore = this_files.replace(' ', '_')
                        this_dump_file_path = f'{dump_folder}\\{parent_name}\\{this_files_change_underscore}\\{number_add_nested}'
                        this_file_create = f'{number_add_nested}'
                        internal_iid_nested = f'{parent_name}#{texture_parent_folder}${number_add_nested}'
                        self.tree_list.insert(parent=f'SubPar_{parent_name}#{this_files}#{number_add}', index='end', 
                                              iid=internal_iid_nested, values=(new_fantasy_name, get_file_type, texture_parent_folder, 
                                                                               file_name, get_flag, this_dump_file_path, this_file_create))
                        number_add_nested += 1
                number_add += 1

    # Treeview Callbacks - For "In Real Time" Previewing
    """Each 'Final Path' represent the path to the file selected in the Treeview"""
    # TODO Rewrite the code to retrieve CLUT information, CLUT Palette and Other stuff
    def selected_treeview(self, button_info):
        self.preview_canvas.update()
        self.current_val_spinbox.set('0')
        self.current_canvas_width = self.preview_canvas.winfo_width()
        self.current_canvas_height = self.preview_canvas.winfo_height()
        current_selection = self.tree_list.focus()
        current_item_value = self.tree_list.item(current_selection)
        current_texture_properties = current_item_value.get('values')
        current_texture_name = current_texture_properties[0]
        if current_texture_name not in self.parent_blacklist:
            self.spinbox_clut.configure(state='disabled')
            self.current_texture_type = current_texture_properties[1]
            self.current_texture_path = f'{sc_folder_def}\\{current_texture_properties[2]}'
            self.current_texture_name: str = current_texture_properties[3]
            self.current_texture_flag: str = current_texture_properties[4]
            self.current_texture_dump_folder: str = current_texture_properties[5]
            self.current_file_create: str = current_texture_properties[6]
            texture_for_preview = PngTexture(texture_path=self.current_texture_path, texture_type=self.current_texture_type, flag=self.current_texture_flag)
            self.texture_converted: dict = texture_for_preview.png_texture.get('RGBA_Data')
            self.texture_size = texture_for_preview.png_texture.get('SizeImg')
            self.number_of_cluts = len(self.texture_converted)
            prepare_texture_preview = TexturePreview(texture_png=texture_for_preview.png_texture)
            self.texture_preview = prepare_texture_preview.texture_for_preview
            self.spinbox_clut.configure(to=(self.number_of_cluts) - 1, state='normal', cursor='xterm')
            self.current_clut_int = 0
            self.total_cluts_label.configure(state='normal', text=f'Current CLUT: {self.current_clut_int + 1} / {self.number_of_cluts}')
            self.label_preview.image = ImageTk.PhotoImage(data=self.texture_preview.get(f'IMAGE_{self.current_clut_int}'), format='png')
            self.label_preview.focus_set()
            self.preview_canvas.create_image(((self.current_canvas_width // 2), (self.current_canvas_height // 2)), image=self.label_preview.image, anchor=CENTER)
            self.convert_current_texture.configure(state='normal')
            self.label_preview.bind('<MouseWheel>', self.mousewheel_spinbox)
            self.spinbox_clut.bind('<MouseWheel>', self.mousewheel_spinbox)
            self.label_preview.bind('<F8>', self.up_arrow_spinbox)
            self.label_preview.bind('<F7>', self.down_arrow_spinbox)
            self.preview_canvas.bind('<MouseWheel>', self.mousewheel_spinbox)
            self.spinbox_clut.bind('<Return>', self.change_spinbox_val)
            self.spinbox_clut.configure(validate='all', validatecommand=(self.register(self.validate_int), "%P"))

    # Spinbox Validation
    def validate_int(self, P):
        if P == '':
            return True
        if len(P) > 2:
            return False
        new_int = int(P)
        if not P.isdigit():
            return False
        elif new_int > self.number_of_cluts:
            return False
        elif new_int < 0:
            return False
        return True
    
    # Spinbox Callback
    def change_spinbox_val(self):
        old_var = self.current_val_spinbox.get()
        new_var = int(old_var)
        if (new_var > (self.number_of_cluts - 1)):
            new_var = f'{0}'
        elif (new_var < 0):
            new_var = f'{self.number_of_cluts - 1}'
        self.current_val_spinbox.set(f'{new_var}')
        self.current_clut_str = self.current_val_spinbox.get()
        if (self.current_clut_str == ""):
            self.current_clut_str = '0'
            self.current_val_spinbox.set('0')
        self.current_clut_int = int(self.current_clut_str)
        self.total_cluts_label.configure(state='normal', text=f'Current CLUT: {int(self.current_clut_str) + 1} / {self.number_of_cluts}')
        self.label_preview.image = ImageTk.PhotoImage(data=self.texture_preview.get(f'IMAGE_{self.current_clut_int}'), format='png')
        self.preview_canvas.create_image(((self.current_canvas_width // 2), (self.current_canvas_height // 2)), image=self.label_preview.image, anchor=CENTER)
    
    def mousewheel_spinbox(self, mouse_action):
        this_var = int(1*(mouse_action.delta/120))
        old_var = self.current_val_spinbox.get()
        old_var_int = int(old_var)
        new_var = old_var_int + this_var
        if (new_var > (self.number_of_cluts - 1)):
            new_var = f'{0}'
        elif (new_var < 0):
            new_var = f'{self.number_of_cluts - 1}'
        self.current_val_spinbox.set(f'{new_var}')
        self.current_clut_str = self.current_val_spinbox.get()
        if (self.current_clut_str == ""):
            self.current_clut_str = '0'
            self.current_val_spinbox.set('0')
        self.current_clut_int = int(self.current_clut_str)
        self.total_cluts_label.configure(state='normal', text=f'Current CLUT: {int(self.current_clut_str) + 1} / {self.number_of_cluts}')
        self.label_preview.image = ImageTk.PhotoImage(data=self.texture_preview.get(f'IMAGE_{self.current_clut_int}'), format='png')
        self.preview_canvas.create_image(((self.current_canvas_width // 2), (self.current_canvas_height // 2)), image=self.label_preview.image, anchor=CENTER)

    def up_arrow_spinbox(self, keyboard):
        print("Woking Up")
        this_var = int(self.current_val_spinbox.get()) + 1
        if this_var > (self.number_of_cluts - 1):
            this_var = f'{0}'
        self.current_val_spinbox.set(f'{this_var}')
        self.current_clut_str = self.current_val_spinbox.get()
        if self.current_clut_str == "":
            self.current_clut_str = '0'
            self.current_val_spinbox.set('0')
        self.current_clut_int = int(self.current_clut_str)
        self.total_cluts_label.configure(state='normal', text=f'Current CLUT: {int(self.current_clut_str) + 1} / {self.number_of_cluts}')
        self.label_preview.image = ImageTk.PhotoImage(data=self.texture_preview.get(f'IMAGE_{self.current_clut_int}'), format='png')
        self.preview_canvas.create_image(((self.current_canvas_width // 2), (self.current_canvas_height // 2)), image=self.label_preview.image, anchor=CENTER)

    def down_arrow_spinbox(self, keyboard):
        print("Woking Down")
        this_var = int(self.current_val_spinbox.get()) - 1
        if this_var < 0:
            this_var = f'{self.number_of_cluts - 1}'
        self.current_val_spinbox.set(f'{this_var}')
        self.current_clut_str = self.current_val_spinbox.get()
        if self.current_clut_str == "":
            self.current_clut_str = f'{self.number_of_cluts - 1}'
            self.current_val_spinbox.set(f'{self.number_of_cluts - 1}')
        self.current_clut_int = int(self.current_clut_str)
        self.total_cluts_label.configure(state='normal', text=f'Current CLUT: {int(self.current_clut_str) + 1} / {self.number_of_cluts}')
        self.label_preview.image = ImageTk.PhotoImage(data=self.texture_preview.get(f'IMAGE_{self.current_clut_int}'), format='png')
        self.preview_canvas.create_image(((self.current_canvas_width // 2), (self.current_canvas_height // 2)), image=self.label_preview.image, anchor=CENTER)

    # Convert Current Texture
    def current_texture_convert(self):
        if len(self.texture_converted) != 0:
            current_selection = self.tree_list.focus()
            current_item_value = self.tree_list.item(current_selection)
            current_texture_name = current_item_value.get('values')
            if current_texture_name not in self.parent_blacklist:
                self.file_location_label.configure(text=f'{self.current_texture_dump_folder}\\{self.current_file_create}.png')
                try:
                    os.makedirs(self.current_texture_dump_folder, exist_ok=True)
                except OSError:
                    error_folder_tim_00 = f'Can\'t create TIM Export folder, permission denied'
                    error_folder_window = messagebox.showerror(title='System Error...', message=error_folder_tim_00)
                    print(error_folder_tim_00)
                    exit()
                if 'TIM' in self.current_texture_type:
                    total_cluts = len(self.texture_converted)
                    for current_clut in range(0, total_cluts):
                        complete_file_path = f'{self.current_texture_dump_folder}\\{self.current_file_create}_{current_clut}.png'
                        img = Image.open(io.BytesIO(self.texture_preview.get(f'IMAGE_{current_clut}')))
                        img.save(complete_file_path)
                elif 'MCQ' in self.current_texture_type:
                    complete_file_path = f'{self.current_texture_dump_folder}\\{self.current_file_create}.png'
                    img = Image.open(io.BytesIO(self.texture_preview.get(f'IMAGE_0')))
                    img.save(complete_file_path)
        else:
            messagebox.showerror(title='Critical!!', message='No Texture file selected to convert')
            raise ValueError(f'Critical Error!: No Texture file selected to convert')
    
    # Checkboxes Controls and Callbacks
    def check_all_convert(self, mouse_interaction):
        if self.check_convertall_var.get() == 0:
            self.convert_all_textures.configure(state='normal')
            self.enable_convert_parent_button.configure(state='disabled')
            self.convert_battlestages_checkbox.configure(state='disabled')
            self.convert_bosses_checkbox.configure(state='disabled')
            self.convert_characters_checkbox.configure(state='disabled')
            self.convert_cutscenes_checkbox.configure(state='disabled')
            self.convert_enemies_checkbox.configure(state='disabled')
            self.convert_menumisc_checkbox.configure(state='disabled')
            self.convert_skyboxes_checkbox.configure(state='disabled')
            self.convert_theend_checkbox.configure(state='disabled')
            self.convert_tutorial_checkbox.configure(state='disabled')
            self.convert_worldmapfield_checkbox.configure(state='disabled')
            self.convert_worldmapthumb_checkbox.configure(state='disabled')
            self.check_battlestages_checkbox.set(0)
            self.check_bosses_checkbox.set(0)
            self.check_characters_checkbox.set(0)
            self.check_cutscenes_checkbox.set(0)
            self.check_enemies_checkbox.set(0)
            self.check_menumisc_checkbox.set(0)
            self.check_skyboxes_checkbox.set(0)
            self.check_theend_checkbox.set(0)
            self.check_tutorial_checkbox.set(0)
            self.check_worldmapfield_checkbox.set(0)
            self.check_worldmapthumb_checkbox.set(0)
        else:
            self.enable_convert_parent_button.configure(state='normal')

    def set_convert_parent(self):
        self.convert_all_textures.configure(state='normal')
        self.enable_convert_parent_button.configure(state='disabled')
        self.convert_battlestages_checkbox.configure(state='normal')
        self.convert_bosses_checkbox.configure(state='normal')
        self.convert_characters_checkbox.configure(state='normal')
        self.convert_cutscenes_checkbox.configure(state='normal')
        self.convert_enemies_checkbox.configure(state='normal')
        self.convert_menumisc_checkbox.configure(state='normal')
        self.convert_skyboxes_checkbox.configure(state='normal')
        self.convert_theend_checkbox.configure(state='normal')
        self.convert_tutorial_checkbox.configure(state='normal')
        self.convert_worldmapfield_checkbox.configure(state='normal')
        self.convert_worldmapthumb_checkbox.configure(state='normal')
    
    # Convert Textures Batch
    def convert_textures_button(self):
        # Create new Widget for Conversion Button
        self.conversion_window_box = Toplevel(master=self)
        self.conversion_window_box.grab_set()
        self.conversion_window_box.focus_set()
        x_main = self.x_y_values[0]
        y_main = self.x_y_values[1]
        self.conversion_window_box.title(string=f'Converting Texture Files')
        self.conversion_window_box.geometry(f'+%d+%d' %(x_main , y_main))
        self.conversion_window_box.geometry(f'{x_main + (500 - x_main)}x{(y_main + (300 - y_main)) // 2}')
        self.conversion_window_box.wm_protocol(name="WM_DELETE_WINDOW", func=self.no_close)
        self.conversion_window_box.overrideredirect(True)
        self.conversion_window_box.configure(bd=4, relief='ridge')

        self.container_label_conversion = LabelFrame(master=self.conversion_window_box, text='Conversion in Progress')
        self.label_converting_files = Label(master=self.container_label_conversion, text='Creating Subfolders', anchor='center')

        self.container_label_conversion.place(relx=0.01, rely=0.01, relwidth=0.99, relheight=0.99)
        self.label_converting_files.place(relx=0, rely=0, relwidth=0.99, relheight=0.99)

        self.convert_textures_start()

    def convert_textures_start(self):
        if self.check_convertall_var.get() == 1:
            self.check_battlestages_checkbox.set(1)
            self.check_bosses_checkbox.set(1)
            self.check_characters_checkbox.set(1)
            self.check_cutscenes_checkbox.set(1)
            self.check_enemies_checkbox.set(1)
            self.check_menumisc_checkbox.set(1)
            self.check_skyboxes_checkbox.set(1)
            self.check_theend_checkbox.set(1)
            self.check_tutorial_checkbox.set(1)
            self.check_worldmapfield_checkbox.set(1)
            self.check_worldmapthumb_checkbox.set(1)
            # Start Conversion of all elements
            self.convert_batch_textures()
        else:
            self.convert_batch_textures()

    def no_close(self): # THIS FUNCTION is to bypass the [X] Windows icon for closing the window
        pass
    
    def convert_batch_textures(self):
        get_battlestages = self.check_battlestages_checkbox.get()
        get_bosses = self.check_bosses_checkbox.get()
        get_characters = self.check_characters_checkbox.get()
        get_cutscenes = self.check_cutscenes_checkbox.get()
        get_enemies = self.check_enemies_checkbox.get()
        get_menu_misc = self.check_menumisc_checkbox.get()
        get_skyboxes = self.check_skyboxes_checkbox.get()
        get_the_end = self.check_theend_checkbox.get()
        get_tutorial = self.check_tutorial_checkbox.get()
        get_world_map_field = self.check_worldmapfield_checkbox.get()
        get_world_map_thumb = self.check_worldmapthumb_checkbox.get()
        selection_list = []
        if get_battlestages == 1:
            selection_list.append("Battle_Stages")
        if get_bosses == 1:
            selection_list.append("Bosses")
        if get_characters == 1:
            selection_list.append("Characters")
        if get_cutscenes == 1:
            for this_cutscenes in self.create_dict_files:
                if 'CutScene' in this_cutscenes:
                    selection_list.append(this_cutscenes)
        if get_enemies == 1:
            selection_list.append("Enemies")
        if get_menu_misc == 1:
            selection_list.append("Menu_Misc")
        if get_skyboxes == 1:
            selection_list.append("Skyboxes")
        if get_the_end == 1:
            selection_list.append("THE_END")
        if get_tutorial == 1:
            selection_list.append("Tutorial")
        if get_world_map_field == 1:
            selection_list.append("World_Map_Field")
        if get_world_map_thumb == 1:
            selection_list.append("World_Map_Thumbnails")
        if len(selection_list) == 0:
            messagebox.showwarning(title='WARNING!!', message=f'You must select at least one of the listed\nTexture groups')

        files_to_convert = []
        for selection in selection_list: # First Generate the list of files and folders to place the files
            get_this_parent = self.create_dict_files.get(f'{selection}')
            for this_files in get_this_parent:
                this_files_data = get_this_parent.get(f'{this_files}')
                in_disk_type = this_files_data.get('inDiskType')
                
                if in_disk_type == 'Single-File':
                    get_file_type = this_files_data.get('formatType')
                    get_file_path = this_files_data.get(f'filePath')
                    get_fantasy_name = this_files_data.get(f'fantasyName')
                    get_flag = this_files_data.get(f'flag')
                    fantasy_name_change_underscore = get_fantasy_name.replace(' ', '_')
                    final_path_origin_file = f'{sc_folder_def}\\{get_file_path[0]}'
                    final_path_to_dump = f'{dump_folder}\\{selection}\\{fantasy_name_change_underscore}'
                    this_conversion = {'filePath': final_path_origin_file, 'filePathDump': final_path_to_dump, 'formatType': get_file_type, 'flag': get_flag}
                    files_to_convert.append(this_conversion)

                elif in_disk_type == 'FOLDER':
                    get_nested_files = this_files_data.get('filePath')
                    get_file_type = this_files_data.get('formatType')
                    get_file_path = this_files_data.get(f'filePath')
                    get_fantasy_name = this_files_data.get(f'fantasyName')
                    get_flag = this_files_data.get(f'flag')
                    number_add_nested = 0
                    for this_texture_path in get_nested_files:
                        final_path_origin_file = f'{sc_folder_def}\\{this_texture_path}'
                        fantasy_name_change_underscore = get_fantasy_name.replace(' ', '_')
                        final_path_to_dump = f'{dump_folder}\\{fantasy_name_change_underscore}\\{number_add_nested}'
                        this_conversion = {'filePath': final_path_origin_file, 'filePathDump': final_path_to_dump, 'formatType': get_file_type, 'flag': get_flag}
                        files_to_convert.append(this_conversion)
                        number_add_nested += 1

        get_total_files = len(files_to_convert)
        current_file_converted = 0
        for current_file_convert in files_to_convert:
            self.conversion_window_box.update()
            file_origin= current_file_convert.get('filePath')
            file_path_export = current_file_convert.get('filePathDump')
            file_format_type = current_file_convert.get('formatType')
            file_flag = current_file_convert.get('flag')
            
            try:
                os.makedirs(file_path_export, exist_ok=True)
            except OSError:
                error_folder_tim_00 = f'Can\'t create TIM Export folder, permission denied'
                error_folder_window = messagebox.showerror(title='System Error...', message=error_folder_tim_00)
                print(error_folder_tim_00)
                exit()

            texture_object = PngTexture(texture_path=file_origin, texture_type=file_format_type, flag=file_flag)
            texture_converted_rgba = texture_object.png_texture.get(f'RGBA_Data')
            #texture_converted_size = texture_object.png_texture.get(f'SizeImg')
            number_of_cluts = len(texture_converted_rgba)
            prepare_texture_convert = TexturePreview(texture_png=texture_object.png_texture)
            texture_converted = prepare_texture_convert.texture_for_preview
            subname_file_find = file_path_export.rfind('\\')
            subname_file = file_path_export[subname_file_find + 1:]
            for clut in range(0, number_of_cluts):
                complete_path = f'{file_path_export}\\{subname_file}_TIM_{clut}.png'
                img = Image.open(io.BytesIO(texture_converted.get(f'IMAGE_{clut}')))
                img.save(complete_path)
            self.label_converting_files.configure(text=f'Conversion in progress...\nCurrent File {current_file_converted + 1} of {get_total_files}')
            current_file_converted += 1
        
        self.label_converting_files.configure(text=f'Conversion in progress...\nCurrent File {current_file_converted} of {get_total_files}')
        if current_file_converted == get_total_files:
            self.conversion_window_box.after(1000, func=lambda: self.destroy_window_conversion())

    def destroy_window_conversion(self):
        self.conversion_window_box.destroy()
        self.after_conversion_info = messagebox.showinfo(title='Conversion FINISHED', message=f'Conversion finished successfully')
        self.new_window_box.grab_set()
        self.new_window_box.focus_set()

    def create_folder_batch(self, this_folder):
        try:
            os.makedirs(this_folder, exist_ok=True)
        except OSError:
            error_folder_batch = f'Can\'t create Batch Export folder, permission denied'
            error_folder_window = messagebox.showerror(title='System Error...', message=error_folder_batch)
            print(error_folder_batch)
            exit()
    
    def check_inside_folder(self, files_path=str) -> list:
        all_files = []
        full_list = os.walk(files_path)
        for root, dirs, files in full_list:
            get_mrg_index = files.index(f'mrg')
            del files[get_mrg_index]
            numbers = [int(f) for f in files]
            numbers.sort()
            files = [str(n) for n in numbers]
            for afile in files:
                full_path_nested = root + f'/' + afile
                this_file_size = os.path.getsize(full_path_nested)
                if (this_file_size != 0):
                    single_file_path = f'{root}/{afile}'
                    all_files.append(single_file_path)
        return all_files
    
    #### Advanced Conversion ####

    def advanced_conversion(self):
        # Create new Widget Window for Advanced Conversion
        self.advanced_window_box = Toplevel(master=self)
        self.advanced_window_box.grab_set()
        self.advanced_window_box.focus_set()
        x_main = self.x_y_values[0]
        y_main = self.x_y_values[1]
        self.advanced_window_box.title(string=f'Advanced Conversion')
        self.advanced_window_box.geometry(f'+%d+%d' %(x_main - 100, y_main - 50))
        self.advanced_window_box.geometry(f'{x_main + (800 - x_main)}x{(y_main + (400 - y_main)) // 2}')

        self.load_texture_button = Button(master=self.advanced_window_box, text='Load Texture File[PXL]', command=self.open_file_select)
        self.load_texture_button.place(relx=0.35, rely=0.35, relwidth=0.3, relheight=0.3)
        ToolTip(self.load_texture_button, msg=f'Load a single Texture File\nSupported Formats: TIM, MCQ, PXL [MiniModels Textures]\nAt the moment, PXL only supported')
    
    def open_file_select(self):
        texture_file_path = askopenfile()
        if texture_file_path != None:
            converted_files, texture_type = convert_advanced.ConvertTextureFile.check_file_type(self=convert_advanced.ConvertTextureFile, file_to_decode=texture_file_path.name)
            texture_export = asksaveasfilename()
            clut_lenght = len(converted_files)
            if converted_files != None:
                if texture_type == 'PXL':
                    find_name_index = texture_file_path.name.rfind("/")
                    name_file = texture_file_path.name[find_name_index + 1:]
                    for clut in range(0, clut_lenght):
                        complete_path = texture_export + f'{name_file}_PXL_{clut}.png'
                        img = Image.open(io.BytesIO(converted_files[clut]))
                        img.save(complete_path)
                elif texture_type == 'MCQ':
                    messagebox.showinfo(title='Info', message='Not supported at the moment...')
                elif texture_type == 'TIM':
                    messagebox.showinfo(title='Info', message='Not supported at the moment...')
            else:
                messagebox.showerror(title='Critical!!!', message='File Processing Stop')
        else:
            messagebox.showinfo(title='Info', message='No file loaded...')

    # Configuration Window
    def configure_tool(self):
        self.size_x = size_x
        self.size_y = size_y
        self.sc_folder_def = sc_folder_def
        self.dump_folder = dump_folder
        self.configure_window = Toplevel(master=self)
        self.configure_window.grab_set()
        self.configure_window.focus_set()
        x_main = self.x_y_values[0] // 2
        y_main = self.x_y_values[1] // 2
        self.configure_window.title(string=f'Tool Configuration')
        self.configure_window.geometry(f'+%d+%d' %(x_main, y_main))
        self.configure_window.geometry(f'{x_main + (x_main - 100)}x{y_main + (y_main - 75)}')

        # RESOLUTION FRAME
        self.resolution_frame = LabelFrame(master=self.configure_window, text=f'Tool Window size')
        self.resolution_list = [f'{self.size_x}x{self.size_y}',f'7680x4320', f'3840x2160', f'2560x1440', f'1920x1080', f'1280x720', f'854x480', f'640x360', f'426x240']
        self.combobox_resolution = ttk.Combobox(master=self.resolution_frame, values=self.resolution_list)
        self.combobox_resolution.current(0)
        self.combobox_resolution.bind('<<ComboboxSelected>>', lambda e: self.combo_box_selected_callback())
        self.ckb_variable_resolution = IntVar()
        self.check_box_custom_res = Checkbutton(master=self.resolution_frame, text=f'Use custom size', variable=self.ckb_variable_resolution)
        self.label_w_entry = Label(master=self.resolution_frame, text='WIDTH')
        self.label_h_entry = Label(master=self.resolution_frame, text='HEIGHT')
        self.width_res_change = Entry(master=self.resolution_frame, justify='center', validate='key', )
        self.height_res_change = Entry(master=self.resolution_frame, justify='center')
        self.set_resolution_button = Button(master=self.resolution_frame, text='SET')
        self.width_res_change.insert(0, size_x)
        self.height_res_change.insert(0, size_y)
        self.width_res_change.configure(state='disabled')
        self.height_res_change.configure(state='disabled')
        self.set_resolution_button.configure(state='disabled')
        self.check_box_custom_res.configure(command=lambda: self.checkbox_change_resolution())
        self.set_resolution_button.configure(command=lambda: self.get_xy_values_entries())
        self.validate_cmd = self.register(self.validate_digit)
        self.width_res_change.configure(validatecommand=(self.validate_cmd, '%P'))
        self.height_res_change.configure(validatecommand=(self.validate_cmd, '%P'))

        # SC FRAME
        self.sc_frame = LabelFrame(master=self.configure_window, text='SC Default Folder')
        self.sc_folder_path_text = Text(master=self.sc_frame, background='#edece3', font='Arial 12')
        self.sc_folder_path_text.insert(END, f'{sc_folder_def}')
        self.sc_folder_path_text.tag_configure("new_configure", justify='center')
        self.sc_folder_path_text.tag_add("new_configure", "1.0", END)
        self.sc_change_folder_path = Button(master=self.sc_frame, cursor='hand2', text=f'Change SC Folder', command=lambda: self.change_sc_folder())

        # DUMP FRAME
        self.dump_frame = LabelFrame(master=self.configure_window, text='Dump Folder')
        self.dump_folder_path_text = Text(master=self.dump_frame, background='#edece3', font='Arial 12')
        self.dump_folder_path_text.insert(END, f'{dump_folder}')
        self.dump_folder_path_text.tag_configure("new_configure", justify='center')
        self.dump_folder_path_text.tag_add("new_configure", "1.0", END)
        self.dump_change_folder_path = Button(master=self.dump_frame, cursor='hand2', text=f'Change DUMP Folder', command=lambda: self.change_dump_folder())

        # SAVE BUTTON
        self.save_configuration_button = Button(master=self.configure_window, cursor='hand2', text=f'SAVE CONFIG', command=lambda: self.save_config(res_x=self.size_x, res_y=self.size_y, sc_path=self.sc_folder_def, dump_path=self.dump_folder))
        # CANCEL BUTTON
        self.cancel_configuration_button = Button(master=self.configure_window, cursor='hand2', text=f'CANCEL', command=lambda: self.cancel_config())

        # PLACING STUFF
        # Resolution Frame
        self.resolution_frame.place(relx=0.05, rely=0.02, relwidth= 0.9, relheight= 0.25)
        self.combobox_resolution.place(relx=0.01, rely=0.4, relwidth= 0.3, relheight= 0.50)
        self.check_box_custom_res.place(relx=0.31, rely=0.4, relwidth= 0.2, relheight= 0.50)
        self.width_res_change.place(relx=0.51, rely=0.4, relwidth= 0.15, relheight= 0.50)
        self.height_res_change.place(relx=0.70, rely=0.4, relwidth= 0.15, relheight= 0.50)
        self.label_w_entry.place(relx=0.51, rely=0.05, relwidth= 0.15, relheight= 0.30)
        self.label_h_entry.place(relx=0.70, rely=0.05, relwidth= 0.15, relheight= 0.20)
        self.set_resolution_button.place(relx=0.87, rely=0.4, relwidth= 0.10, relheight= 0.50)
        # SC Frame
        self.sc_frame.place(relx=0.05, rely=0.27, relwidth= 0.9, relheight= 0.25)
        self.sc_folder_path_text.place(relx=0.05, rely=0.10, relwidth= 0.9, relheight= 0.35)
        self.sc_change_folder_path.place(relx=0.30, rely=0.50, relwidth= 0.4, relheight= 0.45)
        # Dump Frame
        self.dump_frame.place(relx=0.05, rely=0.52, relwidth= 0.9, relheight= 0.25)
        self.dump_folder_path_text.place(relx=0.05, rely=0.10, relwidth= 0.9, relheight= 0.35)
        self.dump_change_folder_path.place(relx=0.30, rely=0.50, relwidth= 0.4, relheight= 0.45)
        # Save Config
        self.save_configuration_button.place(relx=0.2, rely=0.78, relwidth= 0.3, relheight= 0.18)
        # Cancel Config
        self.cancel_configuration_button.place(relx=0.5, rely=0.78, relwidth= 0.3, relheight= 0.18)
    
    def checkbox_change_resolution(self):
        check_state_resolution = self.ckb_variable_resolution.get()
        if check_state_resolution == 1:
            self.combobox_resolution.configure(state='disabled')
            self.width_res_change.configure(state='normal')
            self.height_res_change.configure(state='normal')
            self.set_resolution_button.configure(state='active')
        else:
            self.combobox_resolution.configure(state='normal')
            self.width_res_change.configure(state='disabled')
            self.height_res_change.configure(state='disabled')
            self.set_resolution_button.configure(state='disabled')

    def combo_box_selected_callback(self):
        selected_res = self.combobox_resolution.get()
        find_x = selected_res.find("x")
        self.size_x = selected_res[0:find_x]
        self.size_y = selected_res[find_x + 1:]

    def get_xy_values_entries(self):
        value_x = self.width_res_change.get()
        value_y = self.height_res_change.get()

        value_x_int = int(value_x)
        value_y_int = int(value_y)

        if value_x_int < 100 or value_y_int < 100:
            messagebox.showwarning(title=f'INCORRECT VALUE', message=f'{value_x}, {value_y} is not a possible resolution\nPlease select values above 100')
        else:
            self.size_x = value_x_int
            self.size_y = value_y_int
            messagebox.showinfo(title='Values set', message=f'{self.size_x} and {self.size_y} are set as new resolution values')

    def validate_digit(self, text_entered):
        if (str.isdigit(text_entered)) or (text_entered == f''):
            return True
        else:
            return False

    def change_sc_folder(self):
        new_folder_sc = askdirectory(title='Select new SC Folder')
        if new_folder_sc == f'':
            messagebox.showinfo(title=f'Incorrect SC FOLDER', message='Please Try Again...')
            self.change_sc_folder()
        
        self.sc_folder_path_text.delete("1.0", END)
        self.sc_folder_path_text.insert(END, new_folder_sc)
        self.sc_folder_path_text.tag_configure("new_configure", justify='center')
        self.sc_folder_path_text.tag_add("new_configure", "1.0", END)
        self.sc_folder_def = new_folder_sc

    def change_dump_folder(self):
        new_folder_dump = askdirectory(title='Select new SC Folder')
        if new_folder_dump == f'':
            messagebox.showinfo(title=f'Incorrect DUMP FOLDER', message='Please Try Again...')
            self.change_dump_folder()
        
        self.dump_folder_path_text.delete("1.0", END)
        self.dump_folder_path_text.insert(END, new_folder_dump)
        self.dump_folder_path_text.tag_configure("new_configure", justify='center')
        self.dump_folder_path_text.tag_add("new_configure", "1.0", END)
        self.dump_folder = new_folder_dump

    def save_config(self, res_x=int, res_y=int, sc_path=str, dump_path=str):
        path_file = f'Resources/converter_config.config'
        Options.write_options(Options, path_cnf_file=path_file, first_run=False, size_x=res_x, size_y=res_y, sc_folder_def=sc_path, dump_folder=dump_path)
        messagebox.showinfo(master=self.configure_window, title='CONFIG SAVED', message='Your configuration has been saved...')
        self.configure_window.destroy()

    def cancel_config(self):
        messagebox.showinfo(master=self.configure_window, title='IMPORTANT', message='Your configuration won\'t be saved')
        self.configure_window.destroy()


if __name__ == "__main__":
    main_window = Tk()
    config_window = Options.read_write_options(Options)
    main_window.iconbitmap(default='Resources/Lavitz_Painting.ico')
    main_window.wm_title("TLoD Texture Converter BETA v0.1")
    width_native_windows = main_window.winfo_screenwidth()
    height_native_windows = main_window.winfo_screenheight()
    middle_place_width = (width_native_windows // 2) - (width_native_windows // 3)
    middle_place_height = (height_native_windows // 2) - (height_native_windows // 3)
    main_window.geometry(f'+{middle_place_width}+{middle_place_height}')

    tlod_texture_converter_gui = MainWindow(main_window, width=config_window[0], height=config_window[1])
    tlod_texture_converter_gui.mainloop()