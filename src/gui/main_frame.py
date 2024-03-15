import os
import json
import customtkinter as ctk
from indeed_settings_frame import IndeedSettingsFrame
from excluded_keywords_frame import ExcludedKeywordsFrame
from csv_settings_frame import CsvSettingsFrame

class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()

        with open('config.json') as config_file:
            config = json.load(config_file)

        self.title('Job Listing Scraper')
        self.geometry('800x700')
        self.resizable=False

        ctk.set_appearance_mode('System')
        ctk.set_default_color_theme('dark-blue')
    
        default_font = ctk.CTkFont(family='Roboto', size=12)

        self.indeed_settings_frame = IndeedSettingsFrame(self, default_font, config['indeed_criteria'])
        self.indeed_settings_frame.pack(fill='x', 
                                        padx=10, 
                                        pady=(10, 0))

        self.excluded_keywords_frame = ExcludedKeywordsFrame(self, default_font, config['excluded_keywords'])
        self.excluded_keywords_frame.pack(fill='x', 
                                        padx=10, 
                                        pady=(10, 0))
        
        self.csv_settings_frame = CsvSettingsFrame(self, default_font, config['csv_settings'])
        self.csv_settings_frame.pack(fill='x', 
                                        padx=10, 
                                        pady=(10, 0))
        
        footer_frame = ctk.CTkFrame(self, bg_color='transparent', fg_color='transparent')
        footer_frame.pack(anchor='e')

        quit_button = ctk.CTkButton(footer_frame, text='Quit', fg_color='#ff4d4d', command=self.destroy)
        quit_button.pack(side='left', padx=10, pady=(20, 10))

        start_button = ctk.CTkButton(footer_frame, text='Start', text_color="#008000", fg_color='#4dff4d')
        start_button.pack(side='left', padx=(10, 40), pady=(20, 10))


# Clear console
os.system('cls' if os.name == 'nt' else 'clear')

app = MainFrame()
app.mainloop()