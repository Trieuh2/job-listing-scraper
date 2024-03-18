import customtkinter as ctk
from .utils_wrapper import update_config_field
import threading


class IndeedSettingsFrame(ctk.CTkFrame):
    """A frame for setting Indeed search criteria.
    
    Search results will be catered to the critera set within the Indeed settings frame.

    Attributes:
        position_field (customtkinter.CTkEntry): The entry field for the position.
        location_field (customtkinter.CTkEntry): The entry field for the location.
        user_years_of_experience_field (customtkinter.CTkEntry): The entry field for the maximum years of experience.
        date_posted_option_menu (customtkinter.CTkOptionMenu): The option menu for selecting the date posted.
        job_type_option_menu (customtkinter.CTkOptionMenu): The option menu for selecting the job type.
        experience_level_option_menu (customtkinter.CTkOptionMenu): The option menu for selecting the experience level.
        _values (dict): A dictionary containing the initial values for the entry fields and option menus.
        _update_timer (threading.Timer): A timer used to schedule updates to the configuration file.
        _update_delay (float): The delay (in seconds) before the configuration file is updated after a change is made.
        _validate_command (function): The command used to validate input in the entry fields.
        _enabled_entry_field_fg_color (str): The foreground color of the entry fields when they are enabled.
    """


    def __init__(self, master, font, values, validate_command):
        """Initialize the IndeedSettingsFrame.
        
        Args:
            master (customtkinter.CTkFrame): The parent frame.
            font (customtkinter.CTkFont): The font used for the text elements in the frame.
            values (list): A list of initial entry field values to be displayed and option menu values to be selected.
            validate_command (function): A command registered with the root widget using `register()`. This command is used to validate input in entry fields.
        """
        super().__init__(master)
        self._values = values
        self._update_timer = None
        self._update_delay = 0.25
        self._validate_command = validate_command
        self._enabled_entry_field_fg_color = "black" if ctk.get_appearance_mode() == "Dark" else "white"

        self._create_title(font)
        self._create_fields_frame(font)
        self._create_option_menus_frame(font)
        self._load_config_values()

    def _create_title(self, font):
        """Create the title label for the Indeed settings frame.        
        
        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.

        Returns:
            None
        """
        title = "Indeed Search Settings"
        title_label = ctk.CTkLabel(self, text=title, font=(font, 18))
        title_label.pack(pady=(10, 20))

    def _create_fields_frame(self, font):
        """Create the frame that contains the text entry fields.
        
        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.

        Returns:
            None
        """
        fields_frame = ctk.CTkFrame(self, fg_color='transparent')
        fields_frame.pack(pady=(0, 10), anchor='center')

        self._create_position_field(font, fields_frame)
        self._create_location_field(font, fields_frame)
        self._create_years_experience_field(font, fields_frame)

    def _create_position_field(self, font, parent_frame):
        """Create the field for entering the position.
        
        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.
            parent_frame (customtkinter.CTkFrame): The parent frame that this entry field will be packed into.

        Returns:
            None
        """
        position_frame = ctk.CTkFrame(parent_frame)
        position_frame.pack(side='left', padx=(0, 5), anchor='center')

        position_label = ctk.CTkLabel(position_frame, text="Position", font=font)
        position_label.pack()

        self.position_field = ctk.CTkEntry(position_frame, placeholder_text="Position", font=font, fg_color=self._enabled_entry_field_fg_color)
        self.position_field.pack()
        self.position_field.bind('<KeyRelease>', lambda event: self.schedule_update('position', event))

    def _create_location_field(self, font, parent_frame):
        """Create the field for entering the location.
        
        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.
            parent_frame (customtkinter.CTkFrame): The parent frame that this entry field will be packed into.

        Returns:
            None
        """
        location_frame = ctk.CTkFrame(parent_frame)
        location_frame.pack(side='left', padx=5, anchor='center')

        location_label = ctk.CTkLabel(location_frame, text='Location', font=font)
        location_label.pack()

        self.location_field = ctk.CTkEntry(location_frame, placeholder_text="Location", font=font, fg_color=self._enabled_entry_field_fg_color)
        self.location_field.pack()
        self.location_field.bind('<KeyRelease>', lambda event: self.schedule_update('location', event))

    def _create_years_experience_field(self, font, parent_frame):
        """Create the field for entering the maximum years of experience.
        
        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.
            parent_frame (customtkinter.CTkFrame): The parent frame that this entry field will be packed into.

        Returns:
            None
        """
        years_experience_frame = ctk.CTkFrame(parent_frame)
        years_experience_frame.pack(side='left', padx=(5, 0), anchor='center')

        years_experience_label = ctk.CTkLabel(years_experience_frame, text="Max Years of Experience", font=font)
        years_experience_label.pack()

        self.user_years_of_experience_field = ctk.CTkEntry(years_experience_frame, placeholder_text="Max Years of Experience", font=font, fg_color=self._enabled_entry_field_fg_color)
        self.user_years_of_experience_field.pack()
        self.user_years_of_experience_field.bind('<KeyRelease>', lambda event: self.schedule_update('user_years_of_experience', event))
        self.user_years_of_experience_field.configure(validate='key', validatecommand=(self._validate_command, '%P'))

    def _create_option_menus_frame(self, font):
        """Create the frame that contains the option menus.

        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.

        Returns:
            None
        """
        option_menus_frame = ctk.CTkFrame(self, fg_color='transparent')
        option_menus_frame.pack(pady=(10, 10), anchor='center')

        self._create_date_posted_option_menu(font, option_menus_frame)
        self._create_job_type_option_menu(font, option_menus_frame)
        self._create_experience_level_option_menu(font, option_menus_frame)

    def _create_date_posted_option_menu(self, font, parent_frame):
        """Create the option menu for selecting the maximum age of the job posting (date posted).
        
        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.
            parent_frame (customtkinter.CTkFrame): The parent frame that this option menu will be packed into.

        Returns:
            None
        
        Examples:
            For the 'date_posted' field, if the value selected is 'Last 24 hours', the search results will contain any postings older than a day old.
            If no value is selected, job results may contain posts that are older than a month.
        """
        date_posted_frame = ctk.CTkFrame(parent_frame)
        date_posted_frame.pack(side='left', padx=(0, 5), anchor='center')

        date_posted_label = ctk.CTkLabel(date_posted_frame, text='Date Posted', font=font)
        date_posted_label.pack()

        self.date_posted_option_menu = ctk.CTkOptionMenu(
            date_posted_frame,
            values=['Select', 'Last 24 hours', 'Last 3 days', 'Last 7 days', 'Last 14 days', 'Last 30 days'],
            font=font,
            dropdown_font=font,
            command=lambda selected_value: self.update_config('max_days_posted_ago', selected_value)
        )
        self.date_posted_option_menu.pack()

    def _create_job_type_option_menu(self, font, parent_frame):
        """Create the option menu for selecting the job type.
        
        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.
            parent_frame (customtkinter.CTkFrame): The parent frame that this option menu will be packed into.

        Returns:
            None

        Examples:
            For the 'job_type' field, if the value selected is 'Full-time', then the search results will only include jobs that are tagged with 'Full-Time'.
            If no value is selected, job results may contain all types, including full-time, contract, part-time, temporary, internship, and untagged roles.
        """
        job_type_frame = ctk.CTkFrame(parent_frame)
        job_type_frame.pack(side='left', padx=5, anchor='center')

        job_type_label = ctk.CTkLabel(job_type_frame, text='Job Type', font=font)
        job_type_label.pack()

        self.job_type_option_menu = ctk.CTkOptionMenu(
            job_type_frame,
            values=['Select', 'Full-time', 'Contract', 'Part-time', 'Temporary', 'Internship'],
            font=font,
            dropdown_font=font,
            command=lambda selected_value: self.update_config('job_type', selected_value)
        )
        self.job_type_option_menu.pack()

    def _create_experience_level_option_menu(self, font, parent_frame):
        """Create the option menu for selecting the experience level.

        Args:
            font (customtkinter.CTkFont): The font family used for the text elements within the Frame.
            parent_frame (customtkinter.CTkFrame): The parent frame that this option menu will be packed into.

        Returns:
            None
        
        Examples:
            For the 'experience_level' field, if the value selected is 'Entry Level', then the search results will only include jobs that are tagged as Entry Level roles by Indeed.
            If no value is selected, job results may contain all types, including entry level, mid level, senior level, and untagged roles.
        """
        experience_level_frame = ctk.CTkFrame(parent_frame)
        experience_level_frame.pack(side='left', padx=(5, 0), anchor='center')

        experience_level_label = ctk.CTkLabel(experience_level_frame, text='Experience Level', font=font)
        experience_level_label.pack()

        self.experience_level_option_menu = ctk.CTkOptionMenu(
            experience_level_frame,
            values=["Select", "Entry Level", "Mid Level", "Senior Level"],
            font=font,
            dropdown_font=font,
            command=lambda selected_value: self.update_config('experience_level', selected_value)
        )
        self.experience_level_option_menu.pack()

    def _load_config_values(self):
        """Load the configuration file's values into the fields.
        
        Returns:
            None
        """
        self.position_field.insert(0, self._values['position'])
        self.location_field.insert(0, self._values['location'])
        
        # Set the initial value of the user_years_of_experience_field after configuring the validation
        self.user_years_of_experience_field.delete(0, 'end')
        self.user_years_of_experience_field.insert(0, self._values['user_years_of_experience'])

        self.date_posted_option_menu.set(self.get_field_friendly_name('max_days_posted_ago', self._values['max_days_posted_ago']))
        self.job_type_option_menu.set(self.get_field_friendly_name('job_type', self._values['job_type']))
        self.experience_level_option_menu.set(self.get_field_friendly_name('experience_level', self._values['experience_level']))

    def get_field_friendly_name(self, field_name, field_value):
        """Get the friendly name for a field value.

        Args:
            field_name (str): The name of the field.
            field_value (str): The actual value of the field.

        Returns:
            The friendly name corresponding to the actual value.
        
        Examples:
            For the 'max_days_posted_ago' field, if the field_value is '30', the friendly name returned is 'Last 30 days'.
        """
        field_dictionary = {
            'max_days_posted_ago': {
                '': 'Select',
                '1': 'Last 24 hours',
                '3': 'Last 3 days',
                '7': 'Last 7 days',
                '14': 'Last 14 days',
                '30': 'Last 30 days'
            },
            'job_type': {
                '': 'Select',
                '(fulltime)': 'Full-time',
                '(contract)': 'Contract',
                '(parttime)': 'Part-time',
                '(temporary)': 'Temporary',
                '(internship)': 'Internship'
            },
            'experience_level': {
                '': 'Select',
                '(ENTRY_LEVEL)': 'Entry Level',
                '(MID_LEVEL)': 'Mid Level',
                '(SENIOR_LEVEL)': 'Senior Level'
            }
        }

        return field_dictionary[field_name][field_value]

    def _get_field_value(self, field_name, friendly_name):
        """Get the value for a field based on its friendly name.

        Args:
            field_name (str): The name of the field.
            friendly_name (str): The friendly name of the value.

        Returns:
            The actual value corresponding to the friendly name.
        
        Examples:
            For the 'job_type' field, if the friendly_name is 'Full-time', the actual value returned is '(fulltime)'.
        """
        if field_name in ['position', 'location', 'user_years_of_experience']:
            return getattr(self, f"{field_name}_field").get()

        field_dictionary = {
            'max_days_posted_ago': {
                'Select': '',
                'Last 24 hours': '1',
                'Last 3 days': '3',
                'Last 7 days': '7',
                'Last 14 days': '14',
                'Last 30 days': '30'
            },
            'job_type': {
                'Select': '',
                'Full-time': '(fulltime)',
                'Contract': '(contract)',
                'Part-time': '(parttime)',
                'Temporary': '(temporary)',
                'Internship': '(internship)'
            },
            'experience_level': {
                'Select': '',
                'Entry Level': '(ENTRY_LEVEL)',
                'Mid Level': '(MID_LEVEL)',
                'Senior Level': '(SENIOR_LEVEL)'
            }
        }

        return field_dictionary[field_name][friendly_name]

    def update_config(self, field_name, selected_value_friendly_name):
        """Update a field in the configuration file's Indeed criteria settings with the new field value.
        
        Args:
            field_name (str): The name of the field.
            selected_value_friendly_name (str): The friendly name of the value selected in the option menu.

        Returns:
            None
        """
        updated_value = self._get_field_value(field_name, selected_value_friendly_name)
        update_config_field('config.json', 'indeed_criteria.' + field_name, updated_value)

    def schedule_update(self, field_name, event):
        """Schedule an update to the configuration file after a delay.
        
        Args:
            field_name (str): The name of the field.
            event: The event that triggered the update scheduling.

        Returns:
            None
        """
        if self._update_timer:
            self._update_timer.cancel()

        friendly_name = event.widget.get()
        self._update_timer = threading.Timer(self._update_delay, self.update_config, args=(field_name, friendly_name))
        self._update_timer.start()