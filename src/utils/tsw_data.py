import os
from pathlib import Path
from typing import Union, List, Dict

from shapely.geometry.point import Point

from src.config.constants import MS_TO_MPH


def get_dtg_comm_key() -> str:
    """
    Retrieves the DTG communication key from predefined file locations. This function checks
    a set of possible file paths for the communication key file. If the file exists at any
    of these locations, it reads and returns the key as a string. If the file is not found
    or any error occurs during the reading process, the function returns None.

    :raises Exception: If an error occurs while attempting to read from one of the files.
    :return: The communication key if found and successfully read
    :rtype: str
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
                raise f"Permission denied for {path}: {e}"

    raise FileNotFoundError("DTG communication key file not found")


def get_player_data(content) -> list[Union[str, float, int, Point]]:
    """
    Extracts and transforms player data from the provided content.

    This function processes a dictionary containing various player-related
    information and transforms it into a more accessible and structured
    format. The data includes details such as the current service name,
    maximum track speed, next speed limit, distance to the next speed
    limit, positional coordinates, current tile coordinates, track gradient,
    and geographical location (longitude and latitude).

    :param content: Dictionary containing player-related data with nested
        entries and values.
    :type content: dict
    :return: A list containing the processed player data, structured in the
        following order:
        - Current service name
        - Track maximum speed (converted to MPH)
        - Next speed limit (converted to MPH)
        - Distance to the next speed limit
        - X-coordinate of the next speed limit's position
        - Y-coordinate of the next speed limit's position
        - Current tile's X-coordinate
        - Current tile's Y-coordinate
        - Track gradient
        - Geographic point containing longitude and latitude
    :rtype: list
    """
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
    """
    Extracts AI data based on the provided time, list of vehicle IDs, and content data. The method
    processes the content to map vehicle IDs to their respective geographical points and object
    classes. It then combines this information with the provided time and returns the data as a
    structured list.

    :param ctime: The current time or a timestamp associated with the data.
    :type ctime: Any
    :param all_vehicles: A list of vehicle IDs to extract AI data for.
    :param content: A structured dictionary containing entries with vehicle-specific
        AI data such as geographical points and object classes.
    :return: A list of lists, where each inner list contains the time, vehicle ID,
        associated object class, and geographical point of a vehicle.
    :rtype: List[List[any]]
    """
    v_point = {
        x["Path"].split("Timetable/")[1].split(".LatLon")[0]: Point(x["Values"]["Lon"], x["Values"]["Lat"])
        for x in content["Entries"] if "Path" in x and x["Path"].endswith(".LatLon")
    }
    v_classes = {
        x["Path"].split("Timetable/")[1].split(".ObjectClass")[0]: x["Values"]["ObjectClass"]
        for x in content["Entries"] if "Path" in x and x["Path"].endswith(".ObjectClass")
    }
    return [[ctime, vid, v_classes[vid], v_point[vid]] for vid in all_vehicles]
