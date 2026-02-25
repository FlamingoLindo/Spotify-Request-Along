"""_summary_
    """
from enum import Enum
import os

from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests
from dotenv import load_dotenv
load_dotenv()


class UseType(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_
    """
    OAUTH2 = "oauth2"
    OTHER = "other"


def load_client_vars(usage: UseType):
    """_summary_

    Args:
        usage (UseType): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    match usage:
        case UseType.OAUTH2:
            callback_url = os.getenv("CALLBACK_URL")
            auth_url = os.getenv("AUTH_URL")
            access_token_url = os.getenv("ACCESS_TOKEN_URL")
            return client_id, client_secret, callback_url, auth_url, access_token_url

        case UseType.OTHER:
            return client_id, client_secret
        case _:
            raise ValueError(f"Unknown usage case: {usage}")


def get_token():
    """_summary_

    Returns:
        _type_: _description_
    """
    client_id, client_secret = load_client_vars(UseType.OTHER)[:2]
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=1
    )
    return response.json()["access_token"]


def get_oauth2_url():
    """Generate OAuth2 authorization URL
    Returns:
        str: Authorization URL for user to visit
    """
    client_id, _, callback_url, auth_url, _ = load_client_vars(UseType.OAUTH2)
    scope = [
        "user-read-private",
        "user-read-email",
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "playlist-modify-public",
        "playlist-modify-private",
        "playlist-read-private"
    ]
    spotify = OAuth2Session(client_id, scope=scope, redirect_uri=callback_url)
    authorization_url, _state = spotify.authorization_url(auth_url)
    return authorization_url


def exchange_code_for_token(redirect_response):
    """Exchange authorization code for access token
    Args:
        redirect_response (str): Full redirect URL from Spotify
    Returns:
        str: Access token
    """
    client_id, client_secret, callback_url, _, access_token_url = load_client_vars(
        UseType.OAUTH2)
    scope = [
        "user-read-private",
        "user-read-email",
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "playlist-modify-public",
        "playlist-modify-private",
        "playlist-read-private"
    ]
    spotify = OAuth2Session(client_id, scope=scope, redirect_uri=callback_url)
    auth = HTTPBasicAuth(client_id, client_secret)
    token = spotify.fetch_token(access_token_url, auth=auth,
                                authorization_response=redirect_response)
    return token["access_token"]
