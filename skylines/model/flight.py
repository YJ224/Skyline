# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import ForeignKey, Column, func
from sqlalchemy.types import Integer, DateTime, String
from sqlalchemy.ext.hybrid import hybrid_property
from skylines.model.auth import User
from skylines.model import DeclarativeBase, DBSession
from tg import config, request
from geoalchemy.geometry import GeometryColumn, Point, GeometryDDL
from geoalchemy.postgis import PGComparator
from skylines.model.geo import Location


class Flight(DeclarativeBase):
    __tablename__ = 'flights'

    id = Column(Integer, autoincrement=True, primary_key=True)
    owner_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable=False)
    owner = relation('User', primaryjoin=(owner_id == User.user_id))
    time_created = Column(DateTime, nullable=False, default=datetime.now)
    time_modified = Column(DateTime, nullable=False, default=datetime.now)
    filename = Column(String(), nullable=False)
    md5 = Column(String(32), nullable=False, unique=True)

    logger_manufacturer_id = Column(String(3))

    pilot_id = Column(Integer, ForeignKey('tg_user.user_id'))
    pilot = relation('User', primaryjoin=(pilot_id == User.user_id))
    co_pilot_id = Column(Integer, ForeignKey('tg_user.user_id'))
    co_pilot = relation('User', primaryjoin=(co_pilot_id == User.user_id))

    club_id = Column(Integer, ForeignKey('clubs.id'))

    takeoff_time = Column(DateTime, nullable=False)
    landing_time = Column(DateTime, nullable=False)
    takeoff_location_wkt = GeometryColumn(Point(2), comparator=PGComparator)
    landing_location_wkt = GeometryColumn(Point(2), comparator=PGComparator)

    olc_classic_distance = Column(Integer)
    olc_triangle_distance = Column(Integer)
    olc_plus_score = Column(Integer)

    @hybrid_property
    def duration(self):
        return self.landing_time - self.takeoff_time

    @hybrid_property
    def year(self):
        return self.takeoff_time.year

    @year.expression
    def year(cls):
        return func.date_part('year', cls.takeoff_time)

    @property
    def takeoff_location(self):
        if self.takeoff_location_wkt is None:
            return None

        wkt = DBSession.scalar(self.takeoff_location_wkt.wkt)
        return Location.from_wkt(wkt)

    @takeoff_location.setter
    def takeoff_location(self, location):
        self.takeoff_location_wkt = location.to_wkt()

    @property
    def landing_location(self):
        if self.landing_location_wkt is None:
            return None

        wkt = DBSession.scalar(self.landing_location_wkt.wkt)
        return Location.from_wkt(wkt)

    @landing_location.setter
    def landing_location(self, location):
        self.landing_location_wkt = location.to_wkt()

    @classmethod
    def by_md5(cls, _md5):
        return DBSession.query(cls).filter_by(md5=_md5).first()

    def get_download_uri(self):
        return config['skylines.files.uri'] + '/' + self.filename

    def is_writable(self):
        return request.identity and \
               (self.owner_id == request.identity['user'].user_id or
                self.pilot_id == request.identity['user'].user_id or
                'manage' in request.identity['permissions'])

    def may_delete(self):
        return request.identity and 'manage' in request.identity['permissions']

GeometryDDL(Flight.__table__)
