from datetime import datetime
import time

from typing import List

import requests
import threading
from tkinter import messagebox
import tkinter as tk

import geopandas as gpd
import pandas as pd

from utils.tsw_httpapi import get_subscription, setup_subscription, get_player_data, get_timetable, get_ai_data

all_vehicles = get_timetable()
setup_subscription(all_vehicles)
player_data = []
ai_data = []

# Flag to control the loop
keep_running = threading.Event()
keep_running.set()  # Start as True


def show_cancel_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    result = messagebox.askokcancel("Running", "Click Cancel to stop the loop")
    if not result:
        keep_running.clear()  # Stop the loop
    root.destroy()


def write_to_gpkg(data: List[any], cols: List[str], file_name: str) -> None:
    df = pd.DataFrame(data, columns=cols)
    gdf = gpd.GeoDataFrame(data=df, geometry=df.geometry, crs="EPSG:4326")
    gdf.to_file(file_name, driver="GPKG")


# Start the messagebox in a background thread
dialog_thread = threading.Thread(target=show_cancel_dialog, daemon=True)
dialog_thread.start()

while keep_running.is_set():
    try:
        content = get_subscription()
        ctime = datetime.now()
        player_data.append(get_player_data(content))
        ai_data.extend(get_ai_data(ctime, all_vehicles, content))
        print(content)
        time.sleep(0.1)
    except requests.exceptions.ConnectionError as e:
        print(f"Error: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")

print("Loop stopped by user")

player_filename = r"c:\Projects\tsw3 route maps\_dev\player_data.gpkg"
ai_filename = r"c:\Projects\tsw3 route maps\_dev\ai_data.gpkg"

player_cols = [
    "current_service_name",
    "max_speed",
    "next_speed_limit",
    "next_speed_limit_distance",
    "next_speed_limit_x",
    "next_speed_limit_y",
    "current_tile_x",
    "current_tile_y",
    "gradient",
    "geometry"
]
ai_cols = ["ctime", "vehicle_id", "vehicle_class", "geometry"]

write_to_gpkg(player_data, player_cols, player_filename)
write_to_gpkg(ai_data, ai_cols, ai_filename)

print("DONE!")
