from flask_wtf import FlaskForm

from wtforms import SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from models import db, Status


class Form(FlaskForm):
    client_name = SelectField('client_name', choices=[])
    # status_name = SelectField('status_name', choices=[], default=[1])
    status_name = QuerySelectField('status_name',
                                   query_factory=db.Status.fetch_names,
                                   get_pk=lambda a: a,
                                   get_label=lambda a: a)
