#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""errors.py
"""
__all__ = ('error_generic',)
from flask import render_template, request, Markup


def error_generic(error):
    """
    Called when a generic error occured when responding to a request.
    """
    return render_template(
        'errors/generic.html',
        error_code=error.code,
        e=error,
        description=Markup(error.get_description(request.environ))
    ), error.code
