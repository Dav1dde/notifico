#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__init__.py

Project related views, such as project creation and details.
"""
from flask import (
    Blueprint,
    render_template,
    g,
    abort,
)

from notifico.models.user import User

projects = Blueprint(
    'projects',
    __name__,
    template_folder='templates'
)


@projects.url_defaults
def _fill_in_defaults(endpoint, values):
    if 'u' not in values:
        if g.user:
            values['u'] = g.user.username


@projects.url_value_preprocessor
def _resolve_values(endpoint, values):
    # Resolve a User reference.
    if 'u' in values:
        u = User.by_username(values.pop('u'))
        if not u:
            # No user with that name actually exists.
            return abort(404)

        values['u'] = u

        # Resolve a Project reference.
        if 'p' in values:
            p = u.project_by_name(values.pop('p'))
            if not p:
                # That project doesn't exist.
                return abort(404)

            values['p'] = p


@projects.route('/<u>/')
def dashboard(u):
    """
    Display an overview of all the user's projects with summary
    statistics.
    """
    filtered_projects = g.user.projects

    return render_template(
        'dashboard.html',
        user=u,
        projects=filtered_projects,
        page_title='Notifico! - {u.username}\'s Projects'.format(
            u=u
        )
    )
