import customtkinter as ctk
from tkinter import filedialog
from utils import update_config_field

class CsvSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, font, values):
        super().__init__(master)
        self.values = values
        self.font = font
        self.create_widgets()

    def create_widgets(self):
        self.create_title_label()
        self.create_output_path_frame()
        self.create_update_csv_frame()

    def create_title_label(self):
        title_label = ctk.CTkLabel(self, text="CSV Settings", font=(self.font, 18))
        title_label.pack(pady=(10, 20))

    def create_output_path_frame(self):
        output_path_frame = ctk.CTkFrame(self, fg_color='transparent')
        output_path_frame.pack(anchor='center')

        selected_label = ctk.CTkLabel(output_path_frame, text='Output Path')
        selected_label.pack(side='left', padx=5, pady=(0, 10))

        outline_frame = ctk.CTkFrame(output_path_frame, corner_radius=10, fg_color="black")
        outline_frame.pack(side='left', padx=5, pady=(0, 10))

        self.current_path_label = ctk.CTkLabel(outline_frame, font=self.font, text=self.values['csv_output_path'])
        self.current_path_label.pack(side='left', padx=10, pady=5)

        browse_button = ctk.CTkButton(output_path_frame, font=self.font, text='Browse', command=self.browse_folder)
        browse_button.pack(side='left', padx=10, pady=(0, 10))

    def create_update_csv_frame(self):
        update_csv_frame = ctk.CTkFrame(self, fg_color='transparent')
        update_csv_frame.pack(anchor="center")

        self.update_csv_upon_completion_checkbox = ctk.CTkCheckBox(update_csv_frame, onvalue=True, offvalue=False,
                                                                   font=self.font, text="Update CSV on completion",
                                                                   command=self.update_csv_on_completion)
        if self.values['update_csv_on_completion']:
            self.update_csv_upon_completion_checkbox.select()
        self.update_csv_upon_completion_checkbox.pack(side="left", padx=10, pady=(0, 10))

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            new_path = f"{folder_path}/data.csv"
            update_config_field('config.json', 'csv_settings.csv_output_path', new_path)
            self.current_path_label.configure(text=new_path)

    def update_csv_on_completion(self):
        checkbox_value = self.update_csv_upon_completion_checkbox.get()
        update_config_field('config.json', 'csv_settings.update_csv_on_completion', checkbox_value)
