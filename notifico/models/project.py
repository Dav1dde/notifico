# -*- coding: utf-8 -*-
__all__ = ('Project',)
import datetime

from sqlalchemy import or_

from notifico import db


class Project(db.Model):
    #: The unique identifier for this Project.
    id = db.Column(db.Integer, primary_key=True)
    #: The name for this Project.
    name = db.Column(db.String(50), nullable=False)
    #: The UTC timestamp for when this Project was created.
    created = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
    #: ``True`` if this project is visible to the public.
    public = db.Column(db.Boolean, default=True)
    #: A website for this project.
    website = db.Column(db.String(1024))

    #: The user who created or currently owns this Project.
    owner = db.relationship('User', backref=db.backref(
        'projects',
        order_by=id,
        lazy='dynamic',
        # If a user is deleted, we want all of the associated
        # projects to go with it.
        cascade='all, delete-orphan'
    ))

    #: Obsolete field, no longer used in production.
    full_name = db.Column(db.String(101), nullable=False, unique=True)

    #: The total count of all messages from all sources that have
    #: been recieved for this project.
    message_count = db.Column(db.Integer, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def new(cls, name, public=True, website=None):
        c = cls()
        c.name = name.strip()
        c.public = public
        c.website = website.strip() if website else None
        return c

    @classmethod
    def visible(cls, q, user=None):
        """
        Modifies the sqlalchemy query `q` to only show projects accessible
        to `user`. If `user` is ``None``, only shows public projects.
        """
        if user and user.in_group('admin'):
            # We don't do any filtering for admins,
            # who should have full visibility.
            pass
        elif user:
            # We only show the projects that are either public,
            # or are owned by `user`.
            q = q.filter(or_(
                Project.owner_id == user.id,
                Project.public == True
            ))
        else:
            q = q.filter(Project.public == True)

        return q

    def is_owner(self, user):
        """
        Returns ``True`` if `user` is the owner of this project.
        """
        return user and user.id == self.owner.id

    def can_see(self, user):
        if self.public:
            # Public projects are always visible.
            return True
        if user and user.in_group('admin'):
            # Admins can always see projects.
            return True
        elif self.is_owner(user):
            # The owner of the project can always see it.
            return True

        return False

    def can_modify(self, user):
        """
        Returns ``True`` if `user` can modify this project.
        """
        if user and user.in_group('admin'):
            # Admins can always modify projects.
            return True
        elif self.is_owner(user):
            return True

        return False
