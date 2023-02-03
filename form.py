from flask_wtf import FlaskForm

from wtforms import SelectField
from models import db, Gst
from wtforms_sqlalchemy.fields import QuerySelectField


class Form(FlaskForm):
    client_name = SelectField('client_name', choices=[])
    bill_no = SelectField('bill_no', choices=[])
    gst = QuerySelectField(
        query_factory=Gst.fetch_names,
        get_pk=lambda a: a,
        get_label=lambda a: a)
