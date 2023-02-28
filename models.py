import enum

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    # config development configuration for flask app
    app.config.from_object(ProductionConfig)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


class PaymentStatus(enum.Enum):
    draft = "Draft"
    approved = "Approved"
    cancelled = "Cancelled"

    @staticmethod
    def fetch_names():
        return [c.value for c in PaymentStatus]


class SalesOrderStatus(enum.Enum):
    pending = "Pending"
    received = "Received"
    cancelled = "Cancelled"

    @staticmethod
    def fetch_names():
        return [c.value for c in SalesOrderStatus]


class Gst(enum.Enum):
    percent_5 = 5
    percent_12 = 12
    percent_18 = 18
    percent_28 = 28

    @staticmethod
    def fetch_names():
        return [c.value for c in Gst]


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

    credit_amount = db.Column(db.Float, default=0.0)
    overall_payable = db.Column(db.Float)
    overall_received = db.Column(db.Float)

    def __init__(self, client_name, email, phone_no, address,overall_payable,overall_received, credit_amount=None):
        self.client_name = client_name

        self.email = email
        self.phone_no = phone_no
        self.address = address
        self.overall_payable = overall_payable
        self.overall_received = overall_received

        self.credit_amount = credit_amount


class SalesOrder(db.Model):
    __tablename__ = "sales_order"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client_name = db.relationship('Client')
    content_advt = db.Column(db.String())
    date_of_order = db.Column(db.String(100))
    dop = db.Column(db.String(100))
    bill = db.Column(db.String(100))
    bill_date = db.Column(db.String(100))
    amount = db.Column(db.Float)
    gst_amount = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    gst = db.Column(db.String(100))
    total_paid = db.Column(db.Float)
    total_payable = db.Column(db.Float)
    adjusted_credit = db.Column(db.Float)
    amount_received_date = db.Column(db.String(100))

    status = db.Column(
        db.Enum(SalesOrderStatus, values_callable=lambda x: [str(stat.value) for stat in SalesOrderStatus]),
        default=SalesOrderStatus.pending.value)

    filename = db.Column(db.String())

    def __init__(self, client_id, content_advt, date_of_order, dop, bill, bill_date, amount,gst_amount,total_amount, gst,total_paid,total_payable,adjusted_credit,
                 filename=None, amount_received_date=None):
        self.client_id = client_id
        self.content_advt = content_advt
        self.date_of_order = date_of_order
        self.dop = dop
        self.bill = bill
        self.bill_date = bill_date
        self.amount = amount
        self.gst_amount = gst_amount
        self.total_amount = total_amount
        self.gst = gst
        self.total_paid = total_paid
        self.total_payable = total_payable
        self.adjusted_credit = adjusted_credit

        self.amount_received_date = amount_received_date
        self.filename = filename


class PaymentVoucher(db.Model):
    __tablename__ = "payment_voucher"
    id = db.Column(db.Integer, primary_key=True)
    reference_no = db.Column(db.String())
    payment_date = db.Column(db.String())
    approval_date = db.Column(db.String())
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'))
    bill_no = db.relationship('SalesOrder')
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client_name = db.relationship('Client')
    amount = db.Column(db.Float)
    status = db.Column(
        db.Enum(PaymentStatus, values_callable=lambda x: [str(stat.value) for stat in PaymentStatus]),
        default=PaymentStatus.draft.value)

    def __init__(self, reference_no, payment_date, sales_order_id, amount, client_id, approval_date=None):
        self.reference_no = reference_no
        self.payment_date = payment_date
        self.amount = amount
        self.sales_order_id = sales_order_id
        self.client_id = client_id
        self.approval_date = approval_date
