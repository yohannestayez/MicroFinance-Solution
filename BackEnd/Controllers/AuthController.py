#!/usr/bin/env python3
"""
Authentication-related functions
"""
import bcrypt
from uuid import uuid4
from typing import Union
from sqlalchemy.orm.exc import NoResultFound
from BackEnd.models import storage
from BackEnd.models.user import User
from BackEnd.Controllers.UserControllers import UserController


def _hash_password(password) -> bytes:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Generates a UUID."""
    return str(uuid4())


class AuthController:
    """AuthController class to interact with the authentication database."""
    def __init__(self):
        """Initializes a new AuthController instance"""
        self._db = storage
        self._userC = UserController()

    def register_user(self, username: str, email: str, password: str, admin: bool) -> User:
        """Register a new user in the database."""
        new_user = None
        try:
            new_user = self._userC.find_user_by(email=email)
        except NoResultFound:
            return self._userC.add_user(username, email, password, admin)
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """Validates user login credentials."""
        user = None
        try:
            user = self._userC.find_user_by(email=email)
            if user is not None:
                return bcrypt.checkpw(
                    password.encode("utf-8"),
                    user.password.encode("utf-8")
                )
        except NoResultFound:
            return False
        return False

    def create_session(self, email: str) -> str:
        """Create a new session for user."""
        user = None
        try:
            user = self._userC.find_user_by(email=email)
        except NoResultFound:
            return None
        if user is None:
            return None

        session_id = _generate_uuid()
        self._userC.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """Retrieves a user based on a given session ID."""
        user = None
        if session_id is None:
            return None
        self._db.cleanup_expired_sessions()
        try:
            user = self._userC.find_user_by(session_id=session_id)
        except NoResultFound:
            return None
        return user

    def destroy_session(self, user_id: int) -> None:
        """Destroys a session associated with a given user."""
        if user_id is None:
            return None
        self._userC.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """Generates a password reset token for a user."""
        user = None
        try:
            user = self._userC.find_user_by(email=email)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError("User not found")
        reset_token = _generate_uuid()
        self._userC.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates a user's password given the user's reset token."""
        user = None
        try:
            user = self._userC.find_user_by(reset_token=reset_token)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError("Invalid reset token")
        new_password_hash = _hash_password(password)
        self._userC.update_user(user.id, password=new_password_hash, reset_token=None)
