import json
import os
from pathlib import Path

import requests

from shapely import Point
from typing import Dict, List, Optional

MS_TO_MPH = 2.236936363826430  # consider moving to constants library
SUBSCRIPTION_ID = 1


def get_dtg_comm_key() -> Optional[str]:
    """
    Retrieves the DTG communication key from predefined file locations. This function checks
    a set of possible file paths for the communication key file. If the file exists at any
    of these locations, it reads and returns the key as a string. If the file is not found
    or any error occurs during the reading process, the function returns None.

    :raises Exception: If an error occurs while attempting to read from one of the files.
    :return: The communication key if found and successfully read, otherwise None.
    :rtype: Optional[str]
    """
    # Common locations for the key file
    possible_paths = [
        Path(os.path.expanduser("~/Documents/My Games/TrainSimWorld6/Saved/Config/CommAPIKey.txt")),
        Path(os.path.expanduser("~/OneDrive/Documenten/My Games/TrainSimWorld6/Saved/Config/CommAPIKey.txt")),
        Path(os.path.expanduser("~/OneDrive/Documents/My Games/TrainSimWorld6/Saved/Config/CommAPIKey.txt")),
    ]

    for path in possible_paths:
        if path.exists():
            try:
                return path.read_text(encoding="utf-8").strip()
            except FileNotFoundError:
                continue  # Edge case for race conditions, try next path
            except PermissionError as e:
                print(f"Permission denied for {path}: {e}")

    return None


def get_header() -> Dict[str, str]:
    return {"DTGCommKey": get_dtg_comm_key()}


def send_request(url) -> requests.Response:
    """
    Sends a GET request to the DriverAid.Data endpoint with the required DTGCommKey header.
    Returns the Response object. Raises HTTPError for bad responses.
    """
    response = requests.get(url, headers=get_header(), timeout=10)
    response.raise_for_status()
    return response


def get_player_info():
    url = "http://127.0.0.1:31270/get/DriverAid.PlayerInfo"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return content


def get_speed_limits():
    url = "http://127.0.0.1:31270/get/DriverAid.Data"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return content


def get_timetable():
    url = "http://127.0.0.1:31270/list/Timetable"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return [vehicle["Name"] for vehicle in content["Nodes"]]


def get_lat_long(vehicle_id):
    url = f"http://127.0.0.1:31270/get/Timetable/{vehicle_id}.LatLon"
    content = json.loads(send_request(url).content.decode("utf-8"))
    print(content)
    return ""


def get_vehicle_info(vehicle_id):
    url = f"http://127.0.0.1:31270/get/Timetable/{vehicle_id}.ObjectClass"
    content = json.loads(send_request(url).content.decode("utf-8"))
    print(content)
    return ""


def setup_subscription(all_vehicles: List[str]):
    object_class_urls = [
        f"http://127.0.0.1:31270/subscription/Timetable/{vehicle_id}.ObjectClass?Subscription={SUBSCRIPTION_ID}"
        for vehicle_id in all_vehicles
    ]
    lat_long_urls = [
        f"http://127.0.0.1:31270/subscription/Timetable/{vehicle_id}.LatLon?Subscription={SUBSCRIPTION_ID}"
        for vehicle_id in all_vehicles
    ]
    urls = [
        f"http://127.0.0.1:31270/subscription/DriverAid.PlayerInfo?Subscription={SUBSCRIPTION_ID}",
        f"http://127.0.0.1:31270/subscription/DriverAid.Data?Subscription={SUBSCRIPTION_ID}"
    ] + object_class_urls + lat_long_urls

    print("Setting up subscription ", end="")

    idx = 0
    while idx < len(urls):
        try:
            response = requests.post(urls[idx], headers=get_header(), timeout=10)
            response.raise_for_status()
            idx += 1
        except Exception:
            print(".", end="")

    print(", done!")


def get_subscription():
    url = f"http://127.0.0.1:31270/subscription/?Subscription={SUBSCRIPTION_ID}"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return content


def get_player_data(content):
    return [
        content["Entries"][0]["Values"]["currentServiceName"],
        content["Entries"][1]["Values"]["trackMaxSpeed"]["value"] * MS_TO_MPH,
        content["Entries"][1]["Values"]["nextSpeedLimit"]["value"] * MS_TO_MPH,
        content["Entries"][1]["Values"]["distanceToNextSpeedLimit"],
        content["Entries"][1]["Values"]["nextSpeedLimitPosition"]["x"],
        content["Entries"][1]["Values"]["nextSpeedLimitPosition"]["y"],
        content["Entries"][0]["Values"]["currentTile"]["x"],
        content["Entries"][0]["Values"]["currentTile"]["y"],
        content["Entries"][1]["Values"]["gradient"],
        Point(
            content["Entries"][0]["Values"]["geoLocation"]["longitude"],
            content["Entries"][0]["Values"]["geoLocation"]["latitude"]
        ),
    ]


def get_ai_data(ctime, all_vehicles: List[str], content: Dict[str, any]) -> List[List[any]]:
    v_point = {
        x["Path"].split("Timetable/")[1].split(".LatLon")[0]: Point(x["Values"]["Lon"], x["Values"]["Lat"])
        for x in content["Entries"] if "Path" in x and x["Path"].endswith(".LatLon")
    }
    v_classes = {
        x["Path"].split("Timetable/")[1].split(".ObjectClass")[0]: x["Values"]["ObjectClass"]
        for x in content["Entries"] if "Path" in x and x["Path"].endswith(".ObjectClass")
    }
    return [[ctime, vid, v_classes[vid], v_point[vid]] for vid in all_vehicles]
