"""_summary_
    """
import os
import sys
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
    """Add a track to Spotify playlist first, then to database if successful.

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

    playlist_id = os.getenv("PLAYLIST_ID")
    
    # Simple request - no retries, just like the original
    response = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/items",
        headers={"Authorization": f"Bearer {oauth2}"},
        json={"uris": [uri], "position": 0},
        timeout=10
    )
    
    # Handle response
    if response.status_code in [200, 201]:
        print(f"Successfully added track to Spotify playlist: {track_name}", flush=True)
        db_add_track(uri, track_name)
        return {"success": True, "status": "added"}
    elif response.status_code == 429:
        print(f"Rate limited on playlist add. Retry-After: {response.headers.get('Retry-After', 'N/A')}", file=sys.stderr, flush=True)
        return {"error": "Rate limited", "status": "rate_limited"}
    else:
        print(f"Spotify API error: {response.status_code}", file=sys.stderr, flush=True)
        return {"error": f"Spotify API error: {response.status_code}", "status": "spotify_error"}
