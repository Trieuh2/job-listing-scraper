import customtkinter as ctk
from utils_wrapper import update_config_field

class IndeedSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, font, values):
        super().__init__(master)
        self.values = values
        title = "Indeed Search Settings"
        title_label = ctk.CTkLabel(self, text=title, font=(font, 18))
        title_label.pack(pady=(10, 20))

        # Create a frame for fields: Position, Location, Max Years of Experience
        fields_frame = ctk.CTkFrame(self, fg_color='transparent')
        fields_frame.pack(pady=(0, 10))

        self.position_field = ctk.CTkEntry(fields_frame, 
                                           placeholder_text="Position", 
                                           font=font)
        self.position_field.pack(side='left', padx=(0, 5), anchor='center')

        self.location_field = ctk.CTkEntry(fields_frame, 
                                           placeholder_text="Location", 
                                           font=font)
        self.location_field.pack(side='left', padx=5, anchor='center')

        self.years_of_experience_field = ctk.CTkEntry(fields_frame, 
                                                      placeholder_text="Max Years of Experience", 
                                                      font=font)
        self.years_of_experience_field.pack(side='left', padx=(5, 0), anchor='center')

        fields_frame.pack(anchor='center')

        # Create a frame to hold the option menus: Date Posted, Job Type, Experience Level
        option_menus_frame = ctk.CTkFrame(self, fg_color='transparent')
        option_menus_frame.pack(pady=(10, 10))

        self.date_posted_option_menu = ctk.CTkOptionMenu(option_menus_frame, 
                                                         values=['Date posted', 'Last 24 hours', 'Last 3 days', 'Last 7 days', 'Last 30 days'], 
                                                         font=font,
                                                         dropdown_font=font,
                                                         command=lambda selected_value: self.update_field('max_days_posted_ago', selected_value))
        self.date_posted_option_menu.pack(side='left', padx=(0, 5), anchor='center')

        self.job_type_option_menu = ctk.CTkOptionMenu(option_menus_frame, 
                                                      values=['Job type', 'Full-time', 'Contract', 'Part-time', 'Temporary', 'Internship'], 
                                                      font=font,
                                                      dropdown_font=font,
                                                      command=lambda selected_value: self.update_field('job_type', selected_value))
        self.job_type_option_menu.pack(side='left', padx=5, anchor='center')

        self.experience_level_option_menu = ctk.CTkOptionMenu(option_menus_frame,
                                                              values=["Experience Level", "Entry Level", "Mid Level", "Senior Level"],
                                                              font=font,
                                                              dropdown_font=font,
                                                              command=lambda selected_value: self.update_field('experience_level', selected_value))

        self.experience_level_option_menu.pack(side='left', padx=(5, 0), anchor='center')
        option_menus_frame.pack(anchor='center')

        # Load previously via config.json
        self.load_config_values()

    def get_field_friendly_name(self, field_name, field_value):
        field_dictionary = {
            'max_days_posted_ago': {
                '' : 'Date posted',
                '1' : 'Last 24 hours',
                '3' : 'Last 3 days',
                '7' : 'Last 7 days',
                '30' : 'Last 30 days'
            },
            'job_type': {
                '': 'Job type',
                '(fulltime)': 'Full-time',
                '(contract)': 'Contract',
                '(parttime)': 'Part-time',
                '(temporary)': 'Temporary',
                '(internship)': 'Internship'
            },
            'experience_level':{
                '': 'Experience Level',
                '(ENTRY_LEVEL)': 'Entry Level',
                '(MID_LEVEL)': 'Mid Level',
                '(SENIOR_LEVEL)': 'Senior Level'
            }
        }
        
        return field_dictionary[field_name][field_value]

    def get_field_value(self, field_name, friendly_name):
        field_dictionary = {
            'max_days_posted_ago': {
                'Date posted': '',
                'Last 24 hours': '1',
                'Last 3 days': '3',
                'Last 7 days': '7',
                'Last 30 days': '30'
            },
            'job_type': {
                'Job type': '',
                'Full-time': '(fulltime)',
                'Contract': '(contract)',
                'Part-time': '(parttime)',
                'Temporary': '(temporary)',
                'Internship': '(internship)'
            },
            'experience_level': {
                'Experience Level': '',
                'Entry Level': '(ENTRY_LEVEL)',
                'Mid Level': '(MID_LEVEL)',
                'Senior Level': '(SENIOR_LEVEL)'
            }
        }
        
        return field_dictionary[field_name][friendly_name]

    def load_config_values(self):
        self.position_field.insert(0, self.values['position'])
        self.location_field.insert(0, self.values['location'])
        self.years_of_experience_field.insert(0, self.values['user_years_of_experience'])
        
        self.date_posted_option_menu.set(self.get_field_friendly_name('max_days_posted_ago', self.values['max_days_posted_ago']))
        self.job_type_option_menu.set(self.get_field_friendly_name('job_type', self.values['job_type']))
        self.experience_level_option_menu.set(self.get_field_friendly_name('experience_level', self.values['experience_level']))
    
    def update_field(self, field_name, selected_value_friendly_name):
        updated_value = self.get_field_value(field_name, selected_value_friendly_name)
        update_config_field('config.json', 'indeed_criteria.' + field_name, updated_value)