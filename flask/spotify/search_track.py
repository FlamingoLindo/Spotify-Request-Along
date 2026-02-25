"""_summary_

    Returns:
        _type_: _description_
    """

import requests


def search(query: str, token: str):
    """_summary_

    Args:
        query (_type_): _description_

    Returns:
        _type_: _description_
    """
    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "type": "track", "limit": 10},
        timeout=1
    )
    return response.json()
