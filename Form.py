from flask_wtf import FlaskForm

from wtforms import SelectField


class Form(FlaskForm):
    customer_name = SelectField('customer_name', choices=[])
    status_name = SelectField('status_name', choices=[])


