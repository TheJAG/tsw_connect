import json
import requests

from typing import Dict, List, Any

from src.config.constants import SUBSCRIPTION_ID
from src.utils.request_utils import send_request, get_header


def get_player_info() -> Dict:
    """
    Fetches and returns the player information from the specified server endpoint.

    This function sends a request to a local server endpoint to retrieve player
    information. The response is decoded from JSON format and then returned
    as a Python object.

    :return: A Python object representation of the player information
        retrieved from the server.
    :rtype: dict
    """
    url = "http://127.0.0.1:31270/get/DriverAid.PlayerInfo"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return content


def get_speed_limits() -> Dict:
    """
    Fetches the speed limits data from the DriverAid service.

    This function sends a request to a local endpoint to retrieve speed limits data,
    parses the response from JSON format to Python dictionary, and returns the
    content.

    :return: Parsed JSON response containing the speed limits data.
    :rtype: dict
    """
    url = "http://127.0.0.1:31270/get/DriverAid.Data"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return content


def get_timetable() -> list[Any]:
    """
    Fetches and processes the timetable data from a predefined URL.

    The function sends an HTTP GET request to a designated URL to retrieve
    JSON-encoded timetable data, decodes the response, and extracts the names
    of all vehicles listed in the timetable. It returns this list of vehicle
    names as the result.

    :raises RuntimeError: When the HTTP request fails or the response data cannot
        be decoded properly.
    :raises KeyError: If the expected keys ("Nodes" or "Name") do not exist
        in the response data.
    :raises TypeError: If the extracted data is not in the expected format.

    :return: A list containing the names of the vehicles listed in the timetable.
    :rtype: list[Any]
    """
    url = "http://127.0.0.1:31270/list/Timetable"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return [vehicle["Name"] for vehicle in content["Nodes"]]


def get_lat_long(vehicle_id: str) -> List[float]:
    """
    Retrieve the latitude and longitude of a vehicle.

    This function fetches the latitude and longitude of a vehicle by its ID
    from a remote server. It constructs the request URL using the given
    vehicle ID, sends the request, processes the response, and returns the
    location as a list containing the longitude and latitude.

    :param vehicle_id: The unique identifier of the vehicle whose
        latitude and longitude are to be retrieved.
    :type vehicle_id: str
    :return: A list where the first element is the longitude and the second
        is the latitude of the vehicle's current location.
    :rtype: List[float]
    """
    url = f"http://127.0.0.1:31270/get/Timetable/{vehicle_id}.LatLon"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return [content["Values"]["Lon"], content["Values"]["Lat"]]


def get_vehicle_info(vehicle_id: str) -> str:
    """
    Retrieves the object class of a vehicle based on its ID.

    This function constructs a URL using the `vehicle_id` and sends a request
    to an external service to obtain timetable-related information about the
    specified vehicle. It processes the response and extracts the object's
    class from the returned JSON payload.

    :param vehicle_id: The unique identifier for the vehicle.
    :type vehicle_id: str
    :return: The object class of the vehicle.
    :rtype: str
    """
    url = f"http://127.0.0.1:31270/get/Timetable/{vehicle_id}.ObjectClass"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return content["Values"]["ObjectClass"]


def subscription_urls(all_vehicles: List[str]) -> List[str]:
    """
    Generates a list of subscription URLs for the provided vehicle identifiers. The generated URLs
    include predefined static URLs and dynamically constructed URLs for each vehicle in the input
    list. Static URLs are related to "DriverAid" subscriptions, while dynamic URLs pertain to
    timetable subscriptions for specific vehicles.

    :param all_vehicles: A list of vehicle identifiers used to construct specific subscription URLs
    :return: A list of subscription URLs derived from static configurations and the provided vehicle identifiers
    :rtype: List[str]
    """
    object_class_urls = [
        f"http://127.0.0.1:31270/subscription/Timetable/{vehicle_id}.ObjectClass?Subscription={SUBSCRIPTION_ID}"
        for vehicle_id in all_vehicles
    ]
    lat_long_urls = [
        f"http://127.0.0.1:31270/subscription/Timetable/{vehicle_id}.LatLon?Subscription={SUBSCRIPTION_ID}"
        for vehicle_id in all_vehicles
    ]
    return [
        f"http://127.0.0.1:31270/subscription/DriverAid.PlayerInfo?Subscription={SUBSCRIPTION_ID}",
        f"http://127.0.0.1:31270/subscription/DriverAid.Data?Subscription={SUBSCRIPTION_ID}"
    ] + object_class_urls + lat_long_urls


def setup_subscription(all_vehicles: List[str]):
    """
    Sets up subscriptions for a list of vehicles by sending post requests to the
    generated URLs. Retries connection errors and logs progress, ensuring all
    requests are completed before concluding.

    :param all_vehicles: List of vehicle identifiers for which subscriptions
                         are being setup.
    :type all_vehicles: List[str]
    :return: None
    """
    print("Setting up subscription ", end="")
    urls = subscription_urls(all_vehicles)

    idx = 0
    while idx < len(urls):
        try:
            response = requests.post(urls[idx], headers=get_header(), timeout=10)
            response.raise_for_status()
            idx += 1
        except requests.exceptions.ConnectionError as e:
            print(".", end="")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")

    print(", done!")


def get_subscription() -> Dict:
    """
    Fetches subscription details based on the provided subscription ID.

    This function constructs a URL using a subscription ID and sends an HTTP request
    to fetch subscription details. The response is decoded from JSON format and returned
    as a Python object.

    :return: The subscription details decoded from JSON response
    :rtype: dict
    """
    url = f"http://127.0.0.1:31270/subscription/?Subscription={SUBSCRIPTION_ID}"
    content = json.loads(send_request(url).content.decode("utf-8"))
    return content
