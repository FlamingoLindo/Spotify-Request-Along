"""
User model for Flask-Login authentication.
"""
import os
from flask_login import UserMixin


class User(UserMixin):
    """
    Simple User class that implements Flask-Login's UserMixin.
    """

    def __init__(self, id, username=None, password=None):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User {self.username}>'


users_db = {
    os.getenv("U_LOGIN"): {'password': os.getenv("U_PASSWORD"), 'id': '1'},
}


def get_user(username):
    """Retrieve a user from the mock database.

    Args:
        username: The username to look up

    Returns:
        User object if found, None otherwise
    """
    user_data = users_db.get(username)
    if user_data:
        return User(
            id=user_data['id'],
            username=username,
            password=user_data['password']
        )
    return None


def get_user_by_id(user_id):
    """Retrieve a user by their ID.

    Args:
        user_id: The user ID to look up

    Returns:
        User object if found, None otherwise
    """
    for username, data in users_db.items():
        if data['id'] == user_id:
            return User(
                id=user_id,
                username=username,
                password=data['password']
            )
    return None
