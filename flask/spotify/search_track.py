"""_summary_

    Returns:
        _type_: _description_
    """

import requests
from requests.exceptions import ReadTimeout, RequestException

def search(query: str, token: str):
    """_summary_

    Args:
        query (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": query, "type": "track", "limit": 10},
            timeout=1
        )
        response.raise_for_status()
        return response.json()
    except ReadTimeout:
        raise RuntimeError("Spotify API timed out. Please try again.")
    except RequestException as e:
        raise RuntimeError(f"Spotify API error: {e}")
