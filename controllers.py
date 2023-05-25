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
from .models import get_user_email
from pydal.validators import *

from py4web.utils.form import Form, FormStyleBulma

# Source: adding images - https://github.com/learn-py4web/star_ratings

url_signer = URLSigner(session)

def do_setup():
    db(db.images).delete()
    db.images.insert(image_url=URL('static', 'images/' + 'mainpageimage.png'))

@action('setup')
@action.uses(db)
def setup():
    do_setup()
    return "ok"


@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    # If the database is empty, sets it up.
    if db(db.images).count() == 0:
        do_setup()

    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
        get_images_url = URL('get_images', signer=url_signer)
    )

@action('get_images')
@action.uses(url_signer.verify(), db)
def get_images():
    """Returns the list of images."""
    return dict(images=db(db.images).select().as_list())


@action('find_session', method=["GET", "POST"])
@action.uses('find_session.html', db, session, auth.user, url_signer)
def find_session():
    # form = Form(db.auth_user, csrf_session=session, formstyle=FormStyleBulma)
    # if form.accepted:
    # We simply redirect; the insertion already happened
        # redirect(URL('index'))
    return dict(
        get_images_url = URL('get_images', signer=url_signer)
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
         Field('TA_or_Student_Led', label="TA/Tutor Attendance or Student Lead", requires = IS_IN_SET(['TA/Tutor', 'Student Lead'], zero=T('choose one'), error_message="Error: Choose One")),
         Field('Maximum_Number_of_Students', requires = IS_NOT_EMPTY())],
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
            official=form.vars["TA_or_Student_Led"],
            max_num_students=form.vars["Maximum_Number_of_Students"]
        )
        db.attendance.insert(
            email=get_user_email(),
            session_id=id
        )
        redirect(URL('create_session_results'))
    return dict(form=form,
                get_images_url = URL('get_images', signer=url_signer))

    # return dict(
    #     get_images_url = URL('get_images', signer=url_signer)
    # )

@action('create_session_results')
@action.uses('create_session_results.html', db, session, auth.user, url_signer)
def create_session():
    sessions = db(db.attendance.email == get_user_email()).select().as_list()
    for s in sessions:
        session_info = db(db.session.id == s["session_id"]).select()
        for info in session_info:
            s["session_name"] = info.session_name
            s["school"] = info.school
            s["term"] = info.term
            s["class_name"] = info.class_name
    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
        get_images_url = URL('get_images', signer=url_signer),
        sessions=sessions
    )
    # return dict(
    #     get_images_url = URL('get_images', signer=url_signer)
    # )
