"""_summary_
    """
import requests


def get_queue(oauth2: str):
    """_summary_

    Args:
        oauth2 (str): _description_

    Returns:
        _type_: _description_
    """
    response = requests.get(
        "https://api.spotify.com/v1/me/player/queue",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=1
    )
    response.raise_for_status()
    data = response.json()

    if data['currently_playing'] is None:
        return []

    return data


def add_to_the_queue(oauth2: str, uri: str, device_id: str):
    """_summary_

    Args:
        oauth2 (str): _description_
        uri (str): _description_
        device_id (str): _description_

    Returns:
        _type_: _description_
    """
    response = requests.post(
        "https://api.spotify.com/v1/me/player/queue",
        headers={"Authorization": f"Bearer {oauth2}"},
        params={
            "uri": uri,
            "device_id": device_id
        },
        timeout=5
    )
    return response
