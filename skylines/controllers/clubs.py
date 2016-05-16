# -*- coding: utf-8 -*-

from tg import expose, validate, redirect, request
from tg.i18n import ugettext as _
from tg.decorators import with_trailing_slash
from webob.exc import HTTPForbidden
from sqlalchemy import func

from .base import BaseController
from skylines.forms import club, pilot as pilot_forms
from skylines.lib.dbutil import get_requested_record
from skylines.model import DBSession, User, Group, Club


class ClubController(BaseController):
    @expose('clubs/pilots.jinja')
    def pilots(self):
        users = User.query(club=self.club) \
            .order_by(func.lower(User.name))

        return dict(active_page='settings', club=self.club, users=users)

    @expose('generic/form.jinja')
    def new_pilot(self, **kwargs):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        return dict(active_page='settings', title=_("Create Pilot"),
                    form=pilot_forms.new_form, values={})

    @expose()
    @validate(form=pilot_forms.new_form, error_handler=new_pilot)
    def create_pilot(self, email_address, name, **kw):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        pilot = User(name=name, email_address=email_address, club=self.club)
        DBSession.add(pilot)

        pilots = Group.query(group_name='pilots').first()
        if pilots:
            pilots.users.append(pilot)

        redirect('pilots')
