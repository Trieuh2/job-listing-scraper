import json
import threading
from time import sleep

import customtkinter as ctk

from scraper import Scraper
import utils
from .indeed_settings_frame import IndeedSettingsFrame
from .excluded_keywords_frame import ExcludedKeywordsFrame
from .excel_settings_frame import ExcelSettingsFrame
from .utils_wrapper import update_config_field, is_valid_numerical_field_input

DEFAULT_NUM_PAGES_SCRAPE = 5
DEFAULT_CRAWL_DELAY = 10

class MainFrame(ctk.CTk):
    """
    Main frame of the job listing scraper application.

    This class is responsible for initializing and managing the layout
    of the application's main frame, including setting up subframes for
    different settings, managing the footer, and handling the scraping
    process.

    
    Attributes:
        frames (list): A list of subframes within the main frame.
        scraping_thread (threading.Thread or None): The thread responsible for running the scraper.
        stop_scraping (bool): A flag to indicate whether the scraping process should be stopped.
        default_font (customtkinter.CTkFont): The default font used for widgets in the frame.
        validate_command (function): A function to validate numerical input fields.
        config (dict): The configuration dictionary loaded from the JSON file.
        enabled_entry_field_fg_color (str): The foreground color for enabled entry fields.
        disabled_entry_field_fg_color (str): The foreground color for disabled entry fields.
        indeed_settings_frame (IndeedSettingsFrame): The subframe for Indeed settings.
        excluded_keywords_frame (ExcludedKeywordsFrame): The subframe for excluded keywords.
        csv_settings_frame (ExcelSettingsFrame): The subframe for CSV settings.
        scrape_settings_frame (customtkinter.CTkFrame): The frame containing the scrape settings.
        scrape_all_checkbox (customtkinter.CTkCheckBox): The checkbox for scraping all pages.
        num_pages_scrape_frame (customtkinter.CTkFrame): The frame for setting the number of pages to scrape.
        num_pages_to_scrape_entry_field (customtkinter.CTkEntry): The entry field for the number of pages to scrape.
        crawl_delay_frame (customtkinter.CTkFrame): The frame for setting the crawl delay.
        crawl_delay_entry_field (customtkinter.CTkEntry): The entry field for the crawl delay.
        start_stop_button (customtkinter.CTkButton): The button to start or stop the scraping process.
    """

    # Initialization Functions
    def __init__(self):
        """Initialize the main frame.
        
        This method sets up the appearance of the main frame, loads the
        configuration from a JSON file, initializes the subframes, and
        creates the footer.
        """
        super().__init__()
        self.frames = []
        self.scraping_thread = None
        self.stop_scraping = False
        self.default_font = ctk.CTkFont(family='Roboto', size=12)
        self.validate_command = self.register(is_valid_numerical_field_input)

        with open('config.json') as config_file:
            self.config = json.load(config_file)

        self.title('Job Listing Scraper')
        self.geometry('800x775')
        self.resizable(False, False)

        ctk.set_appearance_mode('System')
        ctk.set_default_color_theme('dark-blue')
        self.enabled_entry_field_fg_color = "black" if ctk.get_appearance_mode() == "Dark" else "white"
        self.disabled_entry_field_fg_color = "#A0A0A0"

        self.init_frames()
        self.create_footer()  

    def init_frames(self) -> None:
        """
        Initialize all frames within the main frame.
        
        This method sets up the Indeed settings frame, the excluded keywords
        frame, and the CSV settings frame.

        Returns:
            None
        """
        self.init_indeed_settings_frame()
        self.init_excluded_keywords_frame()
        self.init_excel_settings_frame()

    def init_indeed_settings_frame(self) -> None:
        """
        Initialize the Indeed settings frame.
        
        This frame allows the user to configure search criteria for Indeed job listings.

        Returns:
            None
        """
        self.indeed_settings_frame = IndeedSettingsFrame(
        self, self.default_font, self.config['indeed_criteria'], self.validate_command)
        self.indeed_settings_frame.pack(fill='x', padx=10, pady=(10, 0))
        self.frames.append(self.indeed_settings_frame)

    def init_excluded_keywords_frame(self) -> None:
        """
        Initialize the excluded keywords frame.
        
        This frame allows the user to specify keywords to exclude from the search results.

        Returns:
            None
        """
        self.excluded_keywords_frame = ExcludedKeywordsFrame(
            self, self.default_font, self.config['excluded_keywords'])
        self.excluded_keywords_frame.pack(fill='x', padx=10, pady=(10, 0))
        self.frames.append(self.excluded_keywords_frame)

    def init_excel_settings_frame(self) -> None:
        """
        Initialize the Excel settings frame.
        
        This frame allows the user to configure settings for exporting the scraped data to an Excel file.

        Returns:
            None
        """
        self.excel_settings_frame = ExcelSettingsFrame(
            self, self.default_font, self.config['csv_settings'])
        self.excel_settings_frame.pack(fill='x', padx=10, pady=(10, 0))
        self.frames.append(self.excel_settings_frame)

    # Footer and Settings Functions
    def create_footer(self) -> None:
        """
        Create the footer of the main frame.
        
        The footer contains the scrape settings frame and the button frame.

        Returns:
            None
        """
        footer_frame = ctk.CTkFrame(self, bg_color='transparent', fg_color='transparent')
        footer_frame.pack(fill='x', pady=10)

        self.create_scrape_settings_frame(footer_frame)
        self.create_button_frame(footer_frame)

    def create_scrape_settings_frame(self, parent: ctk.CTkFrame) -> None:
        """
        Create the scrape settings frame within the footer.
        
        This frame contains the 'Scrape all pages?' checkbox, the number of pages to scrape entry field,
        and the crawl delay entry field.

        Args:
            parent (customtkinter.CTkFrame): The parent frame that will contain the scrape settings frame.

        Returns:
            None
        """
        self.scrape_settings_frame = ctk.CTkFrame(
            parent, bg_color='transparent', fg_color='transparent')
        self.scrape_settings_frame.pack(side='left', fill='x')

        self.scrape_all_checkbox = ctk.CTkCheckBox(
            self.scrape_settings_frame, text="Scrape all pages?", command=self.toggle_scrape_all_checkbox)
        self.scrape_all_checkbox.pack(side='left', padx=(20, 10), pady=(20, 10))

        self.create_num_pages_scrape_frame(self.scrape_settings_frame)
        self.create_crawl_delay_frame(self.scrape_settings_frame)
        self.initialize_scrape_settings()

        self.frames.append(self.scrape_settings_frame)

    def create_num_pages_scrape_frame(self, parent: ctk.CTkFrame) -> None:
        """
        Create the frame for setting the number of pages to scrape.
        
        This frame contains a label and an entry field for specifying the number of pages to scrape.

        Args:
            parent (customtkinter.CTkFrame): The parent frame that will contain the number of pages to scrape frame.

        Returns:
            None
        """
        self.num_pages_scrape_frame = ctk.CTkFrame(
            parent, bg_color='transparent', fg_color='transparent')
        self.num_pages_scrape_frame.pack(side='left', padx=10, pady=(5, 10))

        num_pages_to_scrape_label = ctk.CTkLabel(
            self.num_pages_scrape_frame, text='Number of pages to scrape', font=self.default_font)
        num_pages_to_scrape_label.pack(anchor='w')

        self.num_pages_to_scrape_entry_field = ctk.CTkEntry(
            self.num_pages_scrape_frame, placeholder_text=str(DEFAULT_NUM_PAGES_SCRAPE), font=self.default_font, fg_color=self.enabled_entry_field_fg_color)
        self.num_pages_to_scrape_entry_field.bind(
            '<KeyRelease>', command=self.update_config_num_pages_scrape)
        self.num_pages_to_scrape_entry_field.pack(anchor='w')
        self.num_pages_to_scrape_entry_field.configure(validate='key', validatecommand=(self.validate_command, '%P'))

        self.frames.append(self.num_pages_scrape_frame)

    def create_crawl_delay_frame(self, parent: ctk.CTkFrame) -> None:
        """
        Create the frame for setting the crawl delay.
        
        The crawl delay is the minimum number of seconds to wait between page requests.
        This frame contains a label and an entry field for specifying the crawl delay.

        Args:
            parent (customtkinter.CTkFrame): The parent frame that will contain the crawl delay frame.

        Returns:
            None
        """
        self.crawl_delay_frame = ctk.CTkFrame(
            parent, bg_color='transparent', fg_color='transparent')
        self.crawl_delay_frame.pack(side='left', padx=10, pady=(5, 10))

        crawl_delay_label = ctk.CTkLabel(
            self.crawl_delay_frame, text='Crawl Delay', font=self.default_font)
        crawl_delay_label.pack(anchor='w')

        self.crawl_delay_entry_field = ctk.CTkEntry(self.crawl_delay_frame, font=self.default_font, fg_color=self.enabled_entry_field_fg_color)
        self.crawl_delay_entry_field.pack(anchor='w')
        self.crawl_delay_entry_field.bind('<KeyRelease>', command=self.update_config_crawl_delay)
        self.crawl_delay_entry_field.configure(validate='key', validatecommand=(self.validate_command, '%P'))

        self.frames.append(self.crawl_delay_frame)

    def initialize_scrape_settings(self) -> None:
        """
        Initialize the scrape settings based on the configuration file.
        
        This method sets the initial values of the scrape settings fields and checkboxes
        based on the values stored in the configuration file.

        Returns:
            None
        """
        if self.config['num_pages_to_scrape'] == 0:
            self.scrape_all_checkbox.select()
            self.num_pages_to_scrape_entry_field.configure(state=ctk.DISABLED, fg_color=self.disabled_entry_field_fg_color)
        else:
            self.num_pages_to_scrape_entry_field.insert(
                index=1, string=str(self.config['num_pages_to_scrape']))
            self.num_pages_to_scrape_entry_field.configure(state=ctk.NORMAL, fg_color=self.enabled_entry_field_fg_color)

        # Initialize crawl delay value
        self.crawl_delay_entry_field.insert(0, self.config['crawl_delay'])

    # Footer Button and Checkbox Functions
    def create_button_frame(self, parent: ctk.CTkFrame) -> None:
        """
        Create the button frame within the footer.
        
        This frame contains the Quit and Start/Stop buttons.

        Args:
            parent (customtkinter.CTkFrame): The parent frame that will contain the button frame.

        Returns:
            None
        """
        button_frame = ctk.CTkFrame(
            parent, bg_color='transparent', fg_color='transparent')
        button_frame.pack(side='right', anchor='s')

        quit_button = ctk.CTkButton(
            button_frame, text='Quit', text_color='white', fg_color='#ff4d4d', hover_color='#ff8080', command=self.destroy)
        quit_button.pack(side='left', padx=(10, 5), pady=(20, 10))

        self.start_stop_button = ctk.CTkButton(
            button_frame, text='Start', text_color="#008000", fg_color='#4dff4d', hover_color='#3cb043', command=self.toggle_start_stop)
        self.start_stop_button.pack(side='left', padx=(5, 20), pady=(20, 10))

    def toggle_start_stop(self) -> None:
        """
        Toggle between starting and stopping the scraping process.
        
        When the button is pressed, the method checks the current text of the button to determine
        whether the scraping process should be started or stopped. It then updates the button text
        and appearance accordingly.

        Returns:
            None
        """
        if self.start_stop_button.cget('text') == 'Start':
            self.disable_frames()
            self.start_stop_button.configure(text='Stop', text_color='white', fg_color='#ff4d4d', hover_color='#ff8080')
            self.begin_scraping()
        elif self.start_stop_button.cget('text') == 'Stop':
            self.stop_scraping = True
            while self.scraping_thread:
                sleep(0.1)
            self.enable_frames()
            self.start_stop_button.configure(text='Start', text_color="#008000", fg_color='#4dff4d', hover_color='#3cb043')

    def reset_start_stop_button(self) -> None:
        """
        Reset the start/stop button to its initial state.
        
        This method is called after the scraping process has completed to reset the button's text
        and appearance to the initial 'Start' state.

        Returns:
            None
        """
        self.stop_scraping = True
        self.start_stop_button.configure(text='Start', text_color="#008000", fg_color='#4dff4d', hover_color='#3cb043')

    def toggle_scrape_all_checkbox(self) -> None:
        """
        Toggle the 'Scrape all pages' checkbox.
        
        This method enables or disables the number of pages to scrape entry field based on whether
        the 'Scrape all pages' checkbox is checked or unchecked.

        Returns:
            None
        """
        if self.scrape_all_checkbox.get() == 0:
            # Configured to scrape a specific num of pages
            self.num_pages_to_scrape_entry_field.configure(state=ctk.NORMAL, fg_color=self.enabled_entry_field_fg_color)
            self.set_default_config_num_pages_scrape()
        else:
            # Configured to scrape all pages
            self.num_pages_to_scrape_entry_field.delete(0, len(self.num_pages_to_scrape_entry_field.get()))
            self.num_pages_to_scrape_entry_field.configure(state=ctk.DISABLED, fg_color=self.disabled_entry_field_fg_color)
            update_config_field(filepath='config.json', field_path='num_pages_to_scrape', new_value=0)

    # Configuration Update Functions
    def update_config_num_pages_scrape(self, event) -> None:
        """
        Update the configuration file for the number of pages to scrape.
        
        This method updates the 'num_pages_to_scrape' field in the configuration file based on the
        value entered in the corresponding entry field.

        Args:
            event: The event that triggered the update to the number of pages to scrape setting.

        Returns:
            None
        """
        new_value = self.num_pages_to_scrape_entry_field.get()

        if new_value:
            update_config_field(filepath='config.json', field_path='num_pages_to_scrape', new_value=int(new_value))
        else:
            self.set_default_config_num_pages_scrape()

    def set_default_config_num_pages_scrape(self) -> None:
        """
        Set the configuration file and entry field to scrape the default number of pages.
        
        This method updates the 'num_pages_to_scrape' field in the configuration file to the default value
        and updates the corresponding entry field.

        Returns:
            None
        """
        self.num_pages_to_scrape_entry_field.delete(0, len(self.num_pages_to_scrape_entry_field.get()))
        self.num_pages_to_scrape_entry_field.insert(0, DEFAULT_NUM_PAGES_SCRAPE)
        update_config_field(filepath='config.json', field_path='num_pages_to_scrape', new_value=DEFAULT_NUM_PAGES_SCRAPE)

    def update_config_crawl_delay(self, event) -> None:
        """
        Update the configuration file for the entered crawl delay.

        Args:
            event: The event that triggered the crawl delay to be updated.
        
        This method updates the 'crawl_delay' field in the configuration file based on the
        value entered in the corresponding entry field.

        Returns:
            None
        """
        new_value = self.crawl_delay_entry_field.get()

        if new_value:
            update_config_field(filepath='config.json', field_path='crawl_delay', new_value=int(new_value))
        else:
            self.set_default_config_crawl_delay()

    def set_default_config_crawl_delay(self) -> None:
        """
        Set the configuration file and entry field to the default crawl delay.
        
        This method updates the 'crawl_delay' field in the configuration file to the default value
        and updates the corresponding entry field.

        Returns:
            None
        """
        self.crawl_delay_entry_field.delete(0, len(self.crawl_delay_entry_field.get()))
        self.crawl_delay_entry_field.insert(0, DEFAULT_CRAWL_DELAY)
        update_config_field(filepath='config.json', field_path='crawl_delay', new_value=DEFAULT_CRAWL_DELAY)

    # Scraper Functions
    def begin_scraping(self) -> None:
        """
        Begin the scraping process in a separate thread.
        
        This method creates and starts a new thread for running the scraper.

        Returns:
            None
        """
        self.stop_scraping = False
        self.scraping_thread = threading.Thread(target=self.run_scraper)
        self.scraping_thread.start()

    def setup_scraper(self) -> Scraper:
        """
        Set up the scraper with the latest configuration values.
        
        This method loads the latest configuration values and initializes a new Scraper instance
        with the specified Indeed URL and search criteria.

        Returns:
            Scraper: An instance of the scraper used to perform the scraping.
        """
        with open('config.json') as config_file:
            self.config = json.load(config_file)

        indeed_criteria = self.config['indeed_criteria']
        indeed_url = utils.build_indeed_url(
            max_days_posted_ago=indeed_criteria['max_days_posted_ago'],
            position=indeed_criteria['position'],
            experience_level=indeed_criteria['experience_level'],
            job_type=indeed_criteria['job_type'],
            location=indeed_criteria['location']
        )

        return Scraper(indeed_url)

    def run_scraper(self) -> None:
        """
        Run the scraper to begin extracting job listings.
        
        This method initiates the scraping process and continues until the specified number of pages
        has been scraped or until the stop_scraping flag is set to True. It also handles updating
        the spreadsheet with the scraped data if specified in the configuration.

        Returns:
            None
        """
        scraper = self.setup_scraper()
        num_pages_to_scrape = self.config['num_pages_to_scrape']
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
        print(f"Number of new records: {len(scraper.jobs) - scraper.initial_num_records}")
        print(f"Number of errored extractions: {scraper.num_errored_job_extractions}\n")

        scraper.shutdown()
    
        if self.config['csv_settings']['update_spreadsheet_on_completion']:
            utils.write_jobs_excel(self.config['csv_settings']['excel_output_path'], scraper.jobs)

        self.scraping_thread = None
        self.enable_frames()
        self.reset_start_stop_button()

    # Frame Enable/Disable Functions
    def disable_frames(self) -> None:
        """
        Disable all frames in the main frame.
        
        This method iteratively disables all frames and their child widgets.

        Returns:
            None
        """
        for frame in self.frames:
            self.disable_frame(frame)

    def enable_frames(self) -> None:
        """
        Enable all frames in the main frame.
        
        This method iteratively enables all frames and their child widgets.

        Returns:
            None
        """
        for frame in self.frames:
            self.enable_frame(frame)

    def disable_frame(self, frame: ctk.CTkFrame) -> None:
        """
        Disable a specific frame and all its children.

        This method disables all child widgets of a given frame, including nested frames.

        Args:
            frame (customtkinter.CTkFrame): The frame that contains widgets to be disabled.
        
        Returns:
            None
        """
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                self.disable_frame(child)
            elif isinstance(child, ctk.CTkCheckBox):
                child.configure(state=ctk.DISABLED)
            elif isinstance(child, ctk.CTkEntry):
                child.configure(state=ctk.DISABLED, fg_color=self.disabled_entry_field_fg_color)
            elif isinstance(child, ctk.CTkOptionMenu):
                child.configure(state=ctk.DISABLED)
            elif isinstance(child, ctk.CTkTextbox):
                child.configure(state=ctk.DISABLED)
            elif isinstance(child, ctk.CTkButton):
                child.configure(state=ctk.DISABLED)
    
    def enable_frame(self, frame: ctk.CTkFrame) -> None:
        """
        Enable a specific frame and all its child widgets.

        This method recursively enables all child widgets of a given frame, including nested frames. 
        "Enabling" a widget typically means making it interactive or responsive to user input.

        Args:
            frame (customtkinter.CTkFrame): The frame that contains widgets to be enabled.
        
        Returns:
            None
        """
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                self.enable_frame(child)
            elif isinstance(child, ctk.CTkCheckBox):
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkEntry):
                if child != self.num_pages_to_scrape_entry_field or self.scrape_all_checkbox.get() == 0:
                    child.configure(state=ctk.NORMAL, fg_color=self.enabled_entry_field_fg_color)
            elif isinstance(child, ctk.CTkOptionMenu):
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkTextbox):
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkButton):
                child.configure(state=ctk.NORMAL)