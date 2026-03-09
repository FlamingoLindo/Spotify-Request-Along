"""_summary_
    """

import sys
import requests


def play_new_track(context_uri: str, device_id: str, oauth2: str):
    """Play a new track on the specified device.

    Args:
        context_uri (str): Spotify track URI
        device_id (str): Target device ID
        oauth2 (str): OAuth2 token

    Returns:
        Response: API response
    """
    response = requests.put(
        "https://api.spotify.com/v1/me/player/play",
        headers={"Authorization": f"Bearer {oauth2}"},
        params={"device_id": device_id},
        json={
            "uris": [context_uri],
            "position_ms": 0
        },
        timeout=10
    )
    
    if response.status_code == 429:
        print(f"Rate limited on play_new_track", file=sys.stderr, flush=True)
        response.raise_for_status()  # Will raise HTTPError with 429
    
    return response


def pause_track(oauth2: str):
    """_summary_

    Args:
        device_id (str): _description_
        oauth2 (str): _description_
    """
    response = requests.put(
        "https://api.spotify.com/v1/me/player/pause",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=10
    )
    return response


def skip_track(oauth2: str):
    """_summary_

    Args:
        device_id (str): _description_
        oauth2 (str): _description_
    """
    response = requests.post(
        "https://api.spotify.com/v1/me/player/next",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=10
    )
    return response


def previous_track(oauth2: str):
    """_summary_

    Args:
        device_id (str): _description_
        oauth2 (str): _description_
    """
    response = requests.post(
        "https://api.spotify.com/v1/me/player/previous",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=10
    )
    return response
