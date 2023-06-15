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
from pydal.validators import *
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user_id, get_time
import math

import datetime
import calendar

# Source: adding images - https://github.com/learn-py4web/star_ratings

url_signer = URLSigner(session)

# Home/Main Page
@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():

  return dict(
    get_session_list_url = URL('get_session_list', signer=url_signer),
    calendar_url = URL('calendar_url', signer=url_signer),
  )




# get_session_list - extract only sessions that user added/created 
# (used in create_session results page)
@action('get_session_list', method=["GET", "POST"])
@action.uses(db, auth.user, url_signer.verify())
def get_session_list():
  # db.attendance id match user's id
  sessions = db(db.attendance.user_id == get_user_id()).select().as_list()
  # check if db.session id match db.attendance session_id
  for s in sessions:
    session_info = db(db.session.id == s["session_id"]).select()
    for info in session_info:
      s["session_name"] = info.session_name
      s["owner"] = info.user_id
      s["school"] = 'tmp'#TODO:get school based on course_id
      s["term"] = 'tmp'#TODO
      s["open"] = info.session_is_open
      s["class_name"] = info.course_id#TODO:get course name
      s["location"] = info.session_location
      s["description"] = info.session_description
      s["date"] = info.session_days
      s["starttime"] = info.session_time
      s["endtime"] = info.session_time#TODO:use length instead
      s["announcement"] = 'tmp'#TODO:get announcement from post
      s["official"] = info.has_tas
      s["max_num_students"] = info.session_capacity
      s["num_students"] = 0#TODO:determine from attendance

      # convert string Date to datetime object
      convertDate = datetime.datetime.strptime(s["date"], '%Y-%m-%d')
      # change date format
      changeDateFormat = convertDate.strftime("%Y%m%d")
      # calendar - link to google calendar create events
      s["calendar"] = 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + s["session_name"] + '&details=' + s["description"] + '&dates=' + changeDateFormat + 'T' + s["starttime"]+ '/' + changeDateFormat + 'T' + s["endtime"] + '&location=' + s["location"]

      # edit_session html
      s["edit"] = URL('edit_session', s["id"], signer=url_signer)
      # delete session
      s["delete"] = URL('delete_session', s["id"], signer=url_signer)
      s["discussion"] =  URL('discussion', info.id, signer=url_signer)
      s["info_url"] = URL('info', s["session_id"], signer=url_signer)
  
  return dict(
    session_list = sessions,
    url_signer = url_signer,
    owner = get_user_id(),
  )

def session_dict(session_row):
  course = ''
  school = ''
  course_id = session_row.course_id
  if course_id is not None:
    course_row = db.course[course_id]
    school_row = db.school[course_row.school_id]
    course = course_string(course_row)
    school = school_row.school_name
  return dict(
    id=session_row.id,
    author=db.auth_user[session_row.user_id].email,
    school=school,
    course=course,
    name=session_row.session_name,
    desc=session_row.session_description,
    loc=session_row.session_location,
    days=session_row.session_days,
    time=session_row.session_time,
    len=session_row.session_length,
    start=session_row.session_start_date,
    end=session_row.session_end_date,
    cap=session_row.session_capacity,
    ta=session_row.session_has_tas,
    open=session_row.session_is_open,
  )
#
# find_session page - user can search sessions by class, school name etc

@action('find_session',method=['GET'])
@action.uses('find_session.html', auth.user, url_signer)
def find_session():
  # Get the user ID
  user_id = auth.current_user.get('id')
  # Retrieve the list of sessions from the database
  sessions = db().select(db.session.ALL)

  # Check if the user is enrolled in each session
  for session in sessions:
    enrollment = db(
      (db.session_enrollment.user_id == user_id) &
      (db.session_enrollment.session_id == session.id)
    ).select().first()

      # Set the enrollment status for the session
    session.is_enrolled = bool(enrollment)

      # Print the value of is_enrolled for each session
      # print(f"Session {session.id} - is_enrolled: {session.is_enrolled}")

  # Print the content of sessions
  # print(sessions)

  return dict(
    sessions=sessions,
    remove_session_url=URL('remove_session', signer=url_signer),
    enroll_session_url=URL('enroll_session', signer=url_signer),
    search_sessions_url = URL('search_sessions', signer=url_signer),
    get_courses_url= URL('get_courses', signer=url_signer),
    get_enrolled_schools_url=URL('get_enrolled_schools',
    signer=url_signer),
    get_enrolled_sessions_url=URL('get_enrolled_sessions',
                                    signer=url_signer),
  )

@action('search_sessions',method=['POST'])
@action.uses(db, auth.user, url_signer.verify())
def search_sessions():
  session_results = []
  search_query = request.json.get('search_query')
  course_list = request.json.get('courses')
  is_open = request.json.get('open')
  has_tas = request.json.get('ta')
  location_query = request.json.get('loc')
  before_time = request.json.get('before')
  after_time = request.json.get('after')
  if before_time and len(before_time)==5: before_time += ':00'
  if after_time and len(after_time)==5: after_time += ':00'
  days = request.json.get('days')
  db_query = True
  for k in search_query.split():
    db_query &= (
      db.session.session_name.like('%'+k+'%') |
      db.session.session_description.like('%'+k+'%')
    )
  if len(course_list) > 0:
    course_filter = False
    for course in course_list:
      course_filter |= (db.session.course_id==course['id'])
    db_query &= course_filter
  if is_open: db_query &= (db.session.session_is_open==True)
  if has_tas: db_query &= (db.session.session_has_tas==True)
  db_query &= db.session.session_location.like('%'+location_query+'%')
  if before_time: db_query &= (db.session.session_time<before_time)
  if after_time: db_query &= (db.session.session_time>after_time)
  if len(days) > 0:
    days_filter = True
    for day in days:
      days_filter &= ((db.session.session_days%pow(2,day+1))/pow(2,day)==1)
    db_query &= days_filter
  session_rows = db(db_query).select(orderby=db.session.session_time)
  # Get the user ID
  for session_row in session_rows:
      session_results.append(session_dict(session_row))
  return dict(session_results=session_results)

@action('info/<id:int>')
@action.uses('info.html', db, auth.user)
def info(id):
  session = db(db.session.id == id).select().as_list()[0]
  get_session_list_url = URL('get_session_list', signer=url_signer)
  get_comments_url = URL('get_comments', signer=url_signer)
  add_comment_url = URL('add_comment', signer=url_signer)
  return dict(session=session, get_session_list_url=get_session_list_url, get_comments_url=get_comments_url, add_comment_url=add_comment_url)

@action('get_comments')
@action.uses(db, auth.user, url_signer.verify())
def get_comments():
  id = request.params.get("id")
  comments = db(db.comment.session_id == id).select().as_list()
  comments.reverse()
  return dict(comments=comments)

@action("add_comment", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_reply():
  id = request.json.get("id")
  comment = request.json.get("new_comment")
  db.comment.insert(session_id=id, comment_content=comment, comment_timestamp=get_time().isoformat())
  return "ok"

def course_string(course_row):
  return (
    course_row.course_subject + ' ' +
    course_row.course_number + ' ' +
    (course_row.course_title or '')
  )


@action('get_schools', method=['GET'])
@action.uses(db, url_signer.verify())
def get_schools():
  search_query = request.params.get('query') or ''
  search_query = search_query.lower()
  db_query = (
    db.school.school_name.lower().like('%'+search_query+'%') |
    db.school.school_abbr.lower().like('%'+search_query+'%')
  )
  school_list = [
    dict(id=row.id, name=row.school_name)
    for row in db(db_query).select()
  ]
  return dict(r=school_list)

@action('get_courses', method=['GET'])
@action.uses(db, auth.user, url_signer.verify())
def get_course_list():
  search_query = request.params.get('query') or ''
  search_query = search_query.lower()
  db_query = (
    db.course.course_subject.lower().like('%'+search_query+'%') |
    db.course.course_number.lower().like('%'+search_query+'%') |
    db.course.course_title.lower().like('%'+search_query+'%')
  )
  course_list = [
    dict(id=row.id, name=course_string(row))
    for row in db(db_query).select()
  ]
  return dict(r=course_list)

@action('get_enrolled_schools', method=['GET'])
@action.uses(db, auth, auth.user, url_signer.verify())
def get_enrolled_schools():
  enrolled_schools = [
    dict(id=s.school_id, name=db.school[s.school_id].school_name)
    for s in db(db.school_enrollment.user_id==get_user_id()).select()
  ]
  return dict(r=enrolled_schools)

@action('get_enrolled_courses', method=['GET'])
@action.uses(db, auth, auth.user, url_signer.verify())
def get_enrolled_courses():
  enrolled_courses = [
    dict(id=c.course_id, name=course_string(db.course[c.course_id]))
    for c in db(db.course_enrollment.user_id==get_user_id()).select()
  ]
  return dict(r=enrolled_courses)


@action('get_enrolled_sessions', method=['GET'])
@action.uses(db, auth, auth.user, url_signer.verify())
def get_enrolled_sessions():
  query = db(db.session_enrollment.user_id == get_user_id()).select()
  print(str(query))  # Print the query
  enrolled_sessions = [
    dict(id=es.session_id,
      name=db.session[es.session_id].session_name,
      location=db.session[es.session_id].session_location,
      ta=db.session[es.session_id].session_has_tas,
      time=db.session[es.session_id].session_time,
      len=db.session[es.session_id].session_length,
      days= db.session[es.session_id].session_days,
      start= db.session[es.session_id].session_start_date,
      end= db.session[es.session_id].session_end_date,
      info=URL('info', es.session_id, signer=url_signer),
      open = db.session[es.session_id].session_is_open,
      )
    for es in query
  ]
  return dict(r=enrolled_sessions)


# MY_SESSIONS controllers
@action('my_sessions')
@action.uses('my_sessions.html', auth.user, url_signer)
def my_sessions():
  return dict(
    get_enrolled_sessions_url=URL('get_enrolled_sessions',
      signer=url_signer),
      remove_session_url=URL('remove_session', signer=url_signer),
  )

@action('remove_session', method=['POST'])
@action.uses(db, auth, auth.user, url_signer.verify())
def remove_session():
  session_id = int(request.json.get('session_id'))
  user_id = int(auth.current_user.get('id'))
  # print(str(session_id))
  # Check if the current user is the session creator
  session = db.session(session_id)
  if session and session.user_id == user_id:
    # User is the session creator, delete the entire session
    db(db.session.id == session_id).delete()
    db(db.session_enrollment.session_id == session_id).delete()
  else:
    # User is not the session creator, un-enroll the student from the session
    db((db.session_enrollment.session_id == session_id) & (db.session_enrollment.user_id == user_id)).delete()

  user_id = int(auth.current_user.get('id'))

  db((db.session_enrollment.session_id == session_id) & (db.session_enrollment.user_id == user_id)).delete()
  return "Session removed successfully"

@action('enroll_session', method=['POST'])
@action.uses(db, auth, auth.user, url_signer.verify())
def enroll_session():
  session_id = int(request.json.get('session_id'))
  user_id = int(auth.current_user.get('id'))
  # Check if the session exists
  session = db.session(session_id)
  if session:
    # Check if the user is already enrolled in the session
    enrollment = db(
      (db.session_enrollment.session_id == session_id) &
      (db.session_enrollment.user_id == user_id)
    ).select().first()

    if not enrollment:
      # User is not already enrolled, create a new enrollment record
      db.session_enrollment.insert(session_id=session_id, user_id=user_id)
      return "Session enrolled successfully"  # Return a response indicating successful enrollment
  return "User already in sesssion"





# Dashboard - user can check all study session schedule
@action('dashboard', method=["GET", "POST"])
@action.uses('dashboard.html',db, auth.user, url_signer)
def dashboard():
  return dict(
    get_session_list_url = URL('get_session_list', signer=url_signer),
    calendar_url = URL('calendar_url', signer=url_signer),
    events_url = URL('events_url', signer=url_signer),
  )

# Calendar - used in dashboard page, always displays this month calendar,
#            Clicking left/right arrow displays prev/next month calendar
@action('calendar_url')
@action.uses(db, auth.user, url_signer.verify())
def calendar_url():
  # calendar - starts from Sun Mon Tues, etc
  calendar.setfirstweekday(calendar.SUNDAY)
  # if user clicks left/right arrow, get which calendar month user wants to check
  month = request.params.get("month")
  # if user clicks left/right arrow, get which calendar year user wants to check
  year = request.params.get("year")
  # if user clicks left/right arrow:
  if (month != None):
    # display calendar user wants to see
    month = int(month)
    year = int(year)
    # month_name (ex. "June", "July")
    month_name = calendar.month_name[month]
    # weeks - get a matrix representing month's calendar
    weeks = calendar.monthcalendar(year,month)
  else:
    # if request.params returns None (hasn't clicked left/right arrow yet)
    # display this month calendar
    # get today's date, month, month_name and year
    todayDate = datetime.datetime.now()
    month = todayDate.month
    month_name = calendar.month_name[month]
    year = todayDate.year
    # weeks - get a matrix representing month's calendar
    weeks = calendar.monthcalendar(year,month)
  return dict(weeks = weeks, month=month, year=year, month_name = month_name)

# events_url - used in dashboard page, user can check upcoming sessions schedule
@action('events_url')
@action.uses(db, auth.user, url_signer.verify())
def events_url():
  events_list = []
  # all_sessions - db.session
  all_sessions = db(db.session).select().as_list()
  for each in all_sessions:
    convertedDate = each["session_start_date"]
    # what user clicked on calendar
    clickedDate = datetime.datetime(int(request.params.get("year")), int(request.params.get("month")), int(request.params.get("date")))
    clickedDate = clickedDate.date()
    week_days = ['Sunday', 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    if (each["session_start_date"] == clickedDate and each["session_end_date"] == clickedDate):
      events_list.append(each)
    # if session_start_date <= what user clicked on Calendar
    elif (each["session_start_date"] <= clickedDate):
      # if session_end_date is None OR session_end_date >= what user clicked on Calendar
      if (each["session_end_date"] == None or each["session_end_date"] >= clickedDate):
        # convert db.session.session_days to string (4 -> Monday, 12 -> Tuesday, Wednesday)
        days_list = []
        n = int(each["session_days"])
        for i in range(0, 7):
          if (n % 2):
            days_list.append(week_days[i])
          n = math.floor(n / 2)
        # check days that user clicked on calendar match each session_days
        for abc in days_list:
          if (clickedDate.strftime('%A') == abc):
            # add to events_list
            events_list.append(each)
  return dict(events_list = events_list)
