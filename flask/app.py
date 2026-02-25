"""_summary_

    Returns:
        _type_: _description_
"""
from spotify.connect import get_oauth2_url, exchange_code_for_token
from flask import Flask, render_template, redirect, request, Blueprint


app = Flask(__name__)

spotify = Blueprint('spotify', __name__, url_prefix='/spotify')


@spotify.route("/startup")
def startup():
    """_summary_

    Returns:
        _type_: _description_
    """
    return render_template("startup.html")


@spotify.route("/")
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    return render_template("home.html")


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
    return render_template("get-code.html")


@spotify.route("/oauth2/authenticate", methods=["POST"])
def authenticate():
    """Exchange authorization code for token
    Returns:
        Response: Success or error page
    """
    redirect_url = request.form.get("redirect_url")
    try:
        access_token = exchange_code_for_token(redirect_url)
        # Store token in session or database
        return f"Success! Token: {access_token}"
    except Exception as e:
        return f"Error: {str(e)}", 400


@app.route("/flask-health-check")
def health_check():
    """Health check endpoint for Docker
    Returns:
        Response: Simple success message
    """
    return "OK", 200


app.register_blueprint(spotify)
