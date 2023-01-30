import csv
import datetime
import os
import re
import webbrowser
from datetime import timedelta

import pandas as pd
from flask import render_template, request, url_for, flash, redirect, session, send_from_directory
from flask_migrate import Migrate
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash

from form import Form
from models import db, create_app, Client, Records, RecordStatus, Users, PaymentVoucher, PaymentStatus
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
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        for i in Users.query.all():
            if i.username == username and check_password_hash(i.password, password):
                session["username"] = i.username
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5)
                return redirect(url_for('dashboard'))

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
                return redirect(url_for('manage_users'))
        return render_template(Templates.change_admin_pass)
    return render_template(Templates.login)


# list of clients
@app.route('/client-list')
def all_client_names():
    if "username" in session:
        clients = Client.query.order_by(desc(Client.id))
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

            if request.form["final_deal"].isalpha():
                message = 'Final deal amount cannot contain Alphabets or any special symbol'

            if message:
                flash(message, category='error')
                return render_template(Templates.add_client)
            else:
                gst = round((18 / 100) * float(request.form['final_deal']), 2)

                added_client = Client(client_name=request.form["client_name"], email=request.form["email"],
                                      phone_no=request.form["phone_no"],
                                      address=request.form["address"],
                                      final_deal=float(request.form["final_deal"]) + gst, gst=gst)

                db.session.add(added_client)
                db.session.commit()
                flash('client Added', category='success')
                return redirect(url_for('all_client_names'))
        return render_template(Templates.add_client)
    return render_template(Templates.login)


# delete client
@app.route('/delete-client/<int:client_id>')
def delete_client(client_id):
    if "username" in session:
        client_to_delete = Client.query.filter_by(id=client_id).first()

        if Records.query.filter_by(client_id=client_id).first():
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
        client_to_update = Client.query.filter_by(id=client_id).first()
        get_client = Client.query.filter_by(id=client_id).first()
        old_final_deal = get_client.final_deal
        if request.method == "POST":
            message = ''
            if request.form["client_name"].isnumeric():
                message = 'Name cannot contain numbers or any special symbol'
                flash(message, category='error')

            if request.form["phone_no"].isalpha():
                message = 'Phone number cannot contain Alphabets or any special symbol'
                flash(message, category='error')
            if request.form["final_deal"].isalpha():
                message = 'Final deal amount cannot contain Alphabets or any special symbol'
                flash(message, category='error')

            if message:
                flash('Record not added', category='error')
                return render_template(Templates.update_client, client_to_update=client_to_update)
            else:
                client_to_update.client_name = request.form["client_name"]
                client_to_update.email = request.form["email"]
                client_to_update.phone_no = request.form["phone_no"]
                client_to_update.address = request.form["address"]
                if float(request.form["final_deal"]) == float(request.form["old_final_deal"]):
                    gst = get_client.gst
                    client_to_update.final_deal = float(request.form["old_final_deal"])
                    client_to_update.gst = gst

                else:
                    gst = float((18 / 100) * float(request.form["final_deal"]))
                    client_to_update.final_deal = float(request.form["final_deal"]) + gst
                    client_to_update.gst = gst

                db.session.commit()
                flash('Client Updated.', category='success')
        return render_template(Templates.update_client, client_to_update=client_to_update, last_updated=last_updated,
                               last_updated_time=last_updated_time,
                               old_final_deal=old_final_deal)
    return render_template(Templates.login)


# list of records created
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "username" in session:
        all_records = Records.query.order_by(Records.bill.desc())

        return render_template(Templates.dashboard, all_records=all_records)
    return render_template(Templates.login)


# create a new record
@app.route('/add-record', methods=['GET', 'POST'])
def add_record():
    if "username" in session:
        form = Form()
        form.client_name.choices = [(client.id, client.client_name) for client in Client.query.all()]

        print(RecordStatus.pending.value)
        if request.method == "POST":
            file = request.files['file']
            if file:
                filename = 'Bill No' + '-' + request.form["bill"] + '-' + request.form["date_of_order"] + '.pdf'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                record = Records(request.form["client_name"], request.form["content_advt"],
                                 datetime.datetime.strptime(request.form["date_of_order"], "%d-%m-%Y").strftime(
                                     "%Y-%m-%d")
                                 , datetime.datetime.strptime(request.form["dop"], "%d-%m-%Y").strftime("%Y-%m-%d")
                                 , request.form["bill"],
                                 datetime.datetime.strptime(request.form["bill_date"], "%d-%m-%Y").strftime("%Y-%m-%d"),

                                 filename=os.path.join(app.config['UPLOAD_FOLDER'], filename))

                db.session.add(record)
                db.session.commit()
                flash('Record Added', category='success')
                return redirect(url_for('dashboard'))
            else:
                record = Records(request.form["client_name"], request.form["content_advt"],
                                 request.form["date_of_order"],
                                 request.form["dop"], request.form["bill"], request.form["bill_date"],

                                 filename=None)

                db.session.add(record)
                db.session.commit()
                flash('Record Added', category='success')
                return redirect(url_for('dashboard'))
        return render_template(Templates.add_record, form=form)
    return render_template(Templates.login)


# delete a record
@app.route('/delete-record/<int:record_id>')
def delete_record(record_id):
    if "username" in session:
        record_to_delete = Records.query.filter_by(id=record_id).first()
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
        record_to_update = Records.query.filter_by(id=record_id).first()
        client = Client.query.filter(Client.id == record_to_update.client_id).first()
        form = Form()

        form.client_name.choices = [(client.id, client.client_name) for client in Client.query.all()]
        total_vouchers_in_record = PaymentVoucher.query.filter_by(record_id=record_id).all()
        total_vouchers = 0
        for voucher in total_vouchers_in_record:
            total_vouchers = total_vouchers + 1
        if request.method == "POST":

            client.email = request.form["email"]
            client.phone_no = request.form["phone_no"]
            client.final_deal = request.form["final_deal"]

            record_to_update.client_id = request.form["client_name"]
            record_to_update.content_advt = request.form["content_advt"]
            record_to_update.date_of_order = request.form["date_of_order"]
            record_to_update.dop = request.form["dop"]

            file = request.files['file']
            if request.files['file']:
                filename = 'Bill No' + '-' + str(record_to_update.bill) + '-' + str(
                    record_to_update.date_of_order) + '.pdf'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                record_to_update.filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            db.session.commit()

            flash('Record Updated', category='success')

        form.client_name.default = record_to_update.client_id

        form.process()

        return render_template(Templates.record_details, record_to_update=record_to_update, form=form,
                               last_updated=last_updated, client=client, last_updated_time=last_updated_time,
                               total_vouchers=total_vouchers, RecordStatus=RecordStatus)

    return render_template(Templates.login)


# set record payment status to received
@app.route('/set-receive/<int:record_id>', methods=['GET', 'POST'])
def set_receive(record_id):
    form = Form()
    record_to_update = Records.query.filter_by(id=record_id).first()
    client = Client.query.filter(Client.id == record_to_update.client_id).first()

    date_now = datetime.date.today()
    time_now = datetime.datetime.now()
    last_updated = date_now.strftime("%d/%b/%Y")
    last_updated_time = time_now.strftime("%I:%M %p")
    record_to_update.status = RecordStatus.received.value

    record_to_update.amount_received_date = date_now
    db.session.commit()
    flash('Status Updated', category='success')
    return render_template(Templates.record_details, record_to_update=record_to_update, form=form,
                           last_updated=last_updated, client=client, last_updated_time=last_updated_time)


# set record payment status to cancelled
@app.route('/set-cancel/<int:record_id>', methods=['GET', 'POST'])
def set_cancel(record_id):
    form = Form()
    record_to_update = Records.query.filter_by(id=record_id).first()
    client = Client.query.filter(Client.id == record_to_update.client_id).first()

    date_now = datetime.date.today()
    time_now = datetime.datetime.now()
    last_updated = date_now.strftime("%d/%b/%Y")
    last_updated_time = time_now.strftime("%I:%M %p")
    record_to_update.status = RecordStatus.cancelled.value
    record_to_update.amount_received_date = date_now
    db.session.commit()
    flash('Status Updated', category='success')

    return render_template(Templates.record_details, record_to_update=record_to_update, form=form,
                           last_updated=last_updated, client=client, last_updated_time=last_updated_time,
                           RecordStatus=RecordStatus)


@app.route('/voucher-list/<int:record_id>', methods=['GET', 'POST'])
def voucher_list(record_id):
    record = Records.query.filter_by(id=record_id).first()
    client = Client.query.filter(Client.id == record.client_id).first()
    total_amount = 0
    total_vouchers = PaymentVoucher.query.filter_by(record_id=record.id).all()
    total_voucher_count = len(total_vouchers)
    for voucher in total_vouchers:
        if voucher.status.value == PaymentStatus.approved.value:
            total_amount = total_amount + voucher.amount
    if float(total_amount) >= client.final_deal:
        record.status = RecordStatus.received.value
        client.credit_amount = round(client.credit_amount + float(total_amount) - client.final_deal, 2)
        db.session.commit()

    return render_template('payment_voucher.html', total_vouchers=total_vouchers, record=record,
                           total_amount=total_amount, client=client, RecordStatus=RecordStatus,
                           total_voucher_count=total_voucher_count)


@app.route('/create-payment-voucher/<int:record_id>', methods=['GET', 'POST'])
def create_payment_voucher(record_id):
    if "username" in session:
        record = Records.query.filter_by(id=record_id).first()
        date_today = datetime.date.today()
        paymentVoucher_count = db.session.query(PaymentVoucher).count()

        last_voucher_ref_no = db.session.query(PaymentVoucher).order_by(PaymentVoucher.id.desc()).first()

        if request.method == "POST":

            if paymentVoucher_count < 1:
                voucher_no = 0
                random_string = ''
                for i in range(10):
                    random_string += random.choice(string.ascii_lowercase + string.ascii_uppercase)
                ref_no = f"{random_string}-{record.bill}-{voucher_no + 1}"
                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], record_id=record.id,
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
                                         amount=request.form["amount"], record_id=record.id,
                                         client_id=record.client_id)
                db.session.add(voucher)
                db.session.commit()
                flash('Voucher created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
        return render_template('create_payment_voucher.html', record=record, date_today=date_today)
    return render_template(Templates.login)


@app.route('/voucher-details/<int:voucher_id>', methods=['GET', 'POST'])
def voucher_details(voucher_id):
    if "username" in session:
        voucher = PaymentVoucher.query.filter_by(id=voucher_id).first()
        print(voucher.status.value)
        return render_template('voucher_details.html', voucher=voucher, PaymentStatus=PaymentStatus)
    return render_template(Templates.login)


@app.route('/approve-voucher/<int:voucher_id>', methods=['GET', 'POST'])
def approve_voucher(voucher_id):
    if "username" in session:
        date_today = datetime.date.today()
        voucher_to_update = PaymentVoucher.query.filter_by(id=voucher_id).first()
        voucher_to_update.approval_date = date_today
        voucher_to_update.status = PaymentStatus.approved.value
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


@app.route('/all-vouchers-list', methods=['GET', 'POST'])
def all_vouchers_list():
    if "username" in session:
        all_vouchers = PaymentVoucher.query.order_by(desc(PaymentVoucher.id)).all()
        return render_template('all_payment_vouchers_list.html', all_vouchers=all_vouchers)
    return render_template(Templates.login)


@app.route('/search-vouchers', methods=['POST', 'GET'])
def search_vouchers():
    if "username" in session:

        if request.method == 'GET':
            search = request.args['search'].lower()
            records = Records.query.filter(Records.bill.ilike(f"%{search}%")).all()
            clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
            record_ids = [record.id for record in records]
            client_ids = [client.id for client in clients]
            all_vouchers = PaymentVoucher.query.filter(PaymentVoucher.reference_no.ilike(f"%{search}%") |
                                                       PaymentVoucher.record_id.in_(
                                                           record_ids) | PaymentVoucher.client_id.in_(
                client_ids)).all()
            if all_vouchers:
                return render_template('all_payment_vouchers_list.html', all_vouchers=all_vouchers)
            flash('No Record Found')
            return redirect(url_for('all_vouchers_list'))
        return redirect(url_for('voucher_list'))
    return render_template(Templates.login)


# list of records with pending payment status
@app.route('/pending-payment-list')
def pending_payment_list():
    if "username" in session:

        records = Records.query.filter(Records.status == RecordStatus.pending.value).all()
        total = 0
        total_gst = 0
        deal_total = 0
        for i in records:
            client = Client.query.filter_by(id=i.client_id).first()
            total = round(float(client.final_deal) + total, 2)
            total_gst = round(float(client.gst) + total_gst, 2)
            deal_total = total - total_gst

        pending_list = Records.query.filter(Records.status == RecordStatus.pending.value).order_by(
            desc(Records.id)).all()
        return render_template(Templates.pending_list, pending_list=pending_list, total=total, deal_total=deal_total,
                               total_gst=total_gst)
    return render_template(Templates.login)


# list of records with received payment status
@app.route('/paid-payment-list')
def paid_payment_list():
    if "username" in session:

        total_amount = Records.query.filter(Records.status == RecordStatus.received.value).all()

        total = 0
        total_gst = 0
        deal_total = 0
        for i in total_amount:
            client = Client.query.filter_by(id=i.client_id).first()
            total = round(float(client.final_deal) + total, 2)
            total_gst = round(float(client.gst) + total_gst, 2)
            deal_total = round(float(total - total_gst), 2)
        print(deal_total)
        paid_list = Records.query.filter(Records.status == RecordStatus.received.value).order_by(desc(Records.id)).all()
        return render_template(Templates.paid_list, paid_list=paid_list, total=total, deal_total=deal_total,
                               total_gst=total_gst)
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
@app.route('/search', methods=['POST', 'GET'])
def search_records():
    if "username" in session:
        if request.method == 'GET':
            search = request.args['search'].lower()
            clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
            client_ids = [client.id for client in clients]
            all_records = Records.query.filter(
                Records.client_id.in_(client_ids) | Records.bill.ilike(f"%{search}%")).all()
            if all_records:
                return render_template(Templates.dashboard, all_records=all_records)
            flash('No Record Found')
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    return render_template(Templates.login)


# Search specific keyword in list of clients
@app.route('/clients', methods=['POST', 'GET'])
def search_clients():
    if "username" in session:
        if request.method == 'GET':
            search = request.args['search'].lower()
            clients = Client.query.filter(
                Client.client_name.ilike(f"%{search}%") | Client.phone_no.ilike(f"%{search}%") | Client.address.ilike(
                    f"%{search}%") | Client.email.ilike(f"%{search}%")).all()
            if clients:
                return render_template(Templates.client_list, clients=clients)
            else:
                flash('No Record Found')
                return redirect(url_for('all_client_names'))

    return render_template(Templates.login)


# delete multiple records using checkbox
@app.route('/get_checked_boxes', methods=['GET', 'POST'])
def get_checked_boxes():
    if 'username' in session and request.method == "POST":
        all_vouchers = PaymentVoucher.query.all()
        rec_ids = request.form['rec_ids']
        for ids in rec_ids.split(','):
            delete_rec = Records.query.filter_by(id=ids).first()

            for voucher in all_vouchers:
                if voucher.bill_no.bill == delete_rec.bill:
                    db.session.delete(voucher)

            db.session.delete(delete_rec)
            db.session.commit()
        flash("record_deleted", category='success')
        return redirect(url_for('dashboard'))

    return render_template(Templates.login)


# delete multiple clients using checkbox
@app.route('/get_checked_boxes_for_client', methods=['GET', 'POST'])
def get_checked_boxes_for_client():
    if 'username' in session and request.method == "POST":
        record_ids = request.form['rec_ids']

        for ids in record_ids.split(','):
            delete = Client.query.filter_by(id=ids).first()
            if Records.query.filter_by(client_id=delete.id).first():
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
                check_record_status = Records.query.filter_by(id=record_id).first()
                if check_record_status.status.value == RecordStatus.received.value:
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
            with open(Report_Generated_File + '\\' + file_name, mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow(
                    ['Id', 'Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Amount(Rs.)',
                     'Amount Received Date', 'Status'
                     ])
                for rec_id in rec_ids.split(','):
                    record = Records.query.filter_by(id=rec_id).first()

                    record.date_of_order = record.date_of_order

                    record.dop = record.dop

                    record.bill_date = record.bill_date

                    client = Client.query.filter_by(id=Records.client_id).first()
                    final = [record.id, record.client_id, record.content_advt, record.date_of_order,
                             record.dop, record.bill,
                             record.bill_date,
                             client.final_deal, record.amount_received_date, record.status.value]
                    write_file.writerow(final)
        else:
            file_name = 'Record.csv'
            with open(Report_Generated_File + '\\' + file_name, mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow(
                    ['Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Amount(Rs.)',
                     'Amount Received Date', 'Status'])
                for rec_id in rec_ids.split(','):
                    record = Records.query.filter_by(id=rec_id).first()
                    client = Client.query.filter_by(id=Records.client_id).first()
                    record.date_of_order = record.date_of_order
                    record.dop = record.dop
                    record.bill_date = record.bill_date
                    final = [record.client_name.client_name, record.content_advt, record.date_of_order,
                             record.dop, record.bill,
                             record.bill_date,
                             client.final_deal, record.amount_received_date, record.status.value]
                    write_file.writerow(final)
        return send_from_directory(Report_Generated_File, file_name, as_attachment=True)


# generate csv report for list of clients selected
@app.route('/csv-for-client', methods=['POST', 'GET'])
def csv_for_client():
    client_ids = request.form["check_rec_ids"]
    file_name = 'Clients.csv'
    with open(Client_List_File + '\\' + file_name, mode='w', newline='') as file:
        write_file = csv.writer(file)
        write_file.writerow(
            ['Name', 'Email', 'Phone No.', 'Address', 'Final Deal', 'GST', 'Credit'])
        for cli_id in client_ids.split(','):
            client = Client.query.filter_by(id=cli_id).first()
            final = [client.client_name, client.email, client.phone_no,
                     client.address, client.final_deal,
                     client.gst, client.credit_amount]
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
        record = Records.query.all()
        count = 0
        while count != len(read_file):

            if 'Id' in read_file.columns:
                if count >= len(read_file):
                    break
                else:

                    for row in record:
                        if count >= len(read_file):
                            break
                        if read_file.loc[count, 'Status'] == RecordStatus.pending.value:
                            read_file.loc[count, 'Status'] = RecordStatus.pending.value
                        elif read_file.loc[count, 'Status'] == RecordStatus.received.value:
                            read_file.loc[count, 'Status'] = RecordStatus.received.value
                        elif read_file.loc[count, 'Status'] == RecordStatus.cancelled.value:
                            read_file.loc[count, 'Status'] = RecordStatus.cancelled.value
                        if row.id == int(read_file.loc[count, 'Id']):
                            row.client_id = int(read_file.loc[count, 'Client'])
                            row.content_advt = read_file.loc[count, 'AD/GP/Others']
                            row.date_of_order = read_file.loc[count, 'RO Date']
                            row.dop = read_file.loc[count, 'DoP']
                            row.bill_date = read_file.loc[count, 'Bill Date']
                            row.status = read_file.loc[count, 'Status']
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
                                        address=None, final_deal=0, gst=0)
                    db.session.add(new_client)
                    db.session.commit()

                else:
                    if count >= len(read_file):
                        break
                    else:

                        if read_file.loc[count, 'Status'] == RecordStatus.pending.value:
                            read_file.loc[count, 'Status'] = RecordStatus.pending.value
                        elif read_file.loc[count, 'Status'] == RecordStatus.received.value:
                            read_file.loc[count, 'Status'] = RecordStatus.received.value
                        elif read_file.loc[count, 'Status'] == RecordStatus.cancelled.value:
                            read_file.loc[count, 'Status'] = RecordStatus.cancelled.value

                        bill_no_exists = db.session.query(db.exists().where(
                            str(Records.bill) == read_file.loc[count, 'Bill No.']))
                        print(bill_no_exists)
                        if bill_no_exists:
                            get_record_id = Records.query.filter_by(
                                bill=str(read_file.loc[count, 'Bill No.'])).first()
                            if get_record_id:
                                flash(f"Bill no {get_record_id.bill} already exists in the Database! \n"
                                      f"Duplicate Bill No. at Row No. {count + 2}.")
                                return redirect(url_for('file_upload'))

                            new_record = Records(client_id=get_client_id.id,
                                                 content_advt=read_file.loc[count, 'AD/GP/Others'],
                                                 date_of_order=datetime.datetime.strptime(
                                                     read_file.loc[count, 'RO Date'], "%d-%m-%Y").strftime("%Y-%m-%d"),
                                                 dop=datetime.datetime.strptime(read_file.loc[count, 'DoP'],
                                                                                "%d-%m-%Y").strftime("%Y-%m-%d"),
                                                 bill=int(read_file.loc[count, 'Bill No.']),
                                                 bill_date=datetime.datetime.strptime(read_file.loc[count, 'Bill Date'],
                                                                                      "%d-%m-%Y").strftime("%Y-%m-%d"),
                                                 amount_received_date=read_file.loc[count, 'Amount Received Date'],
                                                 )
                            db.session.add(new_record)
                            db.session.commit()
                            count += 1
        flash(f"{count} Record added", category="success")
    return render_template(Templates.file_upload)


if __name__ == "__main__":
    app.run()
