# -*- coding: utf8 -*-
__all__ = ('User', 'Group')
import os
import base64
import hashlib
import datetime

from sqlalchemy.sql import exists
from sqlalchemy.ext.hybrid import hybrid_property

from notifico import db
from notifico.models import CaseInsensitiveValue


def _create_salt():
    """
    Returns a new base64 salt.
    """
    return base64.b64encode(os.urandom(8))[:8]


def _hash_password(password, salt):
    """
    Returns a hashed password from `password` and `salt`.
    """
    return hashlib.sha256(salt + password.strip()).hexdigest()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(8), nullable=False)
    joined = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)

    @classmethod
    def new(cls, username, email, password):
        u = cls()
        u.email = email.lower().strip()
        u.username = username.strip()
        u.set_password(password)
        return u

    ###
    # Lookup
    ###

    @hybrid_property
    def username_i(self):
        return CaseInsensitiveValue('username', self.username)

    @classmethod
    def by_username(cls, username):
        return cls.query.filter_by(username_i=username).first()

    @classmethod
    def username_in_use(cls, username):
        """
        Checks to see if a user already exists, or
        """
        return db.session.query(exists().where(
            cls.username_i == username
        )).scalar()

    ###
    # Authentication
    ###

    @classmethod
    def is_valid_login(cls, username, password):
        """
        Returns a `User` object for which `username` and `password` are
        correct, otherwise ``None``.

        .. note::

            SQLite support (and it's lack of support for SHA2())
            forces us to pull back the user and then check the
            password, instead of doing it as a single scalar query.
        """
        u = db.session.query(cls.password, cls.salt).filter_by(
            username_i=username
        ).first()

        if u and u.password == _hash_password(password, u.salt):
            return True

        return False

    def set_password(self, new_password):
        """
        Changes a users password, calculating a new salt.

        .. note::

            `set_password()` does not commit the changes to the
            database.
        """
        self.salt = _create_salt()
        self.password = _hash_password(new_password, self.salt)

    ###
    # Authorization
    ###

    def in_group(self, name):
        """
        Returns ``True`` if this user is in the group `name`, otherwise
        ``False``.
        """
        return any(g.name == name.lower() for g in self.groups)

    def add_group(self, name):
        """
        Adds this user to the group `name` if not already in it. The group
        will be created if needed.
        """
        if self.in_group(name):
            # We're already in this group.
            return

        self.groups.append(Group.get_or_create(name=name))


class Group(db.Model):
    """
    A group is a select list of permissions applied to all members
    of that group. For example, you could have an "admin" group
    and a "moderator" group.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(255), unique=True, nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref=db.backref(
        'groups',
        order_by=id,
        lazy='joined'
    ))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Group({name!r})>'.format(name=self.name)

    @classmethod
    def get_or_create(cls, name):
        name = name.lower()

        g = cls.query.filter_by(name=name).first()
        if not g:
            g = Group(name=name)

        return g
