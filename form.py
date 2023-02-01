from flask_wtf import FlaskForm

from wtforms import SelectField


class Form(FlaskForm):
    client_name = SelectField('client_name', choices=[])
    bill_no = SelectField('bill_no', choices=[])

