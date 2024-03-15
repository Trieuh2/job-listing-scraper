import os
import json
import customtkinter as ctk
from .indeed_settings_frame import IndeedSettingsFrame
from .excluded_keywords_frame import ExcludedKeywordsFrame
from .csv_settings_frame import CsvSettingsFrame
from scraper import Scraper
import utils
from .utils_wrapper import update_config_field
import threading

DEFAULT_NUM_PAGES_SCRAPE = 5

class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.frames = []
        self.scraping_thread = None
        self.stop_scraping = False
        self.default_font = ctk.CTkFont(family='Roboto', size=12)

        with open('config.json') as config_file:
            self.config = json.load(config_file)

        self.title('Job Listing Scraper')
        self.geometry('800x750')
        self.resizable=False

        ctk.set_appearance_mode('System')
        ctk.set_default_color_theme('dark-blue')

        self.init_frames()
        self.create_footer()  

    def init_frames(self):
        self.init_indeed_settings_frame()
        self.init_excluded_keywords_frame()
        self.init_csv_settings_frame()

    def init_indeed_settings_frame(self):
        self.indeed_settings_frame = IndeedSettingsFrame(
            self, self.default_font, self.config['indeed_criteria'])
        self.indeed_settings_frame.pack(fill='x', padx=10, pady=(10, 0))
        self.frames.append(self.indeed_settings_frame)

    def init_excluded_keywords_frame(self):
        self.excluded_keywords_frame = ExcludedKeywordsFrame(
            self, self.default_font, self.config['excluded_keywords'])
        self.excluded_keywords_frame.pack(fill='x', padx=10, pady=(10, 0))
        self.frames.append(self.excluded_keywords_frame)

    def init_csv_settings_frame(self):
        self.csv_settings_frame = CsvSettingsFrame(
            self, self.default_font, self.config['csv_settings'])
        self.csv_settings_frame.pack(fill='x', padx=10, pady=(10, 0))
        self.frames.append(self.csv_settings_frame)

    def create_footer(self):
        footer_frame = ctk.CTkFrame(self, bg_color='transparent', fg_color='transparent')
        footer_frame.pack(fill='x')

        self.create_scrape_settings_frame(footer_frame)
        self.create_button_frame(footer_frame)

    def create_scrape_settings_frame(self, parent):
        scrape_settings_frame = ctk.CTkFrame(
            parent, bg_color='transparent', fg_color='transparent')
        scrape_settings_frame.pack(side='left', fill='x')

        self.scrape_all_checkbox = ctk.CTkCheckBox(
            scrape_settings_frame, text="Scrape all pages?", command=self.toggle_scrape_all_checkbox)
        self.scrape_all_checkbox.pack(side='left', padx=(20, 10), pady=(20, 10))

        self.create_num_pages_scrape_frame(scrape_settings_frame)
        self.initialize_scrape_settings()

    def create_num_pages_scrape_frame(self, parent):
        num_pages_scrape_frame = ctk.CTkFrame(
            parent, bg_color='transparent', fg_color='transparent')
        num_pages_scrape_frame.pack(side='left', padx=10, pady=(5, 10))

        num_pages_to_scrape_label = ctk.CTkLabel(
            num_pages_scrape_frame, text='Number of pages to scrape', font=self.default_font)
        num_pages_to_scrape_label.pack(anchor='w')

        self.num_pages_to_scrape_entry_field = ctk.CTkEntry(
            num_pages_scrape_frame, placeholder_text=str(DEFAULT_NUM_PAGES_SCRAPE), font=self.default_font)
        self.num_pages_to_scrape_entry_field.bind(
            '<KeyRelease>', command=self.update_config_num_pages_scrape)
        self.num_pages_to_scrape_entry_field.pack(anchor='w')

    def initialize_scrape_settings(self):
        if self.config['num_pages_to_scrape'] == 0:
            self.scrape_all_checkbox.select()
            self.num_pages_to_scrape_entry_field.configure(state=ctk.DISABLED, fg_color='#A0A0A0')
        else:
            self.num_pages_to_scrape_entry_field.insert(
                index=1, string=str(self.config['num_pages_to_scrape']))
            self.num_pages_to_scrape_entry_field.configure(state=ctk.NORMAL, fg_color='#343638')

    def create_button_frame(self, parent):
        button_frame = ctk.CTkFrame(
            parent, bg_color='transparent', fg_color='transparent')
        button_frame.pack(side='right', anchor='s')

        quit_button = ctk.CTkButton(
            button_frame, text='Quit', text_color='white', fg_color='#ff4d4d', hover_color='#ff8080', command=self.destroy)
        quit_button.pack(side='left', padx=(10, 5), pady=(20, 10))

        self.start_stop_button = ctk.CTkButton(
            button_frame, text='Start', text_color="#008000", fg_color='#4dff4d', hover_color='#3cb043', command=self.toggle_start_stop)
        self.start_stop_button.pack(side='left', padx=(5, 20), pady=(20, 10))

    def disable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                self.disable_frame(child)
            elif isinstance(child, ctk.CTkCheckBox):
                child.configure(state=ctk.DISABLED)
            elif isinstance(child, ctk.CTkEntry):
                child.configure(state=ctk.DISABLED, fg_color='#A0A0A0')
            elif isinstance(child, ctk.CTkOptionMenu):
                child.configure(state=ctk.DISABLED)
            elif isinstance(child, ctk.CTkTextbox):
                child.configure(state=ctk.DISABLED)
            elif isinstance(child, ctk.CTkButton):
                child.configure(state=ctk.DISABLED)
    
    def enable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                self.enable_frame(child)
            elif isinstance(child, ctk.CTkCheckBox):
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkEntry):
                child.configure(state=ctk.NORMAL, fg_color='#343638')
            elif isinstance(child, ctk.CTkOptionMenu):
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkTextbox):
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkButton):
                child.configure(state=ctk.NORMAL)

    def toggle_start_stop(self):
        if self.start_stop_button.cget('text') == 'Start':
            # Disable all widgets before starting to scrape
            for frame in self.frames:
                self.disable_frame(frame)
            self.start_stop_button.configure(text='Stop', text_color='white', fg_color='#ff4d4d', hover_color='#ff8080')

            # Begin scraping
            self.stop_scraping = False  # Reset the flag
            self.scraping_thread = threading.Thread(target=self.run_scraper)
            self.scraping_thread.start()

        elif self.start_stop_button.cget('text') == 'Stop':
            self.stop_scraping = True  # Reset the flag

            # Re-enable all widgets to allow further configuration if desired
            for frame in self.frames:
                self.enable_frame(frame)

            self.start_stop_button.configure(text='Start', text_color="#008000", fg_color='#4dff4d', hover_color='#3cb043')

    def toggle_scrape_all_checkbox(self):
        if self.scrape_all_checkbox.get() == 0:
            # Configured to scrape a specific num of pages
            self.num_pages_to_scrape_entry_field.configure(state=ctk.NORMAL, fg_color='#343638')
            self.num_pages_to_scrape_entry_field.delete(0, len(self.num_pages_to_scrape_entry_field.get()))
            self.num_pages_to_scrape_entry_field.insert(0, 5)
            update_config_field(filepath='config.json', field_path='num_pages_to_scrape', new_value=5)
        else:
            # Configured to scrape all pages
            self.num_pages_to_scrape_entry_field.delete(0, len(self.num_pages_to_scrape_entry_field.get()))
            self.num_pages_to_scrape_entry_field.configure(state=ctk.DISABLED, fg_color='#A0A0A0')
            update_config_field(filepath='config.json', field_path='num_pages_to_scrape', new_value=0)

    def update_config_num_pages_scrape(self, event):
        new_value = int(self.num_pages_to_scrape_entry_field.get())
        update_config_field(filepath='config.json', field_path='num_pages_to_scrape', new_value=new_value)

    def run_scraper(self):
        # Load configuration variables scraper
        with open('config.json') as config_file:
            config = json.load(config_file)

        indeed_criteria = config['indeed_criteria']
        indeed_url = utils.build_indeed_url(
            max_days_posted_ago = indeed_criteria['max_days_posted_ago'],
            position            = indeed_criteria['position'],
            experience_level    = indeed_criteria['experience_level'],
            job_type            = indeed_criteria['job_type'],
            location            = indeed_criteria['location']
        )

        num_pages_to_scrape = config['num_pages_to_scrape']

        # Set up and run the Scraper
        scraper = Scraper(indeed_url)
        pages_scraped = 0

        while (self.stop_scraping == False) and (num_pages_to_scrape == 0 or pages_scraped < num_pages_to_scrape):
            extracted_hash_ids = scraper.extract_current_page()

            # Stop parsing when the last page has been parsed twice
            if self.stop_scraping or extracted_hash_ids == scraper.previous_page_hash_ids:
                break
            else:
                scraper.previous_page_hash_ids = extracted_hash_ids
                scraper.navigate_next_page()
                pages_scraped += 1

        print(f"Number of pages scraped: {pages_scraped}")
        print(f"Number of new records: {len(scraper.jobs) - scraper.initial_num_records}\n")

        scraper.shutdown()
    
        if config['csv_settings']['update_csv_on_completion']:
            utils.write_jobs_csv(config['csv_settings']['csv_output_path'], scraper.jobs)

        # Re-enable all widgets to allow further configuration
        for frame in self.frames:
            self.enable_frame(frame)