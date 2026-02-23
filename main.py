"""_summary_

    Returns:
        _type_: _description_
"""
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    """_summary_

    Returns:
        _type_: _description_
    """
    return render_template("home.html")
