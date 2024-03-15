import os
import json
import customtkinter as ctk
from .indeed_settings_frame import IndeedSettingsFrame
from .excluded_keywords_frame import ExcludedKeywordsFrame
from .csv_settings_frame import CsvSettingsFrame
from scraper import Scraper
import utils
import threading

class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.frames = []
        self.scraping_thread = None
        self.stop_scraping = False

        with open('config.json') as config_file:
            config = json.load(config_file)

        self.title('Job Listing Scraper')
        self.geometry('800x700')
        self.resizable=False

        ctk.set_appearance_mode('System')
        ctk.set_default_color_theme('dark-blue')
    
        default_font = ctk.CTkFont(family='Roboto', size=12)

        # Indeed Settings
        self.indeed_settings_frame = IndeedSettingsFrame(self, default_font, config['indeed_criteria'])
        self.indeed_settings_frame.pack(fill='x', 
                                        padx=10, 
                                        pady=(10, 0))
        self.frames.append(self.indeed_settings_frame)

        # Excluded Keywords Settings
        self.excluded_keywords_frame = ExcludedKeywordsFrame(self, default_font, config['excluded_keywords'])
        self.excluded_keywords_frame.pack(fill='x', 
                                        padx=10, 
                                        pady=(10, 0))
        self.frames.append(self.excluded_keywords_frame)
        
        # CSV Settings
        self.csv_settings_frame = CsvSettingsFrame(self, default_font, config['csv_settings'])
        self.csv_settings_frame.pack(fill='x', 
                                        padx=10, 
                                        pady=(10, 0))
        self.frames.append(self.csv_settings_frame)
        
        # Footer - quit and start/stop buttons
        footer_frame = ctk.CTkFrame(self, bg_color='transparent', fg_color='transparent')
        footer_frame.pack(anchor='e')

        quit_button = ctk.CTkButton(footer_frame, text='Quit', text_color='white', fg_color='#ff4d4d', hover_color='#ff8080', command=self.destroy)
        quit_button.pack(side='left', padx=10, pady=(20, 10))

        self.start_stop_button = ctk.CTkButton(footer_frame, text='Start', text_color="#008000", fg_color='#4dff4d', hover_color='#3cb043', command=self.toggle_start_stop)
        self.start_stop_button.pack(side='left', padx=(10, 40), pady=(20, 10))

    def disable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                self.disable_frame(child)
            elif isinstance(child, ctk.CTkCheckBox):
                child.configure(state=ctk.DISABLED)
            elif isinstance(child, ctk.CTkEntry):
                child.configure(state=ctk.DISABLED)
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
                child.configure(state=ctk.NORMAL)
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
            if extracted_hash_ids == scraper.previous_page_hash_ids or self.stop_scraping:
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