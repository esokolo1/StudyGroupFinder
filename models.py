"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

def get_first_name():
    return auth.current_user.get('first_name') if auth.current_user else None

def get_last_name():
    return auth.current_user.get('last_name') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


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

db.define_table(
    'comment',
    Field('session_id', 'reference session'),
    Field('user_id', default=get_user_id),
    Field('first_name', default=get_first_name),
    Field('last_name', default=get_last_name),
    Field('content'),
    Field("timestamp")
)

db.commit()



# Testing
def add_sessions_for_testing():
    db(db.session).delete()
    db(db.attendance).delete()
    db.session.insert(session_name="test1", school="UCSC", term="Fall 2020", class_name="CSE 183")
    db.session.insert(session_name="test2", school="UCSC", term="Summer 2022", class_name="CSE 10")
    db.commit()
    ids = db(db.session.session_name == "test2").select(db.session.id).as_list()
    id = ids[0]["id"]
    db.attendance.insert(email="ychen606@ucsc.edu", session_id=id)
    db.commit()
#add_sessions_for_testing()
