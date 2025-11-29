from datetime import datetime
import time

from typing import List

import requests
import threading
from tkinter import messagebox
import tkinter as tk

from src.config.config import Config
from src.utils.gpkg_writer_utils import write_to_gpkg
from src.utils.tsw_data import get_player_data, get_ai_data
from utils.tsw_httpapi import get_subscription, setup_subscription, get_timetable


class TSWConnect:
    def __init__(self, config: Config, all_vehicles: List[str]) -> None:
        """
        Initializes a new instance of the TSWConnect class.

        This constructor sets up the initial state for the class, including
        configuration settings and the list of all vehicles. Additionally,
        it initializes an event to handle the running state.

        :param config: Configuration settings for the class instance.
        :type config: Any
        :param all_vehicles: A list of all vehicle identifiers.
        :type all_vehicles: List[str]
        """
        self.config = config
        self.all_vehicles = all_vehicles
        self.keep_running = threading.Event()

    @staticmethod
    def setup() -> "TSWConnect":
        """
        Sets up the TSWConnect instance by loading configuration, fetching vehicle
        data, and initializing necessary subscriptions.

        :staticmethod:

        :return: A new instance of TSWConnect configured with all loaded
                 vehicles and configuration.
        :rtype: TSWConnect
        """
        config = Config.load()
        all_vehicles = get_timetable()
        setup_subscription(all_vehicles)
        return TSWConnect(config, all_vehicles)

    def show_cancel_dialog(self) -> None:
        """
        Displays a cancel dialog box that allows the user to stop a running loop
        by clicking the "Cancel" option. The method will halt the loop
        execution if "Cancel" is selected.

        :return: None
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        result = messagebox.askokcancel("Running", "Click Cancel to stop the loop")
        if not result:
            self.keep_running.clear()  # Stop the loop
        root.destroy()

    def run(self, collection_interval_sec: float = 0.5) -> None:
        """
        Executes a data collection loop that retrieves player and AI data at regular intervals until stopped.
        The method spawns a thread for handling cancel dialog interactions and uses an event flag to manage the loop's execution state.
        It also saves gathered data into GeoPackage files once the loop is terminated.

        :param collection_interval_sec: Interval in seconds between consecutive data collection operations. Defaults to 0.5.
        :return: This function does not return a value. It does however write collected data to GeoPackage files.
        """
        data = {"player": [], "ai": []}
        self.keep_running.set()  # Initialise as True

        dialog_thread = threading.Thread(target=self.show_cancel_dialog, daemon=True)
        dialog_thread.start()

        while self.keep_running.is_set():
            try:
                content = get_subscription()
                print(content)
                ctime = datetime.now()
                data["player"].append(get_player_data(content))
                data["ai"].extend(get_ai_data(ctime, self.all_vehicles, content))
                time.sleep(collection_interval_sec)
            except requests.exceptions.ConnectionError as e:
                print(f"Error: {e}")
            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error: {e}")

        print("Loop stopped by user")

        write_to_gpkg(self.config.data.get("player"), data.get("player"))
        write_to_gpkg(self.config.data.get("ai"), data.get("ai"))

        print("DONE!")


if __name__ == "__main__":
    tswc = TSWConnect.setup()
    tswc.run()
