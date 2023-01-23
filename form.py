from flask_wtf import FlaskForm

from wtforms import SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from models import db, PaymentStatus, RecordStatus


class Form(FlaskForm):
    client_name = SelectField('client_name', choices=[])
    # status_name = SelectField('status_name', choices=[], default=[1])
    payment_status_name = QuerySelectField('payment_status_name',
                                           query_factory=PaymentStatus.fetch_names,
                                           get_pk=lambda a: a,
                                           get_label=lambda a: a)
    record_status_name = QuerySelectField('record_status_name',
                                          query_factory=RecordStatus.fetch_names,
                                          get_pk=lambda a: a,
                                          get_label=lambda a: a)
