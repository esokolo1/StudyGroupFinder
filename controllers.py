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
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
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
        sessions=sessions
    )

@action('create_session', method=["GET", "POST"])
@action.uses('create_session.html', db, auth.user)
def create_session():
    form = Form(
        [Field('Name', 'text'),
         Field('School', 'text'),
         Field('Term', 'text'),
         Field('Class_Name', 'text'),
         Field('Location', 'text'),
         Field('Description', 'text'),
         Field('TA_or_Student_Led', 'text'),
         Field('Maximum_Number_of_Students')],
         formstyle=FormStyleBulma,
         csrf_session=session
    )
    if form.accepted:
        id = db.session.insert(
            session_name=form.vars["Name"],
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
        redirect(URL('index'))
    return dict(form=form)