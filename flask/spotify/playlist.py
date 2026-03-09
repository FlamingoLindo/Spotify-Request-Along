"""_summary_
    """
import os
import requests
from db.db_add_track import track_exists_in_db, db_add_track


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
            timeout=10
        )
        data = response.json()
        print(data)

        tracks += [item["item"]["uri"]
                   for item in data["items"] if item.get("item") is not None]

        url = data["next"]
        params = None

    if not tracks:
        return []

    return tracks


def add_track(oauth2: str, uri: str, track_name: str):
    """Add a track to the database and Spotify playlist if not already present.

    Args:
        oauth2 (str): Spotify OAuth2 token
        uri (str): Spotify track URI
        track_name (str): Name of the track

    Returns:
        dict: Response with success status and message
    """
    # Check if track exists in database
    if track_exists_in_db(uri):
        return {"error": "This track is already in the playlist!", "status": "duplicate"}

    # Add track to database
    if not db_add_track(uri, track_name):
        return {"error": "Failed to add track to database", "status": "db_error"}

    # Add track to Spotify playlist
    playlist_id = os.getenv("PLAYLIST_ID")
    response = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/items",
        headers={"Authorization": f"Bearer {oauth2}"},
        json={
            "uris": [
                uri
            ],
            "position": 0
        },
        timeout=10
    )
    
    if response.status_code in [200, 201]:
        return {"success": True, "status": "added"}
    else:
        return {"error": "Failed to add track to Spotify playlist", "status": "spotify_error"}
