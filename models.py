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

def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'school',
    Field('school_name',notnull=True,unique=True),
    Field('school_abbr'),
)
db.define_table(
    'profile',
    Field('user_id','reference auth_user',default=get_user_id,unique=True),
    Field('profile_description','text',default=''),
)
db.define_table(
    'school_enrollment',
    Field('user_id','reference auth_user',default=get_user_id),
    Field('school_id','reference school',notnull=True),
)
db.define_table(
    'course',
    Field('school_id','reference school',notnull=True),
    Field('course_subject',notnull=True,
      requires=[IS_UPPER(),IS_MATCH('^[A-Z]{2,}$'),IS_NOT_EMPTY()]),
    Field('course_number',notnull=True,
      requires=[IS_UPPER(),IS_MATCH('^\d{1,}[A-Z]?$'),IS_NOT_EMPTY()]),
    Field('course_title'),
#    Field('course_term',
#      requires=[IS_UPPER(),IS_MATCH('^\d{4} [A-Z]{1,}$')]),
#    Field('course_instructor'),
    Field('course_description','text'),
)
db.define_table(
    'course_enrollment',
    Field('user_id','reference auth_user',default=get_user_id),
    Field('course_id','reference course',notnull=True),
    Field('enrollment_is_ta','boolean',default=False),
    Field('enrollment_is_tutor','boolean',default=False),
    Field('is_active','boolean',default=True),
)



db.define_table(
    'session',
    Field('user_id','reference auth_user',default=get_user_id),
    Field('course_id','reference course'),
    Field('session_name',notnull=True,requires=IS_NOT_EMPTY()),
    Field('session_description','text'),
    Field('session_location',notnull=True,requires=IS_NOT_EMPTY()),
    Field('session_days','integer',notnull=True,
      requires=IS_INT_IN_RANGE(0,128)), #combo of 7 days
    Field('session_time','time',notnull=True,requires=IS_NOT_EMPTY()),
    Field('session_length','integer'), #in minutes
    Field('session_start_date','date'),
    Field('session_end_date','date'),
    Field('session_capacity','integer'),
    Field('session_has_tas','boolean',default=False),
    Field('session_is_open','boolean',default=True),
)

db.define_table(
    'session_enrollment',
    Field('user_id','reference auth_user',default=get_user_id),
    Field('session_id','reference session',notnull=True),
    Field('is_enrolled','boolean',default=True),
)

db.define_table(
    'attendance',
    Field('user_id','reference auth_user',default=get_user_id),
    Field('session_id','reference session',notnull=True),
)

db.define_table(
    'study_group',
    Field('group_name',notnull=True,requires=IS_NOT_EMPTY()),
    Field('group_description','text'),
)
db.define_table(
    'group_membership',
    Field('group_id','reference study_group',notnull=True),
    Field('user_id','reference auth_user',default=get_user_id),
)

db.define_table(
    'post',
    Field('session_id','reference session'),
    Field('post_content','text',notnull=True,requires=IS_NOT_EMPTY()),
    Field('post_timestamp','datetime',default=get_time),
    Field('post_is_announcement','boolean',default=False),
)
db.define_table(
    'comment',
    Field('user_id','reference auth_user',default=get_user_id),
    Field('post_id','reference post',notnull=True),
    Field('comment_content','text',notnull=True,requires=IS_NOT_EMPTY()),
    Field('comment_timestamp','datetime',default=get_time),
    Field('parent_comment_id','reference comment'),
)

db.commit()
####################

def testing_insert():
  if db(db.school).select().first() is None:

    db(db.auth_user.email.like('_%')).delete()
    for i in range(0,3):
      user=dict(
        email='_'+str(i)+'@ucsc.edu',
        first_name='a',last_name='a',
        password='_'+str(i),
      )
      auth.register(user,send=False)

    db(db.school).delete()
    db.school.insert(
      school_name='University of California, Santa Cruz',
      school_abbr='UCSC',
    )
    for i in range(0,6):
      db.school.insert(school_name='School '+str(i))

    first_school_id = db(db.school).select().first().id
    db(db.course).delete()
    db.course.insert(
      school_id=first_school_id,
      course_term='2023 Spring',
      course_subject='CSE',
      course_number='183',
      course_title='Webpasdfpjaodsi',
    )
    for i in range(0,6):
      db.course.insert(
        school_id=first_school_id,
        course_term='2023 Spring',
        course_subject='CSE',
        course_number=i,
        course_title='course'+str(i),
      )



    db.commit()

testing_insert()
