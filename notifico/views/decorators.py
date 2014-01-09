# -*- coding: utf-8 -*-
__all__ = (
    'user_required',
    'no_user_required',
    'group_required'
)
from functools import wraps

from flask import (
    g,
    flash,
    url_for,
    redirect
)


def user_required(f):
    """
    A decorator for views which required a logged in user.
    """
    @wraps(f)
    def _wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('account.login'))
        return f(*args, **kwargs)
    return _wrapped


def no_user_required(f):
    """
    A decorator for views which require no user to be logged in,
    such as login and signup pages.
    """
    @wraps(f)
    def _wrapped(*args, **kwargs):
        if g.user:
            flash(u'You are already logged in.', 'danger')
            return redirect(url_for('public.landing'))
        return f(*args, **kwargs)
    return _wrapped


def group_required(name):
    """
    A decorator for views which require a user to be member
    to a particular group.
    """
    def _wrap(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            if g.user is None or not g.user.in_group(name):
                return redirect(url_for('account.login'))
            return f(*args, **kwargs)
        return _wrapped
    return _wrap
