import csv
import datetime
import os
import re
import webbrowser
from datetime import timedelta

import pandas as pd
from flask import render_template, request, url_for, flash, redirect, session, send_from_directory, jsonify
from flask_migrate import Migrate
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash

from form import Form
from models import db, create_app, Client, SalesOrder, SalesOrderStatus, Users, PaymentVoucher, PaymentStatus, Gst
from templates import Templates
import string
import random

app = create_app()
migrate = Migrate(app, db, render_as_batch=True)

UPLOAD_FOLDER = r'W:\work\flask new\client management\data\uploadedBills'
ALLOWED_EXTENSIONS = {'pdf'}
Client_List_File = os.path.join(os.curdir, 'data/clientList')
Report_Generated_File = os.path.join(os.curdir, 'data/reportGenerated')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['Client_List_File'] = Client_List_File
app.config['reportGenerated'] = Report_Generated_File


# Admin Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard', page=1))
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        for i in Users.query.all():
            if i.username == username and check_password_hash(i.password, password):
                session["username"] = i.username
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5)
                return redirect(url_for('dashboard', page=1))

        flash('Username or password is incorrect', category='error')
    return render_template(Templates.login)


# create new admin
@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if 'username' in session:
        if request.method == 'POST':
            userpass = request.form["password"]
            confirm_userpass = request.form["confirm_password"]
            hash_pass = generate_password_hash(userpass)
            email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            if not request.form["first_name"].isalpha():
                flash("Only Alphabets allowed in First name", category='error')
                return render_template(Templates.register)
            elif not request.form["last_name"].isalpha():
                flash("Only Alphabets allowed in Last name", category='error')
                return render_template(Templates.register)
            elif not re.match(email_regex, request.form["email"]):
                flash("Invalid Email", category='error')
                return render_template(Templates.register)
            elif not request.form["phone_no"].isdigit():
                flash("Only Digits allowed in Phone No.", category='error')
                return render_template(Templates.register)

            add_new_user = Users(username=request.form["username"], firstname=request.form["first_name"],
                                 last_name=request.form["last_name"], email=request.form["email"],
                                 phone_no=request.form["phone_no"],
                                 password=hash_pass)
            exists = db.session.query(db.exists().where(
                Users.username == request.form["username"])).scalar()
            if exists:
                flash("User with same username already exists", category='error')
                return render_template(Templates.register)
            if userpass != confirm_userpass:
                flash("Password does not match", category='error')
                return render_template(Templates.register)
            else:
                db.session.add(add_new_user)
                db.session.commit()
                flash('User Created', category='success')
                return redirect(url_for('manage_users'))
        return render_template(Templates.register)

    return render_template(Templates.login)


# logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# list of admins
@app.route('/users', methods=['GET', 'POST'])
def manage_users():
    if 'username' in session:
        users = Users.query.all()
        return render_template(Templates.admin_list, users=users)
    return render_template(Templates.login)


# show/update admin
@app.route('/admin-details/<int:admin_id>', methods=['GET', 'POST'])
def admin_details(admin_id):
    if 'username' in session:
        admin_to_update = Users.query.filter_by(id=admin_id).first()
        if request.method == 'POST':
            admin_to_update.username = request.form["username"]
            admin_to_update.first_name = request.form["first_name"]
            admin_to_update.last_name = request.form["last_name"]
            admin_to_update.email = request.form["email"]
            admin_to_update.phone_no = request.form["phone_no"]
            same_email = Users.query.filter(
                Users.email == admin_to_update.email)

            same_username = Users.query.filter(
                Users.id != admin_to_update.id, Users.username == admin_to_update.username
            )

            for res in same_email:
                if res.id == admin_to_update.id:
                    continue
                flash("Email already in use", category='error')

                return render_template(Templates.admin_details, admin_to_update=admin_to_update)

            for res in same_username:

                if res.id == admin_to_update.id:
                    continue

                flash("Username Already Taken", category='error')

                return render_template(Templates.admin_details, admin_to_update=admin_to_update)
            db.session.commit()
            flash('User Updated', category='success')
            return redirect(url_for('manage_users'))
        return render_template(Templates.admin_details, admin_to_update=admin_to_update)
    return render_template(Templates.login)


# update admin password
@app.route('/change-admin-pass/<int:admin_id>', methods=['GET', 'POST'])
def change_admin_pass(admin_id):
    admin = Users.query.filter_by(id=admin_id).first()
    if "username" in session:
        if request.method == "POST":
            current_password = request.form["current_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            if not check_password_hash(admin.password, current_password):
                flash("Current Password is Not Correct", category='error')
                return render_template(Templates.change_admin_pass)
            elif new_password != confirm_password:
                flash("Password doesn't match", category='error')
                return render_template(Templates.change_admin_pass)
            else:
                admin.password = generate_password_hash(new_password)
                db.session.commit()
                flash("Password Changed Successfully", category='success')
                return redirect(url_for('admin_details', admin_id=admin_id))
        return render_template(Templates.change_admin_pass, admin_id=admin_id)
    return render_template(Templates.login)


# list of clients
@app.route('/client-list/<int:page>')
def all_client_names(page):
    per_page = 8
    if "username" in session:
        clients = Client.query.order_by(desc(Client.id)).paginate(page=page, per_page=per_page,
                                                                  error_out=False)
        return render_template(Templates.client_list, clients=clients)
    return render_template(Templates.login)


# create a new client
@app.route("/new-client", methods=['GET', 'POST'])
def add_client():
    if "username" in session:
        if request.method == "POST":
            message = ''
            if request.form["client_name"].isnumeric():
                message = 'Name cannot contain numbers or any special symbol'

            if request.form["phone_no"].isalpha():
                message = 'Phone number cannot contain Alphabets or any special symbol'

            email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.fullmatch(email_reg, request.form['email']):
                message = "Enter a Valid Email"

            if message:
                flash(message, category='error')
                return render_template(Templates.add_client)
            else:

                added_client = Client(client_name=request.form["client_name"], email=request.form["email"],
                                      phone_no=request.form["phone_no"],
                                      address=request.form["address"]
                                      )

                db.session.add(added_client)
                db.session.commit()
                flash('client Added', category='success')
                return redirect(url_for('all_client_names', page=1))
        return render_template(Templates.add_client)
    return render_template(Templates.login)


# delete client
@app.route('/delete-client/<int:client_id>')
def delete_client(client_id):
    if "username" in session:
        client_to_delete = Client.query.filter_by(id=client_id).first()

        if SalesOrder.query.filter_by(client_id=client_id).first():
            flash("Client in use", category='error')
            return redirect(url_for('all_client_names'))

        else:
            db.session.delete(client_to_delete)
            db.session.commit()
            flash('Client Deleted', category='success')
            return redirect(url_for('all_client_names'))
    return render_template(Templates.login)


# update client
@app.route('/update-client/<int:client_id>', methods=['GET', 'POST'])
def update_client(client_id):
    date_now = datetime.date.today()
    time_now = datetime.datetime.now()
    last_updated = date_now.strftime("%d/%b/%Y")
    last_updated_time = time_now.strftime("%I:%M %p")
    if "username" in session:

        get_client = SalesOrder.query.filter_by(client_id=client_id).all()

        overall_payment_total = 0
        for i in get_client:
            if i.status.value == SalesOrderStatus.received.value:
                overall_payment_total = overall_payment_total + i.final_deal

        client_to_update = Client.query.filter_by(id=client_id).first()

        if request.method == "POST":
            message = ''
            if request.form["client_name"].isnumeric():
                message = 'Name cannot contain numbers or any special symbol'
                flash(message, category='error')

            email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.fullmatch(email_reg, request.form['email']):
                message = "Enter a Valid Email"

            if request.form["phone_no"].isalpha():
                message = 'Phone number cannot contain Alphabets or any special symbol'
                flash(message, category='error')

            if message:
                flash(message + 'Record not updated.', category='error')
                return render_template(Templates.update_client, client_to_update=client_to_update,
                                       )
            else:
                client_to_update.client_name = request.form["client_name"]
                client_to_update.email = request.form["email"]
                client_to_update.phone_no = request.form["phone_no"]
                client_to_update.address = request.form["address"]

                db.session.commit()
                flash('Client Updated.', category='success')
        return render_template(Templates.update_client, client_to_update=client_to_update, last_updated=last_updated,
                               last_updated_time=last_updated_time, overall_payment_total=overall_payment_total
                               )
    return render_template(Templates.login)


# list of SalesOrder created
@app.route('/sales-orders/<int:page>', methods=['GET', 'POST'])
def dashboard(page):
    if "username" in session:
        per_page = 8
        all_SalesOrder = SalesOrder.query.order_by(SalesOrder.bill.desc()).paginate(page=page, per_page=per_page,
                                                                                    error_out=False)
        all_SalesOrder_count = db.session.query(SalesOrder).count()

        total_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.received.value).all()
        pending_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.pending.value).all()

        final_deal_total = 0
        pending_final_total = 0

        for i in total_amount:
            final_deal_total = round(float(i.final_deal) + final_deal_total, 2)
        for i in pending_amount:
            pending_final_total = round(float(i.final_deal) + pending_final_total, 2)

        return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder, final_deal_total=final_deal_total,
                               pending_final_total=pending_final_total, all_SalesOrder_count=all_SalesOrder_count)
    return render_template(Templates.login)


# create a new record
@app.route('/add-record', methods=['GET', 'POST'])
def add_record():
    if "username" in session:
        form = Form()
        form.client_name.choices = [(client.id, client.client_name) for client in Client.query.all()]

        if request.method == "POST":

            exists = db.session.query(SalesOrder.bill).filter_by(bill=request.form["bill"]).first() is not None
            if exists:
                flash('Bill No. already exists', category='error')
                return render_template(Templates.add_record, form=form)

            get_file = request.files['file']
            if get_file:
                filename = 'Bill No' + '-' + request.form["bill"] + '-' + request.form["date_of_order"] + '.pdf'
                get_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                record = SalesOrder(request.form["client_name"], request.form["content_advt"],
                                    datetime.datetime.strptime(request.form["date_of_order"], "%d-%m-%Y").strftime(
                                        "%Y-%m-%d")
                                    , datetime.datetime.strptime(request.form["dop"], "%d-%m-%Y").strftime("%Y-%m-%d")
                                    , request.form["bill"],
                                    datetime.datetime.strptime(request.form["bill_date"], "%d-%m-%Y").strftime(
                                        "%Y-%m-%d"), request.form['final_deal_including_gst'], request.form['gst'],

                                    filename=os.path.join(app.config['UPLOAD_FOLDER'], filename))

                db.session.add(record)
                db.session.commit()
                flash('Record Added', category='success')
                return redirect(url_for('dashboard'))
            else:
                record = SalesOrder(client_id=request.form["client_name"], content_advt=request.form["content_advt"],
                                    date_of_order=request.form["date_of_order"],
                                    dop=request.form["dop"], bill=request.form["bill"],
                                    bill_date=request.form["bill_date"],
                                    final_deal=round(float(request.form["final_deal_including_gst"]), 2),
                                    gst=request.form["gst"],
                                    filename=None)

                db.session.add(record)
                db.session.commit()
                flash('Record Added', category='success')
                return redirect(url_for('dashboard', page=1))
        return render_template(Templates.add_record, form=form)
    return render_template(Templates.login)


# delete a record
@app.route('/delete-record/<int:record_id>')
def delete_record(record_id):
    if "username" in session:
        record_to_delete = SalesOrder.query.filter_by(id=record_id).first()
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()
            flash(f'Record of {record_to_delete} Deleted', category='success')
            return redirect(url_for('dashboard'))
    return render_template(Templates.login)


# show/update record details
@app.route('/record-details/<int:record_id>', methods=['GET', 'POST'])
def record_details(record_id):
    if "username" in session:
        date_now = datetime.date.today()
        time_now = datetime.datetime.now()
        last_updated = date_now.strftime("%d/%b/%Y")
        last_updated_time = time_now.strftime("%I:%M %p")
        record_to_update = SalesOrder.query.filter_by(id=record_id).first()
        get_gst_percentage = record_to_update.gst
        print(get_gst_percentage, type(get_gst_percentage))
        client = Client.query.filter(Client.id == record_to_update.client_id).first()
        form = Form()

        form.client_name.choices = [(client.id, client.client_name) for client in Client.query.all()]
        total_vouchers_in_record = PaymentVoucher.query.filter_by(sales_order_id=record_id).all()
        total_vouchers = 0
        for voucher in total_vouchers_in_record:
            total_vouchers = total_vouchers + 1
        if request.method == "POST":

            client.email = request.form["email"]
            email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.fullmatch(email_reg, request.form['email']):
                message = "Enter a Valid Email"
                flash(message + 'Record Not Updated', category='danger')
                return redirect(url_for('record_details', record_id=record_id))
            client.phone_no = request.form["phone_no"]

            if request.form["phone_no"].isalpha():
                message = 'Phone number cannot contain Alphabets or any special symbol. Record Not Updated'
                flash(message, category='error')
                return redirect(url_for('record_details', record_id=record_id))
            if request.form["final_deal"].isalpha():
                message = 'Final deal amount cannot contain Alphabets or any special symbol. Record Not Updated'
                flash(message, category='error')
                return redirect(url_for('record_details', record_id=record_id))
            record_to_update.client_id = request.form["client_name"]
            record_to_update.content_advt = request.form["content_advt"]
            record_to_update.date_of_order = request.form["date_of_order"]
            record_to_update.dop = request.form["dop"]
            record_to_update.final_deal = request.form["final_deal_including_gst"]

            file = request.files['file']
            if request.files['file']:
                filename = 'Bill No' + '-' + str(record_to_update.bill) + '-' + str(
                    record_to_update.date_of_order) + '.pdf'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                record_to_update.filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            db.session.commit()

            flash('Record Updated', category='success')

        if get_gst_percentage == str(Gst.percent_12.value):
            form.client_name.default = record_to_update.client_id
            form.gst.default = Gst.percent_12.value
            form.process()
        elif get_gst_percentage == str(Gst.percent_5.value):
            form.client_name.default = record_to_update.client_id
            form.gst.default = Gst.percent_5.value
            form.process()
        elif get_gst_percentage == str(Gst.percent_18.value):
            form.client_name.default = record_to_update.client_id
            form.gst.default = Gst.percent_18.value
            form.process()
        elif get_gst_percentage == str(Gst.percent_28.value):
            form.client_name.default = record_to_update.client_id
            form.gst.default = Gst.percent_28.value
            form.process()

        return render_template(Templates.record_details, record_to_update=record_to_update, form=form,
                               last_updated=last_updated, client=client, last_updated_time=last_updated_time,
                               total_vouchers=total_vouchers, SalesOrderStatus=SalesOrderStatus)

    return render_template(Templates.login)


# set record payment status to cancelled
@app.route('/set-cancel/<int:record_id>', methods=['GET', 'POST'])
def set_cancel(record_id):
    form = Form()
    record_to_update = SalesOrder.query.filter_by(id=record_id).first()
    client = Client.query.filter(Client.id == record_to_update.client_id).first()

    date_now = datetime.date.today()
    time_now = datetime.datetime.now()
    last_updated = date_now.strftime("%d/%b/%Y")
    last_updated_time = time_now.strftime("%I:%M %p")
    record_to_update.status = SalesOrderStatus.cancelled.value
    record_to_update.amount_received_date = date_now
    db.session.commit()
    flash('Status Updated', category='success')

    return render_template(Templates.record_details, record_to_update=record_to_update, form=form,
                           last_updated=last_updated, client=client, last_updated_time=last_updated_time,
                           SalesOrderStatus=SalesOrderStatus)


@app.route('/voucher-list/<int:record_id>', methods=['GET', 'POST'])
def voucher_list(record_id):
    record = SalesOrder.query.filter_by(id=record_id).first()
    client = Client.query.filter(Client.id == record.client_id).first()
    total_amount = 0
    total_vouchers = PaymentVoucher.query.filter_by(sales_order_id=record.id).all()
    total_voucher_count = len(total_vouchers)
    for voucher in total_vouchers:
        if voucher.status.value == PaymentStatus.approved.value:
            total_amount = total_amount + voucher.amount
    if float(total_amount) >= record.final_deal:
        record.status = SalesOrderStatus.received.value
        client.credit_amount = round(client.credit_amount + float(total_amount) - record.final_deal, 2)
        db.session.commit()

    return render_template('list_of_sale_order_vouchers.html', total_vouchers=total_vouchers, record=record,
                           total_amount=total_amount, client=client, SalesOrderStatus=SalesOrderStatus,
                           total_voucher_count=total_voucher_count)


@app.route('/create-payment-voucher/<int:record_id>', methods=['GET', 'POST'])
def create_payment_voucher(record_id):
    if "username" in session:
        record = SalesOrder.query.filter_by(id=record_id).first()
        date_today = datetime.date.today()
        payment_voucher_count = db.session.query(PaymentVoucher).count()

        last_voucher_ref_no = db.session.query(PaymentVoucher).order_by(PaymentVoucher.id.desc()).first()

        if request.method == "POST":

            if payment_voucher_count < 1:
                voucher_no = 0
                random_string = ''
                for i in range(10):
                    random_string += random.choice(string.ascii_lowercase + string.ascii_uppercase)
                ref_no = f"{random_string}-{record.bill}-{voucher_no + 1}"
                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=record.id,
                                         client_id=record.client_id)
                db.session.add(voucher)
                db.session.commit()
                flash('Voucher created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
            else:
                random_string = ''
                for i in range(10):
                    random_string += random.choice(string.ascii_lowercase + string.ascii_uppercase)
                ref_no = f"{random_string}-{record.bill}-{int(last_voucher_ref_no.reference_no.split('-')[-1]) + 1}"

                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=record.id,
                                         client_id=record.client_id)
                db.session.add(voucher)
                db.session.commit()
                flash('Voucher created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
        return render_template('create_payment_voucher.html', record=record, date_today=date_today)
    return render_template(Templates.login)


@app.route('/get_client_list/<bill_no>')
def get_client_list(bill_no):
    records = SalesOrder.query.filter_by(id=bill_no).first()
    client_results = SalesOrder.query.filter_by(bill=records.bill).all()
    client_list = []
    for client in client_results:
        print(client.client_id)
        print(client.client_name.client_name)
        client_obj = {

            'client_id': client.client_id,
            'client_name': client.client_name.client_name
        }
        client_list.append(client_obj)
    return jsonify({'client_list': client_list})


@app.route('/create-new-payment-voucher', methods=['GET', 'POST'])
def create_new_payment_voucher():
    if "username" in session:

        form = Form()

        form.bill_no.choices = [(bill_no.id, bill_no.bill) for bill_no in
                                SalesOrder.query.order_by(SalesOrder.bill.asc()).all()]

        date_today = datetime.date.today()
        payment_voucher_count = db.session.query(PaymentVoucher).count()

        last_voucher_ref_no = db.session.query(PaymentVoucher).order_by(PaymentVoucher.id.desc()).first()

        if request.method == "POST":
            bill_no = SalesOrder.query.filter_by(id=form.bill_no.data).first()
            client = Client.query.filter_by(id=bill_no.client_id).first()
            check_sales_order_status = SalesOrder.query.filter_by(id=int(request.form["bill_no"])).first()
            if check_sales_order_status.status.value == SalesOrderStatus.received.value or check_sales_order_status.status.value == SalesOrderStatus.cancelled.value:
                flash("Cannot make changes to this Record.")
                return redirect(url_for('create_new_payment_voucher'))
            if payment_voucher_count < 1:
                voucher_no = 0
                random_string = ''
                for i in range(10):
                    random_string += random.choice(string.ascii_lowercase + string.ascii_uppercase)
                ref_no = f"{random_string}-{request.form['bill_no']}-{voucher_no + 1}"
                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=bill_no.id,
                                         client_id=client.id)
                db.session.add(voucher)
                db.session.commit()
                flash('Voucher created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
            else:
                random_string = ''
                for i in range(10):
                    random_string += random.choice(string.ascii_lowercase + string.ascii_uppercase)
                ref_no = f"{random_string}-{request.form['bill_no']}-{int(last_voucher_ref_no.reference_no.split('-')[-1]) + 1}"

                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=bill_no.id,
                                         client_id=client.id)
                db.session.add(voucher)
                db.session.commit()
                flash('Voucher created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
        return render_template('create_payment_voucher_with_bill.html', form=form, date_today=date_today)
    return render_template(Templates.login)


@app.route('/voucher-details/<int:voucher_id>', methods=['GET', 'POST'])
def voucher_details(voucher_id):
    if "username" in session:
        voucher = PaymentVoucher.query.filter_by(id=voucher_id).first()
        record = SalesOrder.query.filter_by(bill=voucher.bill_no.bill).first()
        return render_template('payment_voucher_details.html', voucher=voucher, PaymentStatus=PaymentStatus,
                               record=record)
    return render_template(Templates.login)


@app.route('/approve-voucher/<int:voucher_id>', methods=['GET', 'POST'])
def approve_voucher(voucher_id):
    if "username" in session:

        date_today = datetime.date.today()
        voucher_to_update = PaymentVoucher.query.filter_by(id=voucher_id).first()
        voucher_to_update.approval_date = date_today
        voucher_to_update.status = PaymentStatus.approved.value
        total_amount = 0
        sale_order = SalesOrder.query.filter_by(bill=voucher_to_update.bill_no.bill).first()

        total_vouchers = PaymentVoucher.query.filter_by(sales_order_id=voucher_to_update.bill_no.bill).all()
        for i in total_vouchers:
            if float(total_amount) >= sale_order.final_deal:
                sale_order.status = SalesOrderStatus.received.value
        db.session.commit()
        flash('Voucher Updated', category='success')
        return redirect(url_for('voucher_details', voucher_id=voucher_id))
    return render_template(Templates.login)


@app.route('/cancel-voucher/<int:voucher_id>', methods=['GET', 'POST'])
def cancel_voucher(voucher_id):
    if "username" in session:
        voucher_to_update = PaymentVoucher.query.filter_by(id=voucher_id).first()

        voucher_to_update.status = PaymentStatus.cancelled.value
        db.session.commit()
        flash('Voucher Updated', category='success')
        return redirect(url_for('voucher_details', voucher_id=voucher_id))
    return render_template(Templates.login)


@app.route('/all-vouchers-list/<int:page>', methods=['GET', 'POST'])
def all_vouchers_list(page):
    per_page = 8
    if "username" in session:
        all_vouchers = PaymentVoucher.query.order_by(desc(PaymentVoucher.id)).paginate(page=page, per_page=per_page,
                                                                                       error_out=False)

        return render_template('list_of_all_payment_vouchers.html', all_vouchers=all_vouchers)
    return render_template(Templates.login)


@app.route('/search-vouchers', methods=['POST', 'GET'])
def search_vouchers():
    if "username" in session:

        if request.method == 'GET':

            search = request.args['search'].lower()
            records = SalesOrder.query.filter(SalesOrder.bill.ilike(f"%{search}%")).all()
            clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
            record_ids = [record.id for record in records]
            client_ids = [client.id for client in clients]
            all_vouchers = PaymentVoucher.query.filter(PaymentVoucher.reference_no.ilike(f"%{search}%") |
                                                       PaymentVoucher.sales_order_id.in_(
                                                           record_ids) | PaymentVoucher.client_id.in_(
                client_ids)).all()
            if all_vouchers:
                return render_template('list_of_all_payment_vouchers.html', all_vouchers=all_vouchers)
            flash('No Record Found')
            return redirect(url_for('all_vouchers_list', page=1))
        return redirect(url_for('all_vouchers_list'))
    return render_template(Templates.login)


# list of records with pending payment status
@app.route('/sales-order/<string:filter_by>/<int:page>')
def filter_payment_status(filter_by, page):
    if "username" in session:
        per_page = 8

        if filter_by == 'pending':
            print(filter_by)
            pending_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.pending.value).all()

            pending_total = 0

            for i in pending_amount:
                pending_total = round(float(i.final_deal) + pending_total, 2)

            if request.args.get('search', ''):
                search = request.args['search'].lower()

                clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
                client_ids = [client.id for client in clients]
                all_SalesOrder_count = db.session.query(SalesOrder).count()
                all_SalesOrder = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).filter(
                    SalesOrder.status == SalesOrderStatus.pending.value).all()

                pending_total = 0

                for i in all_SalesOrder:
                    print(i)
                    pending_total = round(float(i.final_deal) + pending_total, 2)
                if all_SalesOrder:
                    all_SalesOrder = SalesOrder.query.filter(
                        SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(
                            f"%{search}%")).filter(SalesOrder.status == SalesOrderStatus.pending.value).paginate(
                        page=page,
                        per_page=per_page,
                        error_out=False)

                    return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder,
                                           all_SalesOrder_count=all_SalesOrder_count, pending_total=pending_total,
                                           search=search,
                                           filter_by=filter_by)
                flash('No Record Found')

            all_SalesOrder = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.pending.value).order_by(
                desc(SalesOrder.id)).paginate(page=page, per_page=per_page, error_out=False)
            return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder,
                                   pending_total=pending_total, filter_by=filter_by)

        elif filter_by == 'received':
            received_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.received.value).all()

            received_total = 0

            for i in received_amount:
                received_total = round(float(i.final_deal) + received_total, 2)

            if request.args.get('search', ''):
                search = request.args['search'].lower()

                clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
                client_ids = [client.id for client in clients]
                all_SalesOrder_count = db.session.query(SalesOrder).count()
                all_SalesOrder = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).filter(
                    SalesOrder.status == SalesOrderStatus.received.value).all()

                received_total = 0

                for i in all_SalesOrder:
                    received_total = round(float(i.final_deal) + received_total, 2)

                if all_SalesOrder:
                    all_SalesOrder = SalesOrder.query.filter(
                        SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(
                            f"%{search}%")).filter(SalesOrder.status == SalesOrderStatus.received.value).paginate(
                        page=page,
                        per_page=per_page,
                        error_out=False)

                    return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder,
                                           all_SalesOrder_count=all_SalesOrder_count, received_total=received_total,
                                           search=search,
                                           filter_by=filter_by)
                flash('No Record Found')
            all_SalesOrder = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.received.value).order_by(
                desc(SalesOrder.id)).paginate(page=page, per_page=per_page, error_out=False)
            return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder, received_total=received_total,
                                   filter_by=filter_by)

        elif filter_by == 'cancelled':
            received_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.cancelled.value).all()

            cancelled_total = 0

            for i in received_amount:
                cancelled_total = round(float(i.final_deal) + cancelled_total, 2)

            if request.args.get('search', ''):
                search = request.args['search'].lower()

                clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
                client_ids = [client.id for client in clients]
                all_SalesOrder_count = db.session.query(SalesOrder).count()
                all_SalesOrder = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).filter(
                    SalesOrder.status == SalesOrderStatus.received.value).all()

                cancelled_total = 0

                for i in received_amount:
                    cancelled_total = round(float(i.final_deal) + cancelled_total, 2)

                if all_SalesOrder:
                    all_SalesOrder = SalesOrder.query.filter(
                        SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(
                            f"%{search}%")).filter(SalesOrder.status == SalesOrderStatus.cancelled.value).paginate(
                        page=page,
                        per_page=per_page,
                        error_out=False)
                    return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder,
                                           all_SalesOrder_count=all_SalesOrder_count, cancelled_total=cancelled_total,
                                           search=search,
                                           filter_by=filter_by)
                flash('No Record Found')
            all_SalesOrder = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.cancelled.value).order_by(
                desc(SalesOrder.id)).paginate(page=page, per_page=per_page, error_out=False)
            return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder, cancelled_total=cancelled_total,
                                   filter_by=filter_by)
    return render_template(Templates.login)


# opens attachment linked to a record
@app.route('/download/<path:filename>/<int:record_id>')
def download(filename, record_id):
    if "username" in session:
        uploads = os.path.join(UPLOAD_FOLDER, filename)
        webbrowser.open_new_tab(uploads)
        return redirect(url_for('record_details', record_id=record_id))
    return render_template(Templates.login)


# Search specific keyword in list of records
@app.route('/sales-order/<int:page>', methods=['POST', 'GET'])
def search_records(page):
    per_page = 8
    if "username" in session:
        if request.method == 'GET':
            search = request.args['search'].lower()

            clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
            client_ids = [client.id for client in clients]
            all_SalesOrder_count = db.session.query(SalesOrder).count()
            all_SalesOrder = SalesOrder.query.filter(
                SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).all()
            if all_SalesOrder:
                all_SalesOrder = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).paginate(page=page,
                                                                                                          per_page=per_page,
                                                                                                          error_out=False)

                final_deal_total = 0
                pending_final_total = 0

                for i in all_SalesOrder:
                    if i.status.value == SalesOrderStatus.received.value:
                        final_deal_total = round(float(i.final_deal) + final_deal_total, 2)
                    elif i.status.value == SalesOrderStatus.pending.value:
                        pending_final_total = round(float(i.final_deal) + pending_final_total, 2)

                return render_template(Templates.dashboard, all_SalesOrder=all_SalesOrder,
                                       all_SalesOrder_count=all_SalesOrder_count, search=search,
                                       final_deal_total=final_deal_total, pending_final_total=pending_final_total)

            flash('No Record Found')
            return redirect(url_for('dashboard', page=1))
        return redirect(url_for('dashboard', page=1))
    return render_template(Templates.login)


# Search specific keyword in list of clients
@app.route('/clients/<int:page>', methods=['POST', 'GET'])
def search_clients(page):
    per_page = 8
    if "username" in session:
        if request.method == 'GET':
            search = request.args['search'].lower()
            clients = Client.query.filter(
                Client.client_name.ilike(f"%{search}%") | Client.phone_no.ilike(f"%{search}%") | Client.address.ilike(
                    f"%{search}%") | Client.email.ilike(f"%{search}%")).paginate(page=page, per_page=per_page,
                                                                                 error_out=False)
            if clients:
                return render_template(Templates.client_list, clients=clients, search=search)

            flash('No Record Found', category='error')
            return redirect(url_for('all_client_names', page=1))
        return redirect(url_for('all_client_names', page=1))
    return render_template(Templates.login)


# delete multiple records using checkbox
@app.route('/get_checked_boxes', methods=['GET', 'POST'])
def get_checked_boxes():
    if 'username' in session and request.method == "POST":
        all_vouchers = PaymentVoucher.query.all()
        rec_ids = request.form['rec_ids']
        for ids in rec_ids.split(','):
            delete_rec = SalesOrder.query.filter_by(id=ids).first()
            print(delete_rec)
            for voucher in all_vouchers:

                if voucher.bill_no.bill == delete_rec.bill:
                    db.session.delete(voucher)

            db.session.delete(delete_rec)
            db.session.commit()
        flash("record_deleted", category='success')
        return redirect(url_for('dashboard', page=1))

    return render_template(Templates.login)


# delete multiple clients using checkbox
@app.route('/get_checked_boxes_for_client', methods=['GET', 'POST'])
def get_checked_boxes_for_client():
    if 'username' in session and request.method == "POST":
        record_ids = request.form['rec_ids']

        for ids in record_ids.split(','):
            delete = Client.query.filter_by(id=ids).first()
            if SalesOrder.query.filter_by(client_id=delete.id).first():
                flash("Client in use", category='error')
                return redirect(url_for('all_client_names'))
            db.session.delete(delete)
            db.session.commit()
        flash("client Deleted", category='success')
        return redirect(url_for('all_client_names'))

    return render_template(Templates.login)


# delete multiple admins using checkbox
@app.route('/get_checked_boxes_for_admin', methods=['GET', 'POST'])
def get_checked_boxes_for_admin():
    if 'username' in session and request.method == "POST":
        record_ids = request.form['rec_ids']

        for ids in record_ids.split(','):
            user_to_del = Users.query.filter_by(id=ids).first()

            if session["username"] == user_to_del.username:
                flash('Cannot delete a user that is logged in', category='error')
                return redirect(url_for('manage_users'))
            db.session.delete(user_to_del)
            db.session.commit()
        flash("User Deleted", category='success')
        return redirect(url_for('manage_users'))

    return render_template(Templates.login)


@app.route('/get_checked_boxes_for_payment_vouchers/<int:record_id>', methods=['GET', 'POST'])
def get_checked_boxes_for_payment_vouchers(record_id):
    if 'username' in session:
        if request.method == "POST":
            rec_ids = request.form['rec_ids']
            for ids in rec_ids.split(','):
                check_record_status = SalesOrder.query.filter_by(id=record_id).first()
                if check_record_status.status.value == SalesOrderStatus.received.value:
                    flash("Cannot make changes to this record.", category='error')
                    return redirect(url_for('voucher_list', record_id=record_id))
                delete = PaymentVoucher.query.filter_by(id=ids).first()
                db.session.delete(delete)
                db.session.commit()
            flash("record_deleted", category='success')
            return redirect(url_for('voucher_list', record_id=record_id))
    return render_template(Templates.login)


# generate csv report for list of records selected
@app.route('/csv_file_record_to_update', methods=['POST', 'GET'])
def csv_file_record_to_update():
    if 'username' in session and request.method == "POST":
        rec_ids = request.form["check_rec_ids"]
        # if update_record checkbox is checked, id's of clients and record is included in the csv file else excluded
        if request.form.get("update_check"):

            file_name = 'Update_Record.csv'
            with open(os.path.join(Report_Generated_File, file_name), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow(
                    ['Id', 'Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Final Deal(Rs.)',
                     'GST(%)',
                     'Amount Received Date'
                     ])
                for rec_id in rec_ids.split(','):
                    record = SalesOrder.query.filter_by(id=rec_id).first()

                    final = [record.id, record.client_id, record.content_advt, record.date_of_order,
                             record.dop, record.bill,
                             record.bill_date,
                             record.final_deal, record.gst, record.amount_received_date]
                    write_file.writerow(final)
        else:
            file_name = 'Record.csv'
            with open(os.path.join(Report_Generated_File, file_name), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow(
                    ['Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Final Deal(Rs.)', 'GST(%)',
                     'Amount Received Date'])
                for rec_id in rec_ids.split(','):
                    record = SalesOrder.query.filter_by(id=rec_id).first()

                    final = [record.client_name.client_name, record.content_advt, record.date_of_order,
                             record.dop, record.bill,
                             record.bill_date,
                             record.final_deal, record.gst, record.amount_received_date]
                    write_file.writerow(final)
        return send_from_directory(Report_Generated_File, file_name, as_attachment=True)


# generate csv report for list of clients selected
@app.route('/csv-for-client', methods=['POST', 'GET'])
def csv_for_client():
    client_ids = request.form["check_rec_ids"]
    file_name = 'Clients.csv'
    overall_payment_total = 0
    with open(Client_List_File + '\\' + file_name, mode='w', newline='') as file:
        write_file = csv.writer(file)
        write_file.writerow(
            ['Name', 'Email', 'Phone No.', 'Address', 'Overall Payment Total', 'Credit'])
        for cli_id in client_ids.split(','):
            client = Client.query.filter_by(id=cli_id).first()
            record = SalesOrder.query.filter_by(client_id=cli_id).all()
            for i in record:
                if i.status.value == SalesOrderStatus.received.value:
                    overall_payment_total = overall_payment_total + i.final_deal

            final = [client.client_name, client.email, client.phone_no,
                     client.address, overall_payment_total, client.credit_amount]
            print(final)
            write_file.writerow(final)

    return send_from_directory(Client_List_File, file_name, as_attachment=True)


# add/update new records using a csv file
@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
    if 'username' in session and request.method == "POST":
        uploaded_file = request.files['file']
        uploaded_file.save(os.path.join(Report_Generated_File, uploaded_file.filename))
        read_file = pd.read_csv(Report_Generated_File + '\\' + uploaded_file.filename)
        record = SalesOrder.query.all()
        count = 0
        while count != len(read_file):

            if 'Id' in read_file.columns:
                if count >= len(read_file):
                    break
                else:

                    for row in record:
                        if count >= len(read_file):
                            break

                        if row.id == int(read_file.loc[count, 'Id']):
                            if row.status.value == SalesOrderStatus.received.value or row.status.value == SalesOrderStatus.cancelled.value:
                                print(count, row.status.value)
                                flash("Cannot make changes to Records with status Received/Cancelled")
                                return render_template(Templates.file_upload)
                            row.client_id = int(read_file.loc[count, 'Client'])
                            row.content_advt = read_file.loc[count, 'AD/GP/Others']
                            row.date_of_order = read_file.loc[count, 'RO Date'],

                            row.dop = read_file.loc[count, 'DoP']
                            row.bill_date = read_file.loc[count, 'Bill Date'],
                            row.final_deal = float(read_file.loc[count, 'Final Deal(Rs.)'])
                            row.gst = str(read_file.loc[count, 'GST(%)'])

                            row.amount_received_date = read_file.loc[count, 'Amount Received Date']
                            db.session.commit()
                            count += 1
            else:
                exists = db.session.query(db.exists().where(
                    Client.client_name == read_file.loc[count, 'Client'])).scalar()
                get_client_id = Client.query.filter_by(client_name=read_file.loc[count, 'Client']).first()

                print(exists)
                if not exists:
                    new_client = Client(client_name=read_file.loc[count, 'Client'], email=None, phone_no=None,
                                        address=None, credit_amount=0)
                    db.session.add(new_client)
                    db.session.commit()

                else:
                    if count >= len(read_file):
                        break
                    else:

                        bill_no_exists = db.session.query(db.exists().where(
                            str(SalesOrder.bill) == read_file.loc[count, 'Bill No.']))
                        print(bill_no_exists)
                        if bill_no_exists:
                            get_record_id = SalesOrder.query.filter_by(
                                bill=str(read_file.loc[count, 'Bill No.'])).first()
                            if get_record_id:
                                flash(f"Bill no {get_record_id.bill} already exists in the Database! \n"
                                      f"Duplicate Bill No. at Row No. {count + 2}.")
                                return redirect(url_for('file_upload'))

                            new_record = SalesOrder(client_id=get_client_id.id,
                                                    content_advt=read_file.loc[count, 'AD/GP/Others'],
                                                    date_of_order=
                                                    read_file.loc[count, 'RO Date'],
                                                    dop=read_file.loc[count, 'DoP'],

                                                    bill=int(read_file.loc[count, 'Bill No.']),
                                                    bill_date=
                                                    read_file.loc[count, 'Bill Date'],

                                                    final_deal=float(read_file.loc[count, 'Final Deal(Rs.)']),
                                                    gst=str(read_file.loc[count, 'GST(%)']),
                                                    amount_received_date=read_file.loc[count, 'Amount Received Date'],
                                                    )
                            db.session.add(new_record)
                            db.session.commit()
                            count += 1
        flash(f"{count} Record added", category="success")
    return render_template(Templates.file_upload)


if __name__ == "__main__":
    app.run()
