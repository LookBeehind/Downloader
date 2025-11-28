import customtkinter
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from config import SETTINGS_FILE, PLAYLISTS_FILE
from downloader import *

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("YouTube Video Downloader 3000")
        self.geometry("900x600")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.download_details = None
        self.warning = None
        self.extension_values = ['Default', "webm", "mp4"]

        self.load_side_bar()
        self.load_default_settings()
        self.create_main_frame()

    def load_side_bar(self):
        """Creates the sidebar on the left with settings controls"""
        # FIXED: Sidebar MUST be in column 0
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)  # Push things up if needed

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Set Defaults",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.format_select = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                         values=["Video + Audio", "Video", "Audio"],
                                                         command=self.update_extension_options)
        self.format_select.grid(row=1, column=0, padx=20, pady=10)

        self.extension = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                     values=self.extension_values,
                                                     command=self.get_selected_option)
        self.extension.grid(row=2, column=0, padx=20, pady=10)

        self.resolution = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                      values=['144', '240', '360', '480', '720', '1080', '1440',
                                                              '2160'],
                                                      command=self.get_selected_option)
        self.resolution.grid(row=3, column=0, padx=20, pady=10)

        self.path = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Output Path")
        self.path.grid(row=4, column=0, padx=20, pady=10)

        self.submit = customtkinter.CTkButton(self.sidebar_frame, text="Save Settings",
                                              command=self.save_default_settings)
        self.submit.grid(row=5, column=0, padx=20, pady=(20, 30))

    def create_main_frame(self):
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # --- GRID CONFIGURATION (Main Frame) ---
        self.main_frame.grid_columnconfigure(0, weight=1)  # Left
        self.main_frame.grid_columnconfigure(1, weight=1)  # Center
        self.main_frame.grid_columnconfigure(2, weight=1)  # Right

        # 1. Label
        self.logo_label = customtkinter.CTkLabel(self.main_frame, text="Enter your URL",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, columnspan=3, sticky='s', pady=(50, 20), padx=20)

        # 2. Entry
        self.entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="https://www.youtube.com/...")
        self.entry.grid(row=1, column=0, columnspan=3, sticky='ew', padx=40, pady=20)

        # 3. Bottom Controls
        try:
            with open(PLAYLISTS_FILE, 'r') as f:
                self.playlists = {line.strip().split(',')[0]: line.strip().split(',')[1] for line in f.readlines()}
        except FileNotFoundError:
            self.playlists = {}

        # A. Playlist Menu
        self.playlist_menu = customtkinter.CTkOptionMenu(self.main_frame,
                                                         values=list(self.playlists.keys()),
                                                         command=self.load_playlist)
        self.playlist_menu.grid(row=2, column=0, padx=(40, 10), pady=30, sticky='ew')

        # B. Switch
        self.set_properties = customtkinter.CTkSwitch(self.main_frame, text="Options", offvalue=0)
        self.set_properties.grid(row=2, column=1, padx=10, pady=30)

        # C. Download Button
        self.download = customtkinter.CTkButton(self.main_frame, text="Download", command=self.handle_download)
        self.download.grid(row=2, column=2, padx=(10, 40), pady=30, sticky='ew')

    def load_playlist(self, choice):
        self.entry.delete(0, 'end')
        self.entry.insert(0, self.playlists[choice])

    def handle_download(self):
        global url
        url = self.entry.get()

        if self.entry.get() == '':
            self.warning_popup()
        elif self.set_properties.get() != 0:
            self.select_details()
        else:
            download(
                url=self.entry.get(),
                path=self.path.get(),
                video_resolution=int(self.resolution.get() or 1080),
                form=self.format_select.get(),
                ext=self.extension.get()
            )

    def load_default_settings(self):
        try:
            tree = ET.parse(SETTINGS_FILE)
            root = tree.getroot()

            format_value = root.find("format").text
            extension_value = root.find("extension").text
            resolution_value = root.find("resolution").text
            output_folder_value = root.find("output_folder").text

            self.format_select.set(format_value)
            self.extension.set(extension_value)
            self.resolution.set(resolution_value)
            self.path.delete(0, "end")
            self.path.insert(0, output_folder_value)

        except (FileNotFoundError, AttributeError):
            pass

    def update_extension_options(self, choice):
        selected_option = self.get_selected_option(choice)
        if selected_option == 'Audio':
            self.extension_values = ['mp3']
            self.resolution.set('N/A')
            self.resolution.configure(state='disabled')
            self.extension.set('mp3')
        else:
            self.extension_values = ['Default', "webm", "mp4"]
            self.extension.set('Default')
            self.resolution.set('144')
            self.resolution.configure(state='enabled')

        self.extension.configure(values=self.extension_values)

    @staticmethod
    def get_selected_option(choice):
        return choice

    def save_default_settings(self):
        # Create an XML element tree
        root = ET.Element("settings")

        # Add selected options to the XML tree
        format_element = ET.SubElement(root, "format")
        format_element.text = self.format_select.get()

        extension_element = ET.SubElement(root, "extension")
        extension_element.text = self.extension.get()

        resolution_element = ET.SubElement(root, "resolution")
        resolution_element.text = self.resolution.get()

        path_value = self.path.get()

        # Set the default output folder to the download folder of the current user
        if not path_value:
            default_download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            path_element = ET.SubElement(root, "output_folder")
            path_element.text = default_download_folder
        else:
            path_element = ET.SubElement(root, "output_folder")
            path_element.text = path_value

        # Convert to a formatted string
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

        # Write the formatted string to an XML file
        with open(SETTINGS_FILE, "w") as xml_file:
            xml_file.write(xml_str)

        self.load_default_settings()

    def select_details(self):
        if self.download_details is None or not self.download_details.winfo_exists():
            self.download_details = DownloadDetails(self)
            self.download_details.grab_set()
        else:
            self.download_details.focus()

    def warning_popup(self):
        if self.warning is None or not self.warning.winfo_exists():
            self.warning = PopUp(self)
            self.warning.grab_set()
        else:
            self.warning.focus()


class DownloadDetails(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Parameters")
        self.extension_values = ['Default', "webm", "mp4"]
        self.logo_label = customtkinter.CTkLabel(self, text="Select the parameters",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.format_select = customtkinter.CTkOptionMenu(self,
                                                         values=["Video + Audio", "Video", "Audio"],
                                                         command=self.update_extension_options)
        self.format_select.grid(row=1, column=0, padx=20, pady=10)

        self.extension = customtkinter.CTkOptionMenu(self,
                                                     values=self.extension_values,
                                                     command=self.get_selected_option)
        self.extension.grid(row=2, column=0, padx=20, pady=10)

        self.resolution = customtkinter.CTkOptionMenu(self, values=[
            '144', '240', '360', '480', '720', '1080', '1440', '2160'
        ], command=self.get_selected_option)
        self.resolution.grid(row=3, column=0, padx=20, pady=10)

        self.path = customtkinter.CTkEntry(self, placeholder_text="Output Path")
        self.path.grid(row=4, column=0, columnspan=3, padx=20, pady=10)

        self.load_default_settings()

        self.submit = customtkinter.CTkButton(self, text="Download", command=self.handle_download)
        self.submit.grid(row=5, column=0, padx=20, pady=(20, 30))

    def handle_download(self):
        global url
        download(
            url=url,
            path=self.path.get(),
            video_resolution=int(self.resolution.get() or 0),
            ext=self.extension.get(),
            form=self.format_select.get()
        )
        self.destroy()

    def update_extension_options(self, choice):
        selected_option = self.get_selected_option(choice)
        if selected_option == 'Audio':
            self.extension_values = ['mp3']
            self.resolution.set('N/A')
            self.resolution.configure(state='disabled')
            self.extension.set('mp3')
        else:
            self.extension_values = ['Default', "webm", "mp4"]
            self.extension.set('Default')
            self.resolution.set('1080')
            self.resolution.configure(state='enabled')

        self.extension.configure(values=self.extension_values)

    @staticmethod
    def get_selected_option(choice):
        return choice

    def load_default_settings(self):
        try:
            tree = ET.parse(SETTINGS_FILE)
            root = tree.getroot()

            format_value = root.find("format").text
            extension_value = root.find("extension").text
            resolution_value = root.find("resolution").text
            output_folder_value = root.find("output_folder").text

            self.format_select.set(format_value)
            self.extension.set(extension_value)
            self.resolution.set(resolution_value)
            self.path.delete(0, "end")
            self.path.insert(0, output_folder_value)

        except FileNotFoundError:
            pass


class PopUp(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Warning")

        def destroy_this_window():
            self.destroy()

        self.logo_label = customtkinter.CTkLabel(self, text='Please fill up the URL')
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))

        btn = customtkinter.CTkButton(self, command=destroy_this_window, text='OK')
        btn.grid(padx=30, pady=10, row=1, column=0, sticky="ns", ipadx=15)
