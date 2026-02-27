"""_summary_
    """
import os
import requests


def get_playlist(oauth2: str, playlist_id: str):
    """_summary_

    Args:
        oauth2 (str): _description_
        playlist_id (str): _description_

    Returns:
        _type_: _description_
    """
    tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
    params = {"fields": "next,items(item(uri))", "limit": 12}

    while url is not None:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {oauth2}"},
            params=params,
            timeout=1
        )
        data = response.json()
        print(data)

        tracks += [item["item"]["uri"]
                   for item in data["items"] if item.get("item") is not None]

        url = data["next"]
        params = None

    if not tracks:
        return IndexError("There are no tracks in this playlist!")

    return tracks


def add_track(oauth2: str, uri: str):
    """_summary_

    Args:
        oauth2 (str): _description_

    Returns:
        _type_: _description_
    """
    playlist_id = os.getenv("PLAYLIST_ID")

    playlist_tracks = get_playlist(oauth2, playlist_id)

    if uri in playlist_tracks:
        return ValueError("This track is already in the playlist!")

    response = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/items",
        headers={"Authorization": f"Bearer {oauth2}"},
        json={
            "uris": [
                uri
            ],
            "position": 0
        },
        timeout=5
    )
    return response
