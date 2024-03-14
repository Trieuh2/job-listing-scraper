import os
import json
import customtkinter as ctk
import indeed_settings_frame

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

        # Initialize and place other frames or widgets here
        self.indeed_settings_frame = indeed_settings_frame.IndeedSettingsFrame(self, default_font, config['indeed_url_params'])
        self.indeed_settings_frame.pack(fill='x', 
                                        padx=10, 
                                        pady=(10, 0))

# Clear console
os.system('cls' if os.name == 'nt' else 'clear')

app = MainFrame()
app.mainloop()