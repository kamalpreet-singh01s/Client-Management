from flask_wtf import FlaskForm

from wtforms import SelectField


class Form(FlaskForm):
    client_name = SelectField('client_name', choices=[])
    status_name = SelectField('status_name', choices=[], default=[1])


