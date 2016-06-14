# -*- coding: utf-8 -*-
"""Unit and functional test suite for SkyLines."""

from skylines import db
from skylines.websetup.bootstrap import bootstrap

__all__ = ['setup_db', 'setup_app', 'teardown_db', 'url_for']


def setup_db():
    """Method used to build a database"""
    db.create_all()


def setup_app():
    setup_db()
    bootstrap()


def teardown_db():
    """Method used to destroy a database"""
    db.session.remove()
    db.drop_all()
