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

    # Add track to Spotify playlist FIRST
    playlist_id = os.getenv("PLAYLIST_ID")
    try:
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
            print(f"Successfully added track to Spotify playlist: {track_name}", flush=True)
            
            # Only add to database if Spotify API succeeded
            if not db_add_track(uri, track_name):
                print(f"Warning: Track added to Spotify but failed to save in DB: {track_name}", file=sys.stderr, flush=True)
                # Still return success since it's in Spotify
            
            return {"success": True, "status": "added"}
        else:
            error_msg = f"Spotify API error: {response.status_code} - {response.text}"
            print(error_msg, file=sys.stderr, flush=True)
            return {"error": error_msg, "status": "spotify_error"}
    except Exception as e:
        error_msg = f"Exception adding track to Spotify: {str(e)}"
        print(error_msg, file=sys.stderr, flush=True)
        return {"error": error_msg, "status": "spotify_error"}
