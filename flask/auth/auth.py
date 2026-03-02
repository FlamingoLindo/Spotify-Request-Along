"""Authentication blueprint for login and logout functionality."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from auth.models import get_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.

    GET: Display login form
    POST: Process login credentials
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user(username)
        if user and user.password == password:
            login_user(user)

            next_page = request.args.get('next')
            return redirect(next_page or url_for('spotify.home'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')
