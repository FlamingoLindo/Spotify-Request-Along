"""_summary_
    """

import requests


def available_devices(oauth2: str):
    """_summary_

    Returns:
        _type_: _description_
    """
    response = requests.get(
        "https://api.spotify.com/v1/me/player/devices",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=1
    )
    devices = [device["id"] for device in response.json()["devices"]]

    if not devices:
        raise ConnectionError("No connected device!")

    return devices
