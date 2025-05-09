#!/usr/bin/python3
"""
Contains the class User Controller
"""

from BackEnd.models.user import User
from sqlalchemy import tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from BackEnd.models import storage


class UserController:
    """
        - UserController class
    """
    def __init__(self):
        """Initialize the UserController with a database connection"""
        self.db = storage
        self.__session = None

    def add_user(self, username: str, email: str, password: str, admin: bool) -> User:
        """Create a new user in the given Database"""
        try:
            new_user = User(username=username, email=email, admin=admin)
            new_user.set_password(password)  # Set the password using the set_password method
            self.db.new(new_user)
            self.db.save()
        except Exception:
            self.db.Rollback()
            new_user = None
        return new_user

    def find_user_by(self, **filters) -> User:
        """Find a user in the database based on filters."""
        filter_field, filter_value = [], []
        for field, value in filters.items():
            if hasattr(User, field):
                filter_field.append(getattr(User, field))
                filter_value.append(value)
            else:
                raise InvalidRequestError(f"Invalid filter: {field}")
        new_user = self.db.session().query(User).filter(
                tuple_(*filter_field).in_([tuple(filter_value)]),
            ).first()
        if new_user is None:
            raise NoResultFound("User not Found.")
        return new_user

    def update_user(self, user_id, **updates) -> None:
        """Update user information in the database."""
        user = self.find_user_by(id=user_id)
        if user is None:
            return
        update_field = {}
        for key, value in updates.items():
            if hasattr(User, key):
                update_field[getattr(User, key)] = value
            else:
                raise ValueError(f"Invalid field: {key}")
        self.db.session().query(User).filter(User.id == user_id).update(
            update_field,
            synchronize_session=False
        )
        self.db.save()
