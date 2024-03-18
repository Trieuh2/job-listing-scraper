import customtkinter as ctk
from tkinter import filedialog
from utils import update_config_field

class ExcelSettingsFrame(ctk.CTkFrame):
    """
    A frame for setting the Excel data output preferences.
    
    Attributes:
        master (customtkinter.CTkFrame): The parent widget.
        _font (customtkinter.CTkFont): The font family used for the text elements within the Frame.
        _values (dict): Configuration values for the frame, including paths and update flags.
        current_path_label (customtkinter.CTkLabel): Label displaying the current output path.
        update_excel_upon_completion_checkbox (customtkinter.CTkCheckBox): Checkbox to enable/disable spreadsheet updates upon completion.
    """

    def __init__(self, master, font, values):
        """
        Initializes the ExcelSettingsFrame with a parent widget, font, and initial values.
        It also creates the widgets for the frame.

        Args:
            master (customtkinter.CTkFrame): The parent frame.
            font (str): The font family to use for text elements.
            values (dict): Initial configuration values for the frame.
        """
        super().__init__(master)
        self._values = values
        self._font = font
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and arranges the widgets within the frame.

        Returns:
            None
        """
        self._create_title_label()
        self._create_output_path_frame()
        self._create_update_excel_frame()

    def _create_title_label(self):
        """Creates the title label widget.

        Returns:
            None
        """
        title_label = ctk.CTkLabel(self, text="Excel Settings", font=(self._font, 18))
        title_label.pack(pady=(10, 20))

    def _create_output_path_frame(self):
        """Creates the frame and widgets for output path selection.

        Returns:
            None
        """
        output_path_frame = ctk.CTkFrame(self, fg_color='transparent')
        output_path_frame.pack(anchor='center')

        selected_label = ctk.CTkLabel(output_path_frame, text='Output Path')
        selected_label.pack(side='left', padx=5, pady=(0, 10))

        foreground_color = "black" if ctk.get_appearance_mode() == "Dark" else "white"
        outline_frame = ctk.CTkFrame(output_path_frame, corner_radius=10, fg_color=foreground_color)
        outline_frame.pack(side='left', padx=5, pady=(0, 10))

        self.current_path_label = ctk.CTkLabel(outline_frame, font=self._font, text=self._values['excel_output_path'])
        self.current_path_label.pack(side='left', padx=10, pady=5)

        browse_button = ctk.CTkButton(output_path_frame, font=self._font, text='Browse', command=self._browse_folder)
        browse_button.pack(side='left', padx=10, pady=(0, 10))

    def _create_update_excel_frame(self):
        """Creates the frame and checkbox for enabling or disabling spreadsheet updates upon completion.

        Returns:
            None
        """
        update_excel_frame = ctk.CTkFrame(self, fg_color='transparent')
        update_excel_frame.pack(anchor="center")

        self.update_excel_upon_completion_checkbox = ctk.CTkCheckBox(update_excel_frame, onvalue=True, offvalue=False,
                                                                   font=self._font, text="Update spreadsheet on completion",
                                                                   command=self._update_spreadsheet_on_completion)
        if self._values['update_spreadsheet_on_completion']:
            self.update_excel_upon_completion_checkbox.select()
        self.update_excel_upon_completion_checkbox.pack(side="left", padx=10, pady=(0, 10))

    def _browse_folder(self):
        """Opens a dialog to browse and select a folder, and updates the output path accordingly.

        Returns:
            None
        """
        folder_path = filedialog.askdirectory()
        if folder_path:
            new_path = f"{folder_path}/data.xlsx"
            update_config_field('config.json', 'csv_settings.excel_output_path', new_path)
            self.current_path_label.configure(text=new_path)

    def _update_spreadsheet_on_completion(self):
        """Updates the configuration to reflect whether the spreadsheet should be updated upon completion.

        Returns:
            None
        """
        checkbox_value = self.update_excel_upon_completion_checkbox.get()
        update_config_field('config.json', 'csv_settings.update_spreadsheet_on_completion', checkbox_value)
