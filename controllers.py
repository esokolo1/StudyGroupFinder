"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A

from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user_id
from pydal.validators import *

from py4web.utils.form import Form, FormStyleBulma

import datetime
import pytz
from pytz import timezone

# Source: adding images - https://github.com/learn-py4web/star_ratings

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():

    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
        get_session_list_url = URL('get_session_list', signer=url_signer)
    )

@action('find_session', method=["GET", "POST"])
@action.uses('find_session.html', db, session, auth.user, url_signer)
def find_session():

    return dict(
        get_session_list_url = URL('get_session_list', signer=url_signer),

    )


@action('create_session', method=["GET", "POST"])
@action.uses('create_session.html', db, session, auth.user, url_signer)
def create_session():
    form = Form(
        [Field('Session_Name', requires = IS_NOT_EMPTY(error_message="Error: Enter Study Group Session Name")),
         Field('School', requires = IS_NOT_EMPTY(error_message="Error: Enter School Name")),
         Field('Term', requires = IS_NOT_EMPTY(error_message="Error: Enter Term (ex. Spring 2023)")),
         Field('Class_Name', requires = IS_NOT_EMPTY(error_message="Error: Enter Class Name (ex. CSE 183)")),
         Field('Location', requires = IS_NOT_EMPTY(error_message="Error: Enter Location (ex. Kresge Clrm 327)")),
         Field('Description', 'text', requires = IS_NOT_EMPTY(error_message="Error: Enter Description")),
         Field('Date', 'date', requires=IS_DATE_IN_RANGE(format=('%Y-%m-%d'),minimum=datetime.date.today(), error_message='Error: Date cannot be in the past')), 
         Field('Starttime', 'time', requires=IS_TIME()), 
         Field('Endtime', 'time', requires=IS_TIME()), 
         Field('Announcement', 'text'), 
         Field('TA_or_Student_Led', label="TA/Tutor Attendance or Student Led", requires = IS_IN_SET(['TA/Tutor', 'Student Led'], zero=T('choose one'), error_message="Error: Choose One")),
         Field('Maximum_Number_of_Students', requires=IS_INT_IN_RANGE(0, 1e6))],
         formstyle=FormStyleBulma,
         csrf_session=session
    )
    if form.accepted:
        id = db.session.insert(
            session_name=form.vars["Session_Name"],
            school=form.vars["School"],
            term=form.vars["Term"],
            class_name=form.vars["Class_Name"],
            location=form.vars["Location"],
            description=form.vars["Description"],
            date=form.vars["Date"],
            starttime=form.vars["Starttime"],
            endtime=form.vars["Endtime"],
            official=form.vars["TA_or_Student_Led"],
            max_num_students=form.vars["Maximum_Number_of_Students"]
        )
        db.attendance.insert(
            email=get_user_email(),
            session_id=id
        )
        redirect(URL('create_session_results'))
    return dict(form=form,
                )


@action('create_session_results')
@action.uses('create_session_results.html', db, session, auth.user, url_signer)
def create_session_results():

    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
        url_signer = url_signer,
        get_session_list_url = URL('get_session_list', signer=url_signer),
    )


# Edit session
@action('edit_session/<attendance_id:int>', method=["GET", "POST"])
@action.uses('edit_session.html', db, session, auth.user, url_signer.verify())
def edit_session(attendance_id):
    # only user who create this session can edit
    assert attendance_id is not None
    # extract attendance_row
    get_attendance_row = db.attendance[attendance_id]
    # session_row
    session_row = db.session[get_attendance_row.session_id]

    session_name = session_row.session_name
    school = session_row.school
    term = session_row.term
    open_status = session_row.open
    class_name = session_row.class_name
    location = session_row.location
    description = session_row.description
    date = session_row.date
    starttime = session_row.starttime
    endtime = session_row.endtime
    announcement = session_row.announcement
    official = session_row.official
    max_num_students = session_row.max_num_students

    if session_row is None:
        redirect(URL('create_session_results'))
    
    form = Form([
            Field('Session_Name', requires = IS_NOT_EMPTY(error_message="Error: Enter Study Group Session Name")), 
            Field('School', requires = IS_NOT_EMPTY(error_message="Error: Enter School Name")), 
            Field('Term', requires = IS_NOT_EMPTY(error_message="Error: Enter Term (ex. Spring 2023)")), 
            Field('Open', requires = IS_IN_SET([True, False]), default=True), 
            Field('Class_Name', requires = IS_NOT_EMPTY(error_message="Error: Enter Class Name (ex. CSE 183)")), 
            Field('Location', requires = IS_NOT_EMPTY(error_message="Error: Enter Location (ex. Kresge Clrm 327)")), 
            Field('Description', 'text', requires = IS_NOT_EMPTY(error_message="Error: Enter Description")), 
            Field('Date', 'date', requires=IS_DATE_IN_RANGE(format=('%Y-%m-%d'),minimum=datetime.date.today(), error_message='Error: Date cannot be in the past')), 
            Field('Starttime', 'time', requires=IS_TIME()), 
            Field('Endtime', 'time', requires=IS_TIME()), 
            Field('Announcement', 'text'), 
            Field('Official', requires = IS_IN_SET(['TA/Tutor', 'Student Led'], error_message="Error: Choose One")), 
            Field('Maximum_Number_of_Students', requires=IS_INT_IN_RANGE(0, 1e6)),
            ],
        	record = dict(
                Session_Name=session_name, 
                School=school, 
                Term=term, 
                Open=open_status, 
                Class_Name=class_name, 
                Location=location,
                Description=description,
                Date=date,
                Starttime=starttime,
                Endtime=endtime,
                Announcement = announcement,
                Official = official,
                Maximum_Number_of_Students=max_num_students),
            deletable=False,
            csrf_session=session,
            formstyle=FormStyleBulma)
    
    if form.accepted:
        session_row.update_record(
            session_name = form.vars["Session_Name"], 
            school = form.vars["School"],
            term = form.vars["Term"],
            open = form.vars["Open"],
            class_name = form.vars["Class_Name"],
            location = form.vars["Location"],
            description = form.vars["Description"],
            date=form.vars["Date"],
            starttime=form.vars["Starttime"],
            endtime=form.vars["Endtime"],
            official = form.vars["Official"],
            max_num_students = form.vars["Maximum_Number_of_Students"])
        redirect(URL('create_session_results'))
    
    return dict(form=form, 
    url_signer = url_signer,
    )

# Delete Session
@action('delete_session/<attendance_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_contact(attendance_id):
    assert attendance_id is not None
    # extract attendance_row
    get_attendance_row = db.attendance[attendance_id]
    session_row = db.session[get_attendance_row.session_id]
    # only user who create this session can delete
    if (session_row.owner == get_user_id()):
        db(db.session.id == get_attendance_row.session_id).delete()

    redirect(URL('create_session_results'))


@action('dashboard', method=["GET", "POST"])
@action.uses('dashboard.html',db, auth.user, url_signer)
def dashboard():
    # display all sessions that user who is logged in NOT attending
    # sessions = db(db.attendance.email != get_user_email()).select().as_list()
    # for s in sessions:
    #     session_info = db(db.session.id == s["session_id"]).select()
    #     for info in session_info:
    #         s["session_name"] = info.session_name
    #         s["owner"] = info.owner
    #         s["school"] = info.school
    #         s["term"] = info.term
    #         s["class_name"] = info.class_name
    #         s["edit"] = URL('edit_session', s["id"], signer=url_signer)
    #         s["delete"] = URL('delete_session', s["id"], signer=url_signer)
    
    return dict(
        get_session_list_url = URL('get_session_list', signer=url_signer),
        # sessions=sessions
    )

@action('get_session_list', method=["GET", "POST"])
@action.uses(db, auth.user, url_signer.verify())
def get_session_list():
    # My Enrolled Sessions (vue.js)
    sessions = db(db.attendance.email == get_user_email()).select().as_list()
    for s in sessions:
        session_info = db(db.session.id == s["session_id"]).select()
        for info in session_info:
            s["session_name"] = info.session_name
            s["owner"] = info.owner
            s["school"] = info.school
            s["term"] = info.term

            s["location"] = info.location
            s["description"] = info.description
            s["date"] = info.date
            s["starttime"] = info.starttime
            s["endtime"] = info.endtime

            # convert string Date to datetime object
            convertDate = datetime.datetime.strptime(s["date"], '%Y-%m-%d')
            # change date format
            changeDateFormat = convertDate.strftime("%Y%m%d")
            # s["calendar"] = 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + s["session_name"] + '&details=' + s["description"] + '&dates=' + changeDateFormat + 'T' + s["starttime"]+ '/' + changeDateFormat + 'T' + s["endtime"] + '&location=' + s["location"]

            s["class_name"] = info.class_name
            s["edit"] = URL('edit_session', s["id"], signer=url_signer)
            s["delete"] = URL('delete_session', s["id"], signer=url_signer)
    
    return dict(
        session_list = sessions,
        url_signer = url_signer,
        owner = get_user_id(),
    )