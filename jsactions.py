"""
actions for fetching & writing to database via javascript
"""
from py4web import action, request, URL
from .common import db, auth
from .models import get_user_id, get_time
from .controllers import url_signer

# TODO:move to models
# add new defaults to models for session
from datetime import datetime
def get_date():
  return datetime.now()

"""params:
  fetch_schools=  id:school_id, query:str, my:bool,
  enroll_school=  id:school_id, enroll:bool,
  fetch_courses=  id:course_id, query:str, my:bool, school_id:school_id,
  enroll_course=  id:course_id, enroll:bool, ta:bool, tutor:bool,
  fetch_sessions= query:str, loc:str, course_ids:list:course_id,
                  ta:bool, before:time, after:time, days:int,
  write_sessions= id:session_id, course_id:course_id,
                  name:str, desc:text, loc:str, days:list:week_days,
                  time:time, length:int, start:date, end:date,
                  cap:int, ta:bool,
  attend_session= id:session_id, attend:bool,
  fetch_posts=    feed:str, id:session_id,
  write_post=     id:post_id, content:text, is_ann:bool,
  fetch_profile=
  write_profile=  first:str, last:str, desc:text,
"""

################################################################

def school_dict(school_row):
  enrolled = False
  if auth.current_user and db(
    (db.school_enrollment.user_id == get_user_id())
    & (db.school_enrollment.school_id == school_row.id)
  ).select().first():
    enrolled = True
  return dict(
    id=school_row.id,
    name=school_row.school_name,
    abbr=school_row.school_abbr,
    enrolled=enrolled,
  )

@action('fetch_schools')
@action.uses(db, auth, url_signer.verify())
def fetch_schools():
  schools = []
  params = request.params
  school_id = params.get('id')
  query_str = params.get('query')
  fetch_enrolled = params.get('my')

  # construct the database query
  db_query = True
  if school_id:
    # fetch a single school
    db_query = db.school.id == school_id
  elif query_str:
    # fetch schools whose name or abbr match the query
    db_query = (
      db.school.school_name.like('%' + query_str + '%')
      | db.school.school_abbr.like('%' + query_str + '%')
    )
  elif fetch_enrolled and auth.current_user:
    # schools user is enrolled in
    db_enrolled_query = db.school.id == -1
    for enrolled_school in db(
      db.school_enrollment.user_id == get_user_id()
    ).select():
      db_enrolled_query |= db.school.id == enrolled_school.school_id
    db_query &= db_enrolled_query

  # get data
  school_rows = db(db_query).select(db.school.ALL)
  for school_row in school_rows:
    schools.append(school_dict(school_row))

  return dict(schools=schools)

@action('enroll_school')
@action.uses(db, auth.user, url_signer.verify())
def enroll_school():
  params = request.params
  school_id = params.get('id')
  enroll = params.get('enroll')
  if not school_id: return
  if enroll:
    print('enrolled')
    db.school_enrollment.update_or_insert(
      user_id=get_user_id(),
      school_id=school_id,
    )
  else:
    db(
      (db.school_enrollment.user_id == get_user_id())
      & (db.school_enrollment.school_id == school_id)
    ).delete()
    print('uninreolld')
  return 'OK'

################################################################

def course_dict(course_row):
  enrolled = False
  if auth.current_user and db(
    (db.course_enrollment.user_id == get_user_id())
    & (db.course_enrollment.course_id == course_row.id)
  ).select().first():
    enrolled = True
  school = school_dict(db.school[course_row.school_id])
  return dict(
    id=course_row.id,
    subject=course_row.course_subject,
    num=course_row.course_number,
    title=course_row.course_title,
    desc=course_row.course_description,
    school=school,
    enrolled=enrolled,
  )

@action('fetch_courses')
@action.uses(db, auth, url_signer.verify())
def fetch_courses():
  courses = []
  params = request.params
  course_id = params.get('id')
  query_str = params.get('query')
  fetch_enrolled = params.get('my')
  school_id = params.get('school_id')

  # construct the database query
  db_query = True
  if course_id:
    # fetch a single course
    db_query = db.course.id == course_id
  elif query_str:
    # fetch courses whose field(s) match the query
    db_query = (
      db.course.course_title.like('%' + query_str + '%')
      | db.course.course_subject.like('%' + query_str + '%')
      | db.course.course_number.like('%' + query_str + '%')
      | db.course.course_description.like('%' + query_str + '%')
    )
  elif fetch_enrolled and auth.current_user:
    # courses user is enrolled in
    db_enrolled_query = db.course.id == -1
    for enrolled_course in db(
      db.course_enrollment.user_id == get_user_id()).select():
      db_enrolled_query |= db.course.id == enrolled_course.course_id
    db_query &= db_enrolled_query
  if school_id:
    # restrict to courses belonging to a certain school
    db_query &= db.course.school_id == school_id

  # get data
  course_rows = db(db_query).select(db.course.ALL)
  for course_row in course_rows:
    courses.append(course_dict(course_row))

  return dict(courses=courses)

@action('enroll_course')
@action.uses(db, auth.user, url_signer.verify())
def enroll_course():
  params = request.params
  course_id = params.get('id')
  enroll = params.get('enroll')
  is_ta = params.get('ta') or False
  is_tutor = params.get('tutor') or False
  if course_id is None: return
  if enroll:
    db.course_enrollment.update_or_insert(
      user_id=get_user_id(),
      course_id=course_id,
      enrollment_is_ta=is_ta,
      enrollment_is_tutor=is_tutor,
    )
  else:
    db(
      (db.course_enrollment.user_id == get_user_id())
      & (db.course_enrollment.course_id == course_id)
    ).delete()
  return 'OK'

################################################################

week = [
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
]

def session_dict(session_row):
  course = dict()
  school = dict()
  days_list = []
  attending = False
  course_id = session_row.course_id
  course = None
  if course_id is not None:
    course = course_dict(db.course[course_id])
  days_int = session_row.session_days
  for i in range(len(week)):
    if days_int % pow(2, i + 1) // pow(2, i):
      days_list.append(week[i])
  if auth.current_user and db(
    (db.attendance.user_id == get_user_id())
    & (db.attendance.session_id == session_row.id)
  ).select().first():
    attending = True
  return dict(
    id=session_row.id,
    author=db.auth_user[session_row.user_id].email,
    course=course,
    name=session_row.session_name,
    desc=session_row.session_description,
    loc=session_row.session_location,
    days=days_list,
    time=session_row.session_time,
    len=session_row.session_length,
    start=session_row.session_start_date,
    end=session_row.session_end_date,
    cap=session_row.session_capacity,
    ta=session_row.session_has_tas,
    open=session_row.session_is_open,
    attending=attending,
  )

@action('fetch_sessions')
@action.uses(db, auth, url_signer.verify())
def fetch_sessions():
  sessions = []
  params = request.params
  session_id = params.get('id')
  session_row = session_id and db.session[session_id]
  if session_row:
    return dict(session=session_dict(session_row))
  query_str = params.get('query')
  loc_str = params.get('loc')
  course_ids = params.get('course_ids')
  ta = params.get('ta')
  before = params.get('before')
  after = params.get('after')
  days = params.get('days')

  # build query
  db_query = db.session
  if query_str:
    for k in query_str.split():
      db_query &= (
        db.session.session_name.like('%' + k+'%')
        | db.session.session_description.like('%' + k+'%')
      )
  # filtering
  if loc_str:
    db_query &= db.session_location.like('%' + loc_str + '%')
  if course_ids:
    course_filter = False
    for course_id in course_ids:
      course_filter |= db.session_course_id == course_id
    db_query &= course_filter
  if ta:
    db_query &= db.session.session_has_tas == True
  if before:
    before = (before + ':00')[:8]
    db_query &= db.session_time < before
  if after:
    after = (before + ':00')[:8]
    db_query &= db.session_time > after
  if days:
    day_filter = True
    for day in days:
      days_filter &= (
        db.session.session_days % pow(2, day + 1) / pow(2, day) == 1
      )
    db_query &= days_filter

  # get data
  session_rows = db(db_query).select(
    db.session.ALL,
    orderby=db.session.session_time
  )
  for session_row in session_rows:
    sessions.append(session_dict(session_row))

  return dict(sessions=sessions)

@action('attend_session')
@action.uses(db, auth.user, url_signer.verify())
def attend_session():
  params = request.params
  session_id = params.get('id')
  attend = params.get('attend')
  session_row = session_id and db.session[session_id]
  if session_row is None: return
  db_query = (
    (db.attendance.user_id == get_user_id())
    & (db.attendance.session_id == session_id)
  )
  if attend:
    db.attendance.update_or_insert(
      db_query,
      session_id=session_id
    )
    # if a TA for this course joins the session, make it offical
    course_enrollment_row = db(
      (db.course_enrollment.user_id == get_user_id())
      & (db.course_enrollment.course_id == session_row.course_id)
    ).select().first()
    if course_enrollment_row and course_enrollment_row.enrollment_is_ta:
      session_row.update_record(session_has_tas=True)
  else: # remove any attendance entries
    db(db_query).delete()
    # TODO: remove official status if no TAs in the session?
  return 'OK'

@action('write_session', method=['POST'])
@action.uses(db, auth.user, url_signer.verify())
def write_session():
  params = request.json
  session_id = params.get('id')
  session_row = session_id and db.session[session_id]
  user_id = session_row and session_row.user_id
  if session_id and user_id != get_user_id():
    # non-author should not edit existing session
    return
  delete_session = params.get('del')
  if session_row and delete_session:
    session_row.delete_record()
    return dict(url=URL('session'))
  course_id = params.get('course_id')
  name = params.get('name')
  desc = params.get('desc')
  loc = params.get('loc')
  days_list = params.get('days') or []
  days_int = 0
  for day in days_list:
    if day in week:
      days_int += pow(2, week.index(day))
  time = params.get('time')
  length = params.get('length')
  start = params.get('start')
  end = params.get('end')
  cap = params.get('cap')
  ta = params.get('ta') or False
  # TODO: tutor?

  session = dict(
    course_id=course_id,
    session_name=name,
    session_description=desc,
    session_location=loc,
    session_days=days_int,
    session_time=time,
    session_length=length,
    session_start_date=start,
    session_end_date=end,
    session_capacity=cap,
    session_has_tas=ta,
  )

  if session_row: # perform an edit
    session_row.update_record(**session)
  else:
    # create new session
    session_id = db.session.insert(**session)
    # automatically add this user as an attendee
    db.attendance.insert(session_id=session_id)
    return dict(url=URL('session',session_id))

'''
################################################################

@action('fetch_posts')
@action.uses(db, auth, url_signer.verify())
def fetch_posts():
  posts = []
  params = request.params
  feed = params.get('feed')
  session_id = params.get('id')

  # build the query
  db_query = False
  if feed == 'session' and session_id:
    # get posts for specific session
    db_query = db.session_id == session_id
  elif auth.current_user is None:
    # not logged in, get all recent posts
    db_query = True
  elif feed == 'my_schools':
    # posts for sessions for schools user is enrolled in
    for school_enrollment_row in db(
      db.school_enrollment.user_id == get_user_id()
    ).select():
      for course_row in db(
        db.course.school_id == school_enrollment_row.school_id
      ).select():
        for session_row in db(
          db.session_course_id == course_row.id
        ).select():
          db_query |= db.post_session_id == session_row.id
  elif feed == 'my_courses':
    # posts for sessions for courses user is enrolled in
    for course_enrollment_row in db(
      db.course_enrollment.user_id == get_user_id()
    ).select():
      for session_row in db(
        db.session.course_id == course_enrollment_row.course_id:
      ).select():
        db_query |= db.post.session_id == session_row.id
  else: # feed == 'my_sessions'
    # posts for sessions user is attending
    for attendance_row in db(
      db.attendance.user_id == get_user_id()
    ).select():
      db_query |= db.post.session_id == attendance_row.session_id

  # get data
  for post_row in db(db_query).select(
    db.post.ALL,
    orderby=~db.post.post_timestamp,
    limitby=(0, 20),
  ):
    session_row = db.session[post_row.session_id]
    course_row = db.course[session_row.course.id]
    posts.append(dict(
      author='anon', # TODO: add post author in models.py
      content=post_row.post_content,
      timestamp=post_row.post_timestamp.isoformat(),
      is_ann=post_row.post_is_announcement,
      session=session_dict(session_row),
      course=course_dict(course_row),
    ))

  return dict(posts=posts)

@action('write_post', method=['POST'])
@action.uses(db, auth.user, url_signer.verify())
def write_post():
  params = request.json
  post_id = params.get('id')
  post_row = post_id and db.post[post_id]
  if post_row.user_id != get_user_id():
    # non-author should not edit another's post
    return
  content = params.get('content')
  is_ann = params.get('is_ann')
  post = dict(
    post_content=content,
    post_is_announcement=is_ann,
  )
  if post_row:
    post_row.update_record(**post)
  else:
    db.post.insert(**post)
  return 'OK'
'''

################################################################

# TODO: fetching & writing comments

################################################################

@action('fetch_profile')
@action.uses(db, auth.user, url_signer.verify())
def fetch_profile():
  email = auth.current_user.get('email')
  first = auth.current_user.get('first_name')
  last = auth.current_user.get('last_name')
  profile_row = db.profile[get_user_id()]
  desc = profile_row.profile_description if profile_row else ''
  return dict(
    email=email,
    first=first,
    last=last,
    desc=desc,
  )

@action('write_profile', method=['POST'])
@action.uses(db, auth.user, url_signer.verify())
def write_profile():
  params = request.json
  first = params.get('first')
  last = params.get('last')
  desc = params.get('desc')
  db.auth_user[get_user_id()].update_record(
    first_name=first,
    last_name=last
  )
  db.profile.update_or_insert(
    db.profile.user_id == get_user_id(),
    profile_description=desc,
  )
  return 'OK'
