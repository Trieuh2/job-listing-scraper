import threading
import customtkinter as ctk
from typing import List

from .utils_wrapper import update_config_field

class ExcludedKeywordsFrame(ctk.CTkFrame):
    """A frame for configuring the excluded keywords that filter job results from the Excel file output.

    Search results will be filtered from the Excel file output if the job title contains words mentioned in the filter list.

    Attributes:
        _values (list): A list of initial keyword values to be displayed.
        _update_timer (threading.Timer): A timer used for scheduling updates to the configuration file.
        _update_delay (float): The delay in seconds before updating the configuration file.
        filter_frame (customtkinter.CTkFrame): The frame that contains the filter list.
        keywords_text_box (customtkinter.CTkTextbox): The text box for entering excluded keywords.
    """

    def __init__(self, master: ctk.CTk, font: ctk.CTkFont, values:List[str]):
        """
        Initializes the ExcludedKeywordsFrame.

        Args:
            master (customtkinter.CTk): The parent widget.
            font (customtkinter.CTkFont): The font used for the text elements in the frame.
            values (List[str]): A list of initial keyword values to be displayed.

        Returns:
            None
        """
        super().__init__(master)
        self._values = values
        self._update_timer = None
        self._update_delay = 0.25

        self._create_title_label(font)
        self._create_keywords_text_box(font)
        self._create_filter_description_frame(font)
        self._bind_events()

    def _create_title_label(self, font: ctk.CTkFont):
        """
        Creates the title label for the frame.

        Args:
            font (customtkinter.CTkFont): The font used for the text elements in the frame.

        Returns:
            None
        """
        title_label = ctk.CTkLabel(self, text='Excluded Keywords', font=(font, 18))
        title_label.pack(pady=(10, 20))

    def _create_keywords_text_box(self, font: ctk.CTkFont):
        """
        Creates the text box for entering excluded keywords.

        Args:
            font (customtkinter.CTkFont): The font used for the text elements in the frame.

        Returns:
            None
        """
        self._create_filter_frame(font)
        self.keywords_text_box = ctk.CTkTextbox(self.filter_frame, font=font)
        self.keywords_text_box.insert(index='1.0', text="\n".join(self._values))
        self.keywords_text_box.pack(padx=10, pady=(0, 10))

    def _create_filter_frame(self, font: ctk.CTkFont):
        """
        Creates the frame for the filter list.

        Args:
            font (customtkinter.CTkFont): The font used for the text elements in the frame.

        Returns:
            None
        """
        self.filter_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.filter_frame.pack(side='left', padx=10, pady=(0, 10))
        filter_title = ctk.CTkLabel(self.filter_frame, text='Filter List', font=font)
        filter_title.pack()

    def _create_filter_description_frame(self, font: ctk.CTkFont):
        """
        Creates the frame for the filter description.

        Args:
            font (customtkinter.CTkFont): The font used for the text elements in the frame.

        Returns:
            None
        """
        filter_description_frame = ctk.CTkFrame(self, fg_color='transparent')
        filter_description_frame.pack(anchor='center')
        self._create_description_label(font, filter_description_frame)

    def _create_description_label(self, font: ctk.CTkFont, parent_frame: ctk.CTkFrame):
        """
        Creates the description label.

        Args:
            font (customtkinter.CTkFont): The font used for the text elements in the frame.
            parent_frame (customtkinter.CTkFrame): The parent frame for the description label.

        Returns:
            None
        """
        description = ('New scrape results will exclude any job titles that contain any of the excluded keywords.\n\n'
                       'Previously scraped data will not be deleted if a record contains keywords in the filter list.')
        description_label = ctk.CTkLabel(parent_frame, fg_color='transparent', text=description, font=font,
                                         justify="left", wraplength=400)
        description_label.pack(side='left', padx=10, pady=(0, 10))

    def _bind_events(self):
        """
        Binds events to the keywords text box.

        Returns:
            None
        """
        self.keywords_text_box.bind('<KeyRelease>', self._schedule_update)

    def _schedule_update(self, event):
        """
        Schedules an update of the configuration file after a delay.

        Args:
            event: The event that triggered the update scheduling.

        Returns:
            None
        """
        if self._update_timer:
            self._update_timer.cancel()
        self._update_timer = threading.Timer(self._update_delay, self._update_config)
        self._update_timer.start()

    def _update_config(self):
        """
        Updates the configuration file with the new excluded keywords.

        Returns:
            None
        """
        updated_keywords = self.keywords_text_box.get('1.0', 'end-1c').split('\n')
        update_config_field('config.json', 'excluded_keywords', updated_keywords)
