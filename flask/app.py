"""_summary_

    Returns:
        _type_: _description_
"""
import os
from requests.exceptions import RequestException
from oauthlib.oauth2 import OAuth2Error
from spotify.connect import get_oauth2_url, exchange_code_for_token, get_token
from spotify.search_track import search
from flask import Flask, render_template, redirect, request, Blueprint, url_for, session, jsonify


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

spotify = Blueprint('spotify', __name__, url_prefix='/spotify')


@spotify.route("/")
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    return render_template("home.html")


@spotify.route("/startup")
def startup():
    """_summary_

    Returns:
        _type_: _description_
    """
    return render_template("startup.html")


@spotify.route("/startup/start", methods=["POST"])
def start_oauth():
    """Handle the Start button press and initiate OAuth2 flow
    Returns:
        Response: Redirect to OAuth2 authorization URL
    """
    auth_url = get_oauth2_url()
    return redirect(auth_url)


@spotify.route("/oauth2")
def get_code():
    """Display page for user to paste redirect URL
    Returns:
        Response: Rendered template
    """
    full_url = request.url
    return render_template("get-code.html", redirect_url=full_url)


@spotify.route("/oauth2/authenticate", methods=["POST"])
def authenticate():
    """Exchange authorization code for token
    Returns:
        Response: Success or error page
    """
    redirect_url = request.form.get("redirect_url")
    try:
        oauth2 = exchange_code_for_token(redirect_url)
        token = get_token()

        session['token'] = token
        session['oauth2'] = oauth2
        return redirect(url_for('spotify.home'))
    except OAuth2Error as e:
        return render_template('error.html', error=f"OAuth2 error: {str(e)}")
    except RequestException as e:
        return render_template('error.html', error=f"Request error: {str(e)}")


@spotify.route("/search")
def search_tracks():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    token = session.get("token")
    if not token:
        return jsonify({"error": "Not authenticated"}), 401
    data = search(query, token)
    tracks = data.get("tracks", {}).get("items", [])
    results = [
        {
            "name": t["name"],
            "artist": t["artists"][0]["name"],
            "album": t["album"]["name"],
            "image": t["album"]["images"][1]["url"] if t["album"]["images"] else None,
            "url": t["external_urls"]["spotify"],
        }
        for t in tracks
    ]
    return jsonify(results)


app.register_blueprint(spotify)
