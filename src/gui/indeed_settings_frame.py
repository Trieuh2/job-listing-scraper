import customtkinter as ctk
from gui.tooltip import ToolTip
from .utils_wrapper import update_config_field
import threading


class IndeedSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, font, values):
        super().__init__(master)
        self.values = values
        self.update_timer = None
        self.update_delay = 1.5

        self._create_title(font)
        self._create_fields_frame(font)
        self._create_option_menus_frame(font)
        self.load_config_values()

    def _create_title(self, font):
        title = "Indeed Search Settings"
        title_label = ctk.CTkLabel(self, text=title, font=(font, 18))
        title_label.pack(pady=(10, 20))

    def _create_fields_frame(self, font):
        fields_frame = ctk.CTkFrame(self, fg_color='transparent')
        fields_frame.pack(pady=(0, 10), anchor='center')

        self._create_position_field(font, fields_frame)
        self._create_location_field(font, fields_frame)
        self._create_years_experience_field(font, fields_frame)

    def _create_position_field(self, font, parent_frame):
        position_frame = ctk.CTkFrame(parent_frame)
        position_frame.pack(side='left', padx=(0, 5), anchor='center')

        position_label = ctk.CTkLabel(position_frame, text="Position", font=font)
        position_label.pack()

        self.position_field = ctk.CTkEntry(position_frame, placeholder_text="Position", font=font)
        self.position_field.pack()
        self.position_field.bind('<KeyRelease>', lambda event: self.schedule_update('position', event))

    def _create_location_field(self, font, parent_frame):
        location_frame = ctk.CTkFrame(parent_frame)
        location_frame.pack(side='left', padx=5, anchor='center')

        location_label = ctk.CTkLabel(location_frame, text='Location', font=font)
        location_label.pack()

        self.location_field = ctk.CTkEntry(location_frame, placeholder_text="Location", font=font)
        self.location_field.pack()
        self.location_field.bind('<KeyRelease>', lambda event: self.schedule_update('location', event))

    def _create_years_experience_field(self, font, parent_frame):
        years_experience_frame = ctk.CTkFrame(parent_frame)
        years_experience_frame.pack(side='left', padx=(5, 0), anchor='center')

        years_experience_label = ctk.CTkLabel(years_experience_frame, text="Max Years of Experience", font=font)
        years_experience_label.pack()

        self.user_years_of_experience_field = ctk.CTkEntry(years_experience_frame, placeholder_text="Max Years of Experience", font=font)
        self.user_years_of_experience_field.pack()
        self.user_years_of_experience_field.bind('<KeyRelease>', lambda event: self.schedule_update('user_years_of_experience', event))

    def _create_option_menus_frame(self, font):
        option_menus_frame = ctk.CTkFrame(self, fg_color='transparent')
        option_menus_frame.pack(pady=(10, 10), anchor='center')

        self._create_date_posted_option_menu(font, option_menus_frame)
        self._create_job_type_option_menu(font, option_menus_frame)
        self._create_experience_level_option_menu(font, option_menus_frame)

    def _create_date_posted_option_menu(self, font, parent_frame):
        date_posted_frame = ctk.CTkFrame(parent_frame)
        date_posted_frame.pack(side='left', padx=(0, 5), anchor='center')

        date_posted_label = ctk.CTkLabel(date_posted_frame, text='Date Posted', font=font)
        date_posted_label.pack()

        self.date_posted_option_menu = ctk.CTkOptionMenu(
            date_posted_frame,
            values=['Select', 'Last 24 hours', 'Last 3 days', 'Last 7 days', 'Last 30 days'],
            font=font,
            dropdown_font=font,
            command=lambda selected_value: self.update_config('max_days_posted_ago', selected_value)
        )
        self.date_posted_option_menu.pack()

    def _create_job_type_option_menu(self, font, parent_frame):
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

    def load_config_values(self):
        self.position_field.insert(0, self.values['position'])
        self.location_field.insert(0, self.values['location'])
        self.user_years_of_experience_field.insert(0, self.values['user_years_of_experience'])

        self.date_posted_option_menu.set(self.get_field_friendly_name('max_days_posted_ago', self.values['max_days_posted_ago']))
        self.job_type_option_menu.set(self.get_field_friendly_name('job_type', self.values['job_type']))
        self.experience_level_option_menu.set(self.get_field_friendly_name('experience_level', self.values['experience_level']))

    def get_field_friendly_name(self, field_name, field_value):
        field_dictionary = {
            'max_days_posted_ago': {
                '': 'Select',
                '1': 'Last 24 hours',
                '3': 'Last 3 days',
                '7': 'Last 7 days',
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

    def get_field_value(self, field_name, friendly_name=None):
        if field_name in ['position', 'location', 'user_years_of_experience']:
            return getattr(self, f"{field_name}_field").get()

        field_dictionary = {
            'max_days_posted_ago': {
                'Select': '',
                'Last 24 hours': '1',
                'Last 3 days': '3',
                'Last 7 days': '7',
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

    def update_config(self, field_name, selected_value_friendly_name=None):
        updated_value = self.get_field_value(field_name, selected_value_friendly_name)
        update_config_field('config.json', 'indeed_criteria.' + field_name, updated_value)

    def schedule_update(self, field_name, event):
        if self.update_timer:
            self.update_timer.cancel()

        friendly_name = event.widget.get()
        self.update_timer = threading.Timer(self.update_delay, self.update_config, args=(field_name, friendly_name))
        self.update_timer.start()