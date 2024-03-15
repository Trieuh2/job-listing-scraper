import threading
import customtkinter as ctk

from .utils_wrapper import update_config_field


class ExcludedKeywordsFrame(ctk.CTkFrame):
    def __init__(self, master, font, values):
        super().__init__(master)
        self.values = values
        self.update_timer = None
        self.update_delay = 0.25

        self.create_title_label(font)
        self.create_keywords_text_box(font)
        self.create_filter_description_frame(font)
        self.bind_events()

    def create_title_label(self, font):
        # Create the title label for the frame
        title_label = ctk.CTkLabel(self, text='Excluded Keywords', font=(font, 18))
        title_label.pack(pady=(10, 20))

    def create_keywords_text_box(self, font):
        # Create the text box for entering excluded keywords
        self.create_filter_frame(font)
        self.keywords_text_box = ctk.CTkTextbox(self.filter_frame, font=font)
        self.keywords_text_box.insert(index='1.0', text="\n".join(self.values))
        self.keywords_text_box.pack(padx=10, pady=(0, 10))

    def create_filter_frame(self, font):
        # Create the frame for the filter list
        self.filter_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.filter_frame.pack(side='left', padx=10, pady=(0, 10))
        filter_title = ctk.CTkLabel(self.filter_frame, text='Filter List', font=font)
        filter_title.pack()

    def create_filter_description_frame(self, font):
        # Create the frame for the filter description
        filter_description_frame = ctk.CTkFrame(self, fg_color='transparent')
        filter_description_frame.pack(anchor='center')
        self.create_description_label(font, filter_description_frame)

    def create_description_label(self, font, parent_frame):
        # Create the description label
        description = ('New scrape results will exclude any job titles that contain any of the excluded keywords.\n\n'
                       'Previously scraped data will not be deleted if a record contains keywords in the filter list.')
        description_label = ctk.CTkLabel(parent_frame, fg_color='transparent', text=description, font=font,
                                         justify="left", wraplength=400)
        description_label.pack(side='left', padx=10, pady=(0, 10))

    def bind_events(self):
        # Bind releasing a keypress to scheduling an update to config.json file
        self.keywords_text_box.bind('<KeyRelease>', self.schedule_update)

    def schedule_update(self, event):
        # Schedule an update of the configuration file after a delay
        if self.update_timer:
            self.update_timer.cancel()
        self.update_timer = threading.Timer(self.update_delay, self.update_config)
        self.update_timer.start()

    def update_config(self):
        # Update the configuration file with the new excluded keywords
        updated_keywords = self.keywords_text_box.get('1.0', 'end-1c').split('\n')
        update_config_field('config.json', 'excluded_keywords', updated_keywords)
