import os
import json
import customtkinter as ctk
from indeed_settings_frame import IndeedSettingsFrame
from excluded_keywords_frame import ExcludedKeywordsFrame 

class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()

        with open('config.json') as config_file:
            config = json.load(config_file)

        self.title='Job Listing Scraper'
        self.geometry('800x600')

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

# Clear console
os.system('cls' if os.name == 'nt' else 'clear')

app = MainFrame()
app.mainloop()