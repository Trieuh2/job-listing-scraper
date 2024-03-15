import customtkinter as ctk
from tkinter import filedialog
from utils import update_config_field

class CsvSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, font, values):
        super().__init__(master)
        self.values = values
        title = "CSV Settings"
        title_label = ctk.CTkLabel(self, text=title, font=(font, 18))
        title_label.pack(pady=(10, 20))

        # Frame for CSV output path
        output_path_frame = ctk.CTkFrame(self, fg_color='transparent')
        output_path_frame.pack(anchor='center')
        
        selected_label = ctk.CTkLabel(output_path_frame, text='Output Path')
        selected_label.pack(side='left', padx=5, pady=(0,10))
        outline_frame = ctk.CTkFrame(output_path_frame, corner_radius=10, fg_color="black")
        outline_frame.pack(side='left', padx=5, pady=(0,10))

        self.current_path_label = ctk.CTkLabel(outline_frame, 
                                          font=font,
                                          text= self.values['csv_output_path'])
        self.current_path_label.pack(side='left', padx=10, pady=5)

        browse_button = ctk.CTkButton(output_path_frame, 
                                      font=font, 
                                      text='Browse',
                                      command=self.browse_folder)
        browse_button.pack(side='left', padx=10, pady=(0,10))

        # Frame for updating CSV upon completion
        frame = ctk.CTkFrame(self, fg_color='transparent')
        frame.pack(anchor="center")
        self.update_csv_upon_completion_checkbox = ctk.CTkCheckBox(frame, 
                                                              onvalue=True,
                                                              offvalue=False,
                                                              font=font,
                                                              text="Update CSV on completion",
                                                              command=self.update_csv_on_completion
                                                              )
        if self.values['update_csv_on_completion']:
            self.update_csv_upon_completion_checkbox.select()
        
        self.update_csv_upon_completion_checkbox.pack(side="left", padx=10, pady=(0,10))

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            update_config_field('config.json', 'csv_settings.csv_output_path', f"{folder_path}/data.csv")
            self.current_path_label.configure(text=f"{folder_path}/data.csv")

    def update_csv_on_completion(self):
        checkbox_value = self.update_csv_upon_completion_checkbox.get()
        update_config_field('config.json', 'csv_settings.update_csv_on_completion', checkbox_value)