from typing import Dict

import requests

from src.utils.tsw_data import get_dtg_comm_key


def get_header() -> Dict[str, str]:
    """
    Retrieves a dictionary that contains the communication key header.

    This function retrieves a specific communication key and returns it
    as a dictionary where the key is "DTGCommKey". This is typically used
    for setting headers in communication protocols requiring authentication
    or identification.

    :return: A dictionary containing the communication key header.
    :rtype: Dict[str, str]
    """
    return {"DTGCommKey": get_dtg_comm_key()}


def send_request(url) -> requests.Response:
    """
    Sends an HTTP GET request to the specified URL with predefined headers and timeout.

    This function uses the `requests` library to send a GET request to the provided URL.
    It adds custom headers using a helper function and enforces a timeout for the request.
    In case of an HTTP error, the function raises an exception.

    :param url: The URL to which the GET request should be sent.
    :type url: str
    :return: The HTTP response object from the GET request.
    :rtype: requests.Response
    :raises requests.RequestException: If there is an issue with the HTTP request.
    """
    response = requests.get(url, headers=get_header(), timeout=10)
    response.raise_for_status()
    return response
