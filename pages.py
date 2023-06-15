"""
actions for each page/app
"""
from py4web import action, redirect, URL
from .common import db, auth, session
from .models import get_user_id
from .controllers import url_signer
from .jsactions import week

"""urls:
    fetch_schools_url=URL('fetch_schools', signer=url_signer),
    enroll_school_url=URL('enroll_school', signer=url_signer),
    fetch_courses_url=URL('fetch_courses', signer=url_signer),
    enroll_course_url=URL('enroll_course', signer=url_signer),
    fetch_sessions_url=URL('fetch_sessions', signer=url_signer),
    write_session_url=URL('write_session', signer=url_signer),
    attend_session_url=URL('attend_session', signer=url_signer),
    fetch_posts_url=URL('fetch_posts', signer=url_signer),
    write_post_url=URL('write_post', signer=url_signer),
    fetch_profile_url=URL('fetch_profile', signer=url_signer),
    write_profile_url=URL('write_profile', signer=url_signer),
"""

################################################################

@action('profile')
@action.uses('profile.html', auth.user, url_signer)
def profile():
  return dict(
    fetch_schools_url=URL('fetch_schools', signer=url_signer),
    enroll_school_url=URL('enroll_school', signer=url_signer),
    fetch_courses_url=URL('fetch_courses', signer=url_signer),
    enroll_course_url=URL('enroll_course', signer=url_signer),
    fetch_profile_url=URL('fetch_profile', signer=url_signer),
    write_profile_url=URL('write_profile', signer=url_signer),
  )

@action('session')
@action('session/<session_id:int>')
@action.uses('session.html', db, auth, url_signer)
def session(session_id=0):
  editable = False
  if session_id > 0:
    session_row = db.session[session_id]
    if session_row is None: # session does not exist
      redirect(URL('session'))
    # if looking at an existing session,
    # session is editable if user is session's author
    editable = session_row.user_id == get_user_id()
  elif auth.current_user:
    # logged-in useer may create a new session
    editable = True
  return dict(
    week=week,
    session_id=session_id,
    editable=editable,
    fetch_courses_url=URL('fetch_courses', signer=url_signer),
    fetch_sessions_url=URL('fetch_sessions', signer=url_signer),
    attend_session_url=URL('attend_session', signer=url_signer),
    write_session_url=URL('write_session', signer=url_signer),
  )
