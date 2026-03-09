"""_summary_
    """

import requests


def available_devices(oauth2: str):
    """Get the first available Spotify device.

    Returns:
        str: Device ID of the first available device
    """
    response = requests.get(
        "https://api.spotify.com/v1/me/player/devices",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=10
    )
    
    if response.status_code == 429:
        raise ConnectionError("Spotify rate limit exceeded. Please wait a moment.")
    
    devices = [device["id"] for device in response.json().get("devices", [])]

    if not devices:
        raise ConnectionError("No connected device!")

    return devices[0]  # Return first device ID directly
