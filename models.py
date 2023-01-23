import enum

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import DevelopmentConfig

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    # config development configuration for flask app
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone_no = db.Column(db.String(100))
    password = db.Column(db.String())

    def __init__(self, username, firstname, last_name, email, phone_no, password):
        self.username = username
        self.first_name = firstname
        self.last_name = last_name
        self.email = email
        self.phone_no = phone_no
        self.password = password


class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone_no = db.Column(db.String(100))
    address = db.Column(db.String(500))
    final_deal = db.Column(db.Float)
    gst = db.Column(db.Float)

    def __init__(self, client_name, email, phone_no, address, final_deal, gst):
        self.client_name = client_name
        self.final_deal = final_deal
        self.email = email
        self.phone_no = phone_no
        self.address = address
        self.gst = gst


class Status(enum.Enum):
    draft = "Draft"
    received = "Received"
    cancelled = "Cancelled"

    @staticmethod
    def fetch_names():
        return [c.value for c in Status]


class Records(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client_name = db.relationship('Client')
    content_advt = db.Column(db.String())
    date_of_order = db.Column(db.String(100))
    dop = db.Column(db.String(100))
    bill = db.Column(db.String())
    bill_date = db.Column(db.String(100))

    amount_received_date = db.Column(db.String(100))

    # status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    # status_name = db.relationship('Status')
    status = db.Column(
        db.Enum(Status, values_callable=lambda x: [str(stat.value) for stat in Status]))

    filename = db.Column(db.String())

    def __init__(self, client_id, content_advt, date_of_order, dop, bill, bill_date,
                 status=status, filename=None, amount_received_date=None):
        self.client_id = client_id
        self.content_advt = content_advt
        self.date_of_order = date_of_order
        self.dop = dop
        self.bill = bill
        self.bill_date = bill_date
        self.amount_received_date = amount_received_date
        # self.status_id = status_id
        self.status = status

        self.filename = filename

# class Status(db.Model):
#     __tablename__ = "status"
#     id = db.Column(db.Integer, primary_key=True)
#     status_name = db.Column(db.String(100))
#
#     def __init__(self, status_name):
#         self.status_name = status_name
