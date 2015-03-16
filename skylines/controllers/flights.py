# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from tg import expose, validate, require, request, redirect, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.decorators import override_template
from repoze.what.predicates import has_permission
from webob.exc import HTTPNotFound, HTTPForbidden
from sqlalchemy.sql.expression import desc, or_, and_, between
from sqlalchemy import func
from sprox.formbase import EditableForm
from sprox.widgets import PropertySingleSelectField
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, User, Club, Flight
from skylines.controllers.upload import UploadController
from skylines.lib.datatables import GetDatatableRecords

class PilotSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        users = DBSession.query(User) \
                .filter(User.club_id == request.identity['user'].club_id) \
                .order_by(User.display_name)
        options = [(None, 'None')] + \
                  [(user.user_id, user) for user in users]
        d['options'] = options
        return d

class SelectPilotForm(EditableForm):
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['pilot', 'co_pilot']
    __base_widget_args__ = dict(action='select_pilot')
    pilot = PilotSelectField
    co_pilot = PilotSelectField

select_pilot_form = SelectPilotForm(DBSession)

class FlightController(BaseController):
    def __init__(self, flight):
        self.flight = flight

    @expose('skylines.templates.flights.view')
    def index(self):
        from skylines.lib.analysis import flight_path
        fixes = flight_path(self.flight)

        import cgpolyencode
        encoder = cgpolyencode.GPolyEncoder(num_levels=4)
        fixes = encoder.encode(fixes)

        return dict(page='flights', flight=self.flight,
                    fixes=fixes)

    @expose('skylines.templates.flights.map')
    def map(self):
        from skylines.lib.analysis import flight_path
        fixes = flight_path(self.flight)

        import cgpolyencode
        encoder = cgpolyencode.GPolyEncoder(num_levels=4)
        fixes = encoder.encode(fixes)

        return dict(page='flights', fixes=fixes)

    @expose('skylines.templates.generic.form')
    def change_pilot(self):
        if not self.flight.is_writable():
            raise HTTPForbidden

        return dict(page='settings', title=_('Select Pilot'),
                    form=select_pilot_form,
                    values=dict(pilot=self.flight.pilot_id, co_pilot=self.flight.co_pilot_id))

    @expose()
    @validate(form=select_pilot_form, error_handler=change_pilot)
    def select_pilot(self, pilot, co_pilot, **kwargs):
        if not self.flight.is_writable():
            raise HTTPForbidden

        user = request.identity['user']
        if self.flight.owner_id == user.user_id:
            if self.flight.pilot_id != pilot:
                self.flight.pilot_id = pilot
                if pilot:
                    self.flight.club_id = DBSession.query(User).get(pilot).club_id
            self.flight.co_pilot_id = co_pilot
            self.flight.time_modified = datetime.now()
            DBSession.flush()

        redirect('.')

    @expose()
    @require(has_permission('upload'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        from skylines.lib.analysis import analyse_flight
        analyse_flight(self.flight)
        DBSession.flush()

        return redirect('/flights/id/' + str(self.flight.id))

    @expose('skylines.templates.generic.confirm')
    @require(has_permission('manage'))
    def delete(self, yes=False):
        if yes:
            files.delete_file(self.flight.filename)
            DBSession.delete(self.flight)

            redirect('/flights/')
        else:
            return dict(title='Delete Flight',
                        question='Are you sure you want to delete this flight?',
                        action='', cancel='.')

class FlightIdController(BaseController):
    @expose()
    def lookup(self, id, *remainder):
        flight = DBSession.query(Flight).get(int(id))
        if flight is None:
            raise HTTPNotFound

        controller = FlightController(flight)
        return controller, remainder

class FlightsController(BaseController):
    def _do_list(self, tab, kw, date=None, pilot=None, club=None, filter=None):
        flights = DBSession.query(Flight)
        if date:
            flights = flights.filter(between(Flight.takeoff_time,
                                             date, date + timedelta(days=1)))
        if pilot:
            flights = flights.filter(or_(Flight.pilot == pilot,
                                         Flight.co_pilot == pilot))
        if club:
            flights = flights.filter(Flight.club == club)
        if filter is not None:
            flights = flights.filter(filter)

        flights = flights.order_by(desc(Flight.takeoff_time))

        if kw.get("json", "false")  == 'true':
            columns = { 0: 'takeoff_time', 1 : 'olc_plus_score', 2: 'pilot_id', 3: 'olc_classic_distance',
                        4: 'club_id', 5: 'takeoff_time', 6: 'id' }

            flights, response_dict = GetDatatableRecords(kw, flights, columns)

            method = tab
            if method == 'all': method = 'index'
            override_template(getattr(self, method), 'mako:skylines.templates.flights.list_m')
            return dict(response_dict=response_dict,
                        date=date, pilot=pilot, club=club,
                        flights = flights)

        else:
            flights_count = flights.count()
            if flights_count > int(config.get('skylines.lists.server_side', 250)):
                limit = int(config.get('skylines.lists.display_length', 50))
            else:
                limit = int(config.get('skylines.lists.server_side', 250))

            flights = flights.order_by(desc(Flight.takeoff_time)).limit(limit)
            return dict(page = 'flights', tab = tab,
                        date=date, pilot=pilot, club=club,
                        flights = flights, flights_count = flights_count)

    @expose()
    def index(self, **kw):
        redirect('today')

    @expose('skylines.templates.flights.list')
    def all(self, **kw):
        return self._do_list('all', kw)

    @expose('skylines.templates.flights.list')
    def today(self, **kw):
        date = DBSession.query(func.max(Flight.takeoff_time).label('date')).one().date.date()
        return self._do_list('today', kw, date=date)

    @expose('skylines.templates.flights.list')
    def my(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        return self._do_list('my', kw, pilot=request.identity['user'])

    @expose('skylines.templates.flights.list')
    def my_club(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        return self._do_list('my_club', kw, club=request.identity['user'].club)

    @expose('skylines.templates.flights.list')
    def unassigned(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        f = and_(Flight.pilot_id == None,
                 Flight.owner == request.identity['user'])
        print "FILTER=========", repr(f), repr(Flight.pilot_id == None), repr(Flight.owner == request.identity['user'])
        return self._do_list('unassigned', kw, filter=f)

    @expose('skylines.templates.flights.list')
    def pilot(self, id, **kw):
        pilot = DBSession.query(User).get(id)
        if not pilot:
            raise HTTPNotFound

        return self._do_list('pilot', kw, pilot=pilot)

    @expose('skylines.templates.flights.list')
    def club(self, id, **kw):
        club = DBSession.query(Club).get(id)
        if not club:
            raise HTTPNotFound

        return self._do_list('club', kw, club=club)

    @expose('skylines.templates.flights.top_pilots')
    def top(self):
        subq = DBSession.query(Flight.pilot_id,
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(Flight.pilot_id).subquery()
        result = DBSession.query(User, subq.c.count, subq.c.total) \
                 .join((subq, subq.c.pilot_id == User.user_id))
        result = result.order_by(desc('total'))
        result = result.limit(20)
        return dict(page='flights', tab='top', result=result)

    @expose('skylines.templates.flights.top_clubs')
    def top_clubs(self):
        subq = DBSession.query(Flight.club_id,
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(Flight.club_id).subquery()
        result = DBSession.query(Club, subq.c.count, subq.c.total) \
                 .join((subq, subq.c.club_id == Club.id))
        result = result.order_by(desc('total'))
        result = result.limit(20)
        return dict(page='flights', tab='top_clubs', result=result)

    @expose()
    @require(has_permission('manage'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        from skylines.lib.analysis import analyse_flight
        for flight in DBSession.query(Flight):
            analyse_flight(flight)
            DBSession.flush()

        return redirect('/flights/')

    id = FlightIdController()
    upload = UploadController()
