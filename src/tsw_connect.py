from datetime import datetime
import time

from typing import List

import requests
import threading

from src.config.config import Config
from src.utils.gpkg_writer_utils import write_to_gpkg
from src.utils.tsw_data import get_player_data, get_ai_data
from utils.tsw_httpapi import get_subscription, setup_subscription, get_timetable
from src.utils.dashboard_gui import DashboardGUI


class TSWConnect:
    def __init__(self, config: Config, all_vehicles: List[str]) -> None:
        self.config = config
        self.all_vehicles = all_vehicles
        self.keep_running = threading.Event()
        self.data = {"player": [], "ai": []}

    @staticmethod
    def setup() -> "TSWConnect":
        config = Config.load()
        all_vehicles = get_timetable()
        setup_subscription(all_vehicles)
        return TSWConnect(config, all_vehicles)

    def _collection_loop(self, collection_interval_sec: float):
        """
        Background thread function to collect data.
        """
        print("Starting data collection loop...")
        while self.keep_running.is_set():
            try:
                content = get_subscription()
                # print(content)  # Optional: reduce console spam
                ctime = datetime.now()
                
                # Safely append data
                p_data = get_player_data(content)
                a_data = get_ai_data(ctime, self.all_vehicles, content)
                
                self.data["player"].append(p_data)
                self.data["ai"].extend(a_data)
                
                time.sleep(collection_interval_sec)
            except requests.exceptions.ConnectionError as e:
                # print(f"Connection Error: {e}")
                pass
            except requests.exceptions.HTTPError as e:
                # print(f"HTTP Error: {e}")
                pass

        print("Collection loop finished.")

    def run(self, collection_interval_sec: float = 0.5) -> None:
        """
        Runs the data collection process in a separate thread and initializes the GUI for
        progress updates. This function handles setting up necessary threads, running the
        GUI, and saving collected data into files after the process is complete.

        :param collection_interval_sec: Interval (in seconds) at which data is collected
                                        in the background thread. By default, this is set
                                        to 0.5 seconds.
        :return: This function does not return a value.
        """
        self.keep_running.set()
        self.data = {"player": [], "ai": []}
        start_time = datetime.now()

        # Start collection in background thread
        collection_thread = threading.Thread(
            target=self._collection_loop, 
            args=(collection_interval_sec,), 
            daemon=True
        )
        collection_thread.start()

        # GUI Setup (Main Thread)
        def stop_callback():
            self.keep_running.clear()

        gui = DashboardGUI(self.data, stop_callback, start_time)
        gui.run()

        print("Waiting for collection thread to join...")
        collection_thread.join(timeout=2.0)

        print("Saving data...")
        write_to_gpkg(self.config.data.get("player"), self.data.get("player"))
        write_to_gpkg(self.config.data.get("ai"), self.data.get("ai"))

        print("DONE!")


if __name__ == "__main__":
    tswc = TSWConnect.setup()
    tswc.run()
