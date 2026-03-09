"""_summary_
    """
import sys
import requests


def get_queue(oauth2: str):
    """Get the current playback queue.

    Args:
        oauth2 (str): OAuth2 token

    Returns:
        dict or list: Queue data or empty list if nothing playing
    """
    response = requests.get(
        "https://api.spotify.com/v1/me/player/queue",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=10
    )
    
    if response.status_code == 429:
        print(f"Rate limited on get_queue", file=sys.stderr, flush=True)
        response.raise_for_status()  # Will raise HTTPError with 429
    
    response.raise_for_status()
    data = response.json()

    if data.get('currently_playing') is None:
        return []

    return data


def add_to_the_queue(oauth2: str, uri: str, device_id: str):
    """Add a track to the playback queue.

    Args:
        oauth2 (str): OAuth2 token
        uri (str): Spotify track URI
        device_id (str): Target device ID

    Returns:
        Response: API response
    """
    response = requests.post(
        "https://api.spotify.com/v1/me/player/queue",
        headers={"Authorization": f"Bearer {oauth2}"},
        params={
            "uri": uri,
            "device_id": device_id
        },
        timeout=10
    )
    
    if response.status_code == 429:
        print(f"Rate limited on add_to_queue", file=sys.stderr, flush=True)
        response.raise_for_status()  # Will raise HTTPError with 429
    
    return response
