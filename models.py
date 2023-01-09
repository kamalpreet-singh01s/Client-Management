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
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone_no = db.Column(db.Numeric)
    address = db.Column(db.String(500))
    final_deal = db.Column(db.Float)
    gst = db.Column(db.Float)

    def __init__(self, customer_name, email, phone_no, address, final_deal, gst):
        self.customer_name = customer_name
        self.final_deal = final_deal
        self.email = email
        self.phone_no = phone_no
        self.address = address
        self.gst = gst


class Records(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer_name = db.relationship('Customer')
    content_advt = db.Column(db.String())
    date_of_order = db.Column(db.String(100))
    dop = db.Column(db.String(100))
    bill = db.Column(db.Numeric)
    bill_date = db.Column(db.String(100))
    # amount = db.Column(db.Float)
    # amount_received_date = db.Column(db.String(100))
    # pending_amount = db.Column(db.Float)
    #
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status_name = db.relationship('Status')

    filename = db.Column(db.String())
    # data = db.Column(db.LargeBinary)

    def __init__(self, customer_id, content_advt, date_of_order, dop, bill, bill_date,
                 status_id, filename=None, data=None):
        self.customer_id = customer_id
        self.content_advt = content_advt
        self.date_of_order = date_of_order
        self.dop = dop
        self.bill = bill
        self.bill_date = bill_date
        # self.amount = amount
        # self.amount_received_date = amount_received_date
        # self.pending_amount = pending_amount

        self.status_id = status_id

        self.filename = filename
        self.data = data


class Status(db.Model):
    __tablename__ = "status"
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(100))

    def __init__(self, status_name):
        self.status_name = status_name
