# -*- coding: utf-8 -*-
"""Setup the SkyLines application"""

from skylines.model import User


def test_admin():
    u = User()
    u.first_name = u'Example'
    u.last_name = u'Manager'
    u.email_address = u'manager@somedomain.com'
    u.password = u'managepass'
    u.admin = True
    return u


def test_user():
    u1 = User()
    u1.first_name = u'Example'
    u1.last_name = u'User'
    u1.email_address = u'max+skylines@blarg.de'
    u1.password = u'test'
    u1.tracking_key = 123456
    return u1
