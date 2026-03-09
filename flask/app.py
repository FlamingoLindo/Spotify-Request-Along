"""_summary_

    Returns:
        _type_: _description_
"""
import os
import time
import sys
import redis
import requests
from requests.exceptions import ReadTimeout, RequestException
from oauthlib.oauth2 import OAuth2Error
from spotify.connect import get_oauth2_url, exchange_code_for_token, get_token
from spotify.search_track import search
from spotify.player import play_new_track
from spotify.devices import available_devices
from spotify.playlist import add_track
from spotify.queue import get_queue, add_to_the_queue
from flask import Flask, render_template, redirect, request, Blueprint, url_for, jsonify
from flask_login import LoginManager, login_required
from auth.auth import auth_bp
from auth.models import get_user_by_id
from db.db_connect import connect_to_db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Initialize database with retry logic
max_retries = 5
retry_delay = 2
for attempt in range(max_retries):
    try:
        print(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})...", flush=True)
        connect_to_db()
        print("Database initialized successfully!", flush=True)
        break
    except Exception as e:
        print(f"Database connection failed: {e}", file=sys.stderr, flush=True)
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...", flush=True)
            time.sleep(retry_delay)
        else:
            print("Failed to connect to database after multiple attempts", file=sys.stderr, flush=True)
            raise

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return get_user_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access attempts."""
    return redirect(url_for('auth.login'))


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),  # pylint: disable=W1508
    decode_responses=True
)

spotify = Blueprint('spotify', __name__, url_prefix='/spotify')


@spotify.route("/")
async def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    return render_template("home.html")


@spotify.route("/startup")
@login_required
def startup():
    """_summary_

    Returns:
        _type_: _description_
    """
    return render_template("startup.html")


@spotify.route("/startup/start", methods=["POST"])
@login_required
def start_oauth():
    """Handle the Start button press and initiate OAuth2 flow
    Returns:
        Response: Redirect to OAuth2 authorization URL
    """
    auth_url = get_oauth2_url()
    return redirect(auth_url)


@spotify.route("/oauth2")
@login_required
def get_code():
    """Display page for user to paste redirect URL
    Returns:
        Response: Rendered template
    """
    full_url = request.url
    return render_template("get-code.html", redirect_url=full_url)


@spotify.route("/oauth2/authenticate", methods=["POST"])
@login_required
def authenticate():
    """Exchange authorization code for token
    Returns:
        Response: Success or error page
    """
    redirect_url = request.form.get("redirect_url")
    try:
        oauth2_data = exchange_code_for_token(redirect_url)
        token = get_token()
        # Store globally in Redis (accessible by all workers)
        redis_client.set("spotify_token", token)
        redis_client.set("spotify_oauth2", str(oauth2_data))
        return redirect(url_for('spotify.home'))
    except OAuth2Error as e:
        return render_template('error.html', error=f"OAuth2 error: {str(e)}")
    except RequestException as e:
        return render_template('error.html', error=f"Request error: {str(e)}")


@spotify.route("/search")
async def search_tracks():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    token = redis_client.get("spotify_oauth2")
    if not token:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        data = search(query, token)
    except ReadTimeout:
        return jsonify({"error": "Spotify request timed out, please try again"}), 504
    except RequestException as e:
        return jsonify({"error": f"Spotify API error: {str(e)}"}), 502

    tracks = data.get("tracks", {}).get("items", [])
    results = [
        {
            "uri": t["uri"],
            "name": t["name"],
            "artist": t["artists"][0]["name"],
            "album": t["album"]["name"],
            "image": t["album"]["images"][1]["url"] if t["album"]["images"] else None,
            "url": t["external_urls"]["spotify"],
        }
        for t in tracks
    ]
    return jsonify(results)


@spotify.route("/play/<uri>", methods=["PUT"])
async def play_track(uri: str):
    """Add track to database and playlist, then play/queue it.

    Args:
        uri (str): Spotify track URI

    Returns:
        _type_: JSON response with success or error message
    """
    try:
        oauth2 = redis_client.get("spotify_oauth2")
        if not oauth2:
            return jsonify({"error": "Not authenticated"}), 401

        # Get track name from request body
        data = request.get_json()
        track_name = data.get("name", "Unknown Track") if data else "Unknown Track"

        device = available_devices(oauth2=oauth2)
        
        # Check database and add track to playlist if new
        result = add_track(oauth2=oauth2, uri=uri, track_name=track_name)
        
        is_duplicate = result.get("status") == "duplicate"
        
        # Handle database errors (but not duplicates)
        if result.get("status") == "db_error":
            return jsonify({"error": result.get("error")}), 500
        
        # Handle Spotify API errors
        if result.get("status") == "spotify_error":
            error_message = result.get("error", "Unknown Spotify error")
            # Check if it's a rate limit error (429)
            if "429" in error_message:
                return jsonify({"error": "Spotify rate limit exceeded. Please wait a moment and try again."}), 429
            return jsonify({"error": error_message}), 500

        # Add to queue or play (even if duplicate)
        try:
            queue = get_queue(oauth2=oauth2)

            if queue == []:
                play_new_track(context_uri=uri, device_id=device, oauth2=oauth2)
            else:
                add_to_the_queue(oauth2=oauth2, uri=uri, device_id=device)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return jsonify({"error": "Spotify rate limit exceeded. Please wait before adding more tracks."}), 429
            raise

        # Return appropriate message
        if is_duplicate:
            return jsonify({"success": True, "message": "Track already in playlist, added to queue"}), 200
        else:
            return jsonify({"success": True, "message": "Track added to playlist and queue"}), 200
    except OAuth2Error as e:
        return jsonify({"error": f"OAuth2 error: {str(e)}"}), 500
    except RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500


@spotify.route("/queue")
async def queue_page():
    """Display the queue page

    Returns:
        _type_: _description_
    """

    try:
        oauth2 = redis_client.get("spotify_oauth2")
        if not oauth2:
            return jsonify({"error": "Not authenticated"}), 401

        queue = get_queue(oauth2=oauth2)

        if not queue:
            return render_template("queue.html", current=None, tracks=[])

        current = queue['currently_playing']
        current_track = {
            "uri": current["uri"],
            "name": current["name"],
            "artist": current["artists"][0]["name"],
            "album": current["album"]["name"],
            "image": current["album"]["images"][1]["url"] if current["album"]["images"] else None,
            "url": current["external_urls"]["spotify"],
        }
        tracks = [
            {
                "uri": t["uri"],
                "name": t["name"],
                "artist": t["artists"][0]["name"],
                "album": t["album"]["name"],
                "image": t["album"]["images"][1]["url"] if t["album"]["images"] else None,
                "url": t["external_urls"]["spotify"],
            }
            for t in queue['queue']
        ]
        return render_template("queue.html", current=current_track, tracks=tracks)
    except OAuth2Error as e:
        return render_template('error.html', error=f"OAuth2 error: {str(e)}")
    except RequestException as e:
        return render_template('error.html', error=f"Request error: {str(e)}")


app.register_blueprint(auth_bp)
app.register_blueprint(spotify)
