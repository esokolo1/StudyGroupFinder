"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

# added
def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None



### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'session',
    Field('session_name', requires = IS_NOT_EMPTY()),
    Field('owner', 'reference auth_user', default=get_user_id),
    Field('school', requires = IS_NOT_EMPTY()),
    Field('term', requires = IS_NOT_EMPTY()),
    Field('open', default=True),
    Field('class_name', requires = IS_NOT_EMPTY()),
    Field('location', requires = IS_NOT_EMPTY()),
    Field('description', requires = IS_NOT_EMPTY()),
    Field('date', requires = IS_NOT_EMPTY()),
    Field('starttime', requires = IS_NOT_EMPTY()),
    Field('endtime', requires = IS_NOT_EMPTY()),
    Field('announcement', default=""),
    Field('official'), # string, saying TA or student led
    Field('max_num_students', 'integer', requires = IS_NOT_EMPTY()),
    Field('num_students', 'integer', default=1)
)

db.define_table(
    'attendance',
    Field('email'),
    Field('session_id', 'reference session')
)

db.commit()
