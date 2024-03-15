import customtkinter as ctk
from .utils_wrapper import update_config_field
import threading

class ExcludedKeywordsFrame(ctk.CTkFrame):
    def __init__(self, master, font, values):
        super().__init__(master)
        self.values = values
        self.update_timer = None
        self.update_delay = 1.5
        title = 'Excluded Keywords'
        title_label = ctk.CTkLabel(self, text=title, font=(font, 18))
        title_label.pack(pady=(10, 20))

        # Create a frame to display the TextArea for the excluded keywords and a description
        filter_description_frame = ctk.CTkFrame(self, fg_color='transparent')

        self.filter_frame = ctk.CTkFrame(filter_description_frame)
        self.filter_title = ctk.CTkLabel(self.filter_frame, text='Filter List', font=font)
        self.filter_title.pack()
        self.keywords_text_box = ctk.CTkTextbox(self.filter_frame, font=font)
        self.keywords_text_box.insert(index='1.0', text="\n".join(values))
        self.keywords_text_box.pack(padx=10, pady=(0, 10))
        self.filter_frame.pack(side='left', padx=10, pady=(0, 10))

        description = 'New scrape results will exclude any job titles that contain any of the excluded keywords.\n\nPreviously scraped data will not be deleted if a record contains keywords in the filter list.'
        self.description_label = ctk.CTkLabel(filter_description_frame, 
                                              fg_color='transparent', 
                                              text=description, 
                                              font=font, 
                                              justify="left", 
                                              wraplength=400)
        self.description_label.pack(side='left', padx=10, pady=(0, 10))

        filter_description_frame.pack(anchor='center')

        # Bind the event to the keywords text box
        self.keywords_text_box.bind('<KeyRelease>', self.schedule_update)
    
    def schedule_update(self, event):
        # The config file will be updated after 1.5s when modifying the list of excluded keywords
        if self.update_timer:
            self.update_timer.cancel()
        self.update_timer = threading.Timer(self.update_delay, self.update_config)
        self.update_timer.start()

    def update_config(self):
        updated_keywords = self.keywords_text_box.get('1.0', 'end-1c').split('\n')
        update_config_field('config.json', 'excluded_keywords', updated_keywords)