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
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_id
from pydal.validators import *

import datetime
# from datetime import datetime
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


@action('create_session', method=["GET", "POST"])
@action.uses('create_session.html', db, session, auth.user, url_signer)
def create_session():
    form = Form(
        [Field('Session_Name', requires = IS_NOT_EMPTY(error_message="Error: Enter Study Group Session Name")),
         Field('School', requires = IS_NOT_EMPTY(error_message="Error: Enter School Name")),
         Field('Term', requires = IS_IN_SET(['Spring 2023','Summer 2023', 'Fall 2023', 'Winter 2024'])), # requires = IS_NOT_EMPTY(error_message="Error: Enter Term (ex. Spring 2023)")), 
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
    return dict(form=form)


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
            Field('Term', requires = IS_IN_SET(['Spring 2023','Summer 2023', 'Fall 2023', 'Winter 2024'])), # requires = IS_NOT_EMPTY(error_message="Error: Enter Term (ex. Spring 2023)")), 
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

@action('find_session', method=["GET", "POST"])
@action.uses('find_session.html', db, session, auth.user, url_signer)
def find_session():

    return dict(
        get_session_list_url = URL('get_session_list', signer=url_signer),
        search_url=URL('search', signer=url_signer),
        enroll_session_url=URL('enroll_session', signer=url_signer),
    )


@action('search')
@action.uses(db, auth.user, url_signer.verify())
def search():
    school = request.params.get("school") # what I typed in search bar
    term = request.params.get("term")
    status = request.params.get("status")
    open_status = "True"
    if status == "Open": 
        open_status = "True"
    elif status == "Closed":
        open_status = "False"
    class_name = request.params.get("class_name")
    location = request.params.get("location")
    meeting_date = request.params.get("meeting_date")
    meeting_start = request.params.get("meeting_start")
    meeting_end = request.params.get("meeting_end")
    ta = request.params.get("ta")

    # ONLY display sessions that user who is logged in NOT ENROLLED YET
    # List of sessions that user who is logged in NOT ENROLLED YET
    session_list_not_enrolled = []
    attendance_list = db(db.attendance).select().as_list()
    session_list = db(db.session).select().as_list()
    for each_session in session_list:
        email_list = []
        for each_attendance in attendance_list:
            # if db.session id == db attendance session_id
            if (each_session["id"] == each_attendance["session_id"]):
                # add all attendance user email to email_list
                email_list.append(each_attendance["email"])
        # if there is NO user who is logged in in the email list -> user is not enrolled in that session yet
        if (get_user_email() not in email_list):
            # add that session to "session_list_not_enrolled" list
            session_list_not_enrolled.append(each_session)

    # rename session_list_not_enrolled list to "session_list"
    session_list = session_list_not_enrolled

    # search results
    results = []
    for r in session_list:
        # str(school) -> what user typed in search bar
        # r["school"] -> iterate through list of sessions, only extract school name
        # if r['school'] contains what user typed in search bar, append to results list
        # .lower() -> convert search input to lowercase

        # ADD CODE HERE (term, status, classname, location, meeting date, starttime, endtime, attendance)

        if (len(str(meeting_start)) > 0):
            start_hr = int(meeting_start[:2])
            start_m = int(meeting_start[3:5]);
        official_start_hr = int((r['starttime'])[:2])
        official_start_m = int(r['starttime'][3:5])

        if (len(str(meeting_end)) > 0):
            end_hr = int(meeting_end[:2])
            end_m = int(meeting_end[3:5])
        # print(len(str(meeting_end)))
        official_end_hr = int(r['endtime'][:2])
        official_end_m = int(r['endtime'][3:5])

        actual_end_m = official_end_m
        if official_end_m == 0:
            actual_end_m = 60

        if (str(school).lower() in r['school'].lower()):
            if (str(term).lower() in r['term'].lower()):
                if(open_status == r['open']):
                    if (str(class_name).lower() in r['class_name'].lower()):
                        if (str(location).lower() in r['location'].lower()):
                            if (str(meeting_date).lower() in r['date'].lower()):
                                # if there is a start and end time 
                                if ((len(str(meeting_start)) > 0) & (len(str(meeting_end)) > 0)):
                                     if ((start_hr >= official_start_hr) & (start_m >= official_start_m)):
                                         # checks that choosen start time is before the official meetings end time
                                        if ((start_hr < official_end_hr) & (start_m <= actual_end_m)):
                                            # checks that choosen end time is before or same as official end time
                                            if ((end_hr <= official_end_hr) & (end_m <= actual_end_m)):
                                                # checks that choosen end time is after the official start time 
                                                if ((end_hr >= official_start_hr) & (end_m >= official_start_m)):
                                                    if(str(ta) in r['official']):
                                                        results.append(r)
                                # if there is a start time 
                                elif ((len(str(meeting_start)) > 0)):
                                    # checks that choosen start time is same or after official meetings start time
                                    if ((start_hr >= official_start_hr) & (start_m >= official_start_m)):
                                         # checks that choosen start time is before the official meetings end time
                                        if ((start_hr < official_end_hr) & (start_m <= actual_end_m)):
                                            if(str(ta) in r['official']):
                                                    results.append(r)
                                # if there is an end time 
                                elif (len(str(meeting_end)) > 0):
                                        # checks that choosen end time is before or same as official end time 
                                        if ((end_hr <= official_end_hr) & (end_m <= actual_end_m)):
                                            # checks that choosen end time is after the official start time 
                                            if ((end_hr >= official_start_hr) & (end_m >= official_start_m)):
                                                if(str(ta) in r['official']):
                                                    results.append(r)
                                # if there are no start or end time 
                                else:
                                    if(str(ta) in r['official']):
                                        results.append(r)
    
    return dict(results=results,
                session_list=session_list)
