"""_summary_
    """

import os
import redis
import requests

# Redis client for caching
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

DEVICE_CACHE_KEY = "spotify_device_id"
DEVICE_CACHE_TTL = 10800  # 3 hours in seconds


def available_devices(oauth2: str, force_refresh: bool = False):
    """Get the first available Spotify device with Redis caching.
    
    Args:
        oauth2 (str): OAuth2 token
        force_refresh (bool): Force refresh from API instead of using cache

    Returns:
        str: Device ID of the first available device
    """
    # Check cache first unless force refresh
    if not force_refresh:
        cached_device = redis_client.get(DEVICE_CACHE_KEY)
        if cached_device:
            print(f"Using cached device ID: {cached_device}", flush=True)
            return cached_device
    
    # Fetch from API
    print("Fetching device ID from Spotify API...", flush=True)
    response = requests.get(
        "https://api.spotify.com/v1/me/player/devices",
        headers={"Authorization": f"Bearer {oauth2}"},
        timeout=10
    )
    
    if response.status_code == 429:
        raise ConnectionError("Spotify rate limit exceeded. Please wait a moment.")
    
    devices = [device["id"] for device in response.json().get("devices", [])]

    if not devices:
        raise ConnectionError("No connected device!")

    device_id = devices[0]  # Use first device
    
    # Cache the device ID for 3 hours
    redis_client.setex(DEVICE_CACHE_KEY, DEVICE_CACHE_TTL, device_id)
    print(f"Cached device ID for {DEVICE_CACHE_TTL}s: {device_id}", flush=True)
    
    return device_id
