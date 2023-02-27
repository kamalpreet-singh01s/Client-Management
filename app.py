import csv
import datetime
import os
import re
import sys
import webbrowser
from datetime import timedelta

import pandas as pd
from flask import render_template, request, url_for, flash, redirect, session, send_from_directory, jsonify
from flask_migrate import Migrate
from flaskwebgui import FlaskUI
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash

from form import Form
from models import db, create_app, Client, SalesOrder, SalesOrderStatus, Users, PaymentVoucher, PaymentStatus, Gst
from templates import Templates

app = create_app()
migrate = Migrate(app, db, render_as_batch=True)

UPLOAD_FOLDER = os.path.join(os.curdir, 'data/uploadedBills')

ALLOWED_EXTENSIONS = {'pdf'}
Client_List_File = os.path.join(os.curdir, 'data/clientList')
Report_Generated_File = os.path.join(os.curdir, 'data/reportGenerated')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['Client_List_File'] = Client_List_File
app.config['reportGenerated'] = Report_Generated_File

# constants
email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
valid_email = "Enter a Valid Email"

date_now = datetime.date.today()
time_now = datetime.datetime.now()
last_updated = date_now.strftime("%d/%b/%Y")
last_updated_time = time_now.strftime("%I:%M %p")

No_Record_Found = 'No Record Found'


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


# Admin Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('list_of_sales_order', page=1))
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        for i in Users.query.all():
            if i.username == username and check_password_hash(i.password, password):
                session["username"] = i.username
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5)
                flash(f"Welcome {i.first_name} {i.last_name}", category='success')
                return redirect(url_for('list_of_sales_order', page=1))

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
                                 phone_no=request.form["phone_no"], password=hash_pass)
            exists = db.session.query(db.exists().where(
                Users.username == request.form["username"])).scalar()
            if exists:
                flash("User with same username already exists", category='error')
                return render_template(Templates.register)
            if userpass != confirm_userpass:
                flash("Password does not match", category='error')
                return render_template(Templates.register)
            pass_regex = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$"
            if not re.match(pass_regex, userpass):
                flash("Password must contain Minimum eight characters, at least one letter and one number:",
                      category='error')
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


# view/update admin
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


# delete multiple admins using checkbox
@app.route('/get_checked_boxes_for_admin', methods=['GET', 'POST'])
def get_checked_boxes_for_admin():
    if 'username' in session and request.method == "POST":
        sale_order_ids = request.form['rec_ids']

        for ids in sale_order_ids.split(','):
            user_to_del = Users.query.filter_by(id=ids).first()

            if session["username"] == user_to_del.username:
                flash('Cannot delete a user that is logged in', category='error')
                return redirect(url_for('manage_users'))
            db.session.delete(user_to_del)
            db.session.commit()
        flash("User Deleted", category='success')
        return redirect(url_for('manage_users'))

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
            if any(char.isdigit() for char in request.form["client_name"]):
                message = 'Name cannot contain numbers or any special character'

            if request.form["phone_no"].isalpha() or not len(request.form["phone_no"]) == 10:
                message = 'Not a Valid Phone number.'

            if not re.fullmatch(email_reg, request.form['email']):
                message = valid_email

            if message:
                flash(message, category='error')
                return render_template(Templates.add_client)
            else:

                added_client = Client(client_name=request.form["client_name"], email=request.form["email"],
                                      phone_no=request.form["phone_no"],
                                      address=request.form["address"], overall_payable=0, overall_received=0
                                      )

                db.session.add(added_client)
                db.session.commit()
                flash('Client Added', category='success')
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
@app.route('/client-deails/<int:client_id>', methods=['GET', 'POST'])
def update_client(client_id):
    if "username" in session:

        get_sale_orders = SalesOrder.query.filter_by(client_id=client_id).all()
        total = 0
        for i in get_sale_orders:
            if i.status.value == SalesOrderStatus.pending.value:
                total = total + i.total_amount
        print(total)

        client_to_update = Client.query.filter_by(id=client_id).first()

        if request.method == "POST":
            message = ''
            if any(char.isdigit() for char in request.form["client_name"]):
                message = 'Name cannot contain numbers or any special character. Client details not updated.'

            if not re.fullmatch(email_reg, request.form['email']):
                message = valid_email

            if request.form["phone_no"].isalpha() or len(request.form["phone_no"]) < 10:
                message = 'Not a Valid Phone number. Client details not updated.'

            if message:
                flash(message, category='error')
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
                               last_updated_time=last_updated_time
                               )
    return render_template(Templates.login)


# delete multiple clients using checkbox
@app.route('/get_checked_boxes_for_client', methods=['GET', 'POST'])
def get_checked_boxes_for_client():
    if 'username' in session and request.method == "POST":
        sale_order_ids = request.form['rec_ids']

        for ids in sale_order_ids.split(','):
            delete = Client.query.filter_by(id=ids).first()
            if SalesOrder.query.filter_by(client_id=delete.id).first():
                flash("Client in use", category='error')
                return redirect(url_for('all_client_names', page=1))
            db.session.delete(delete)
            db.session.commit()
        flash("Client Deleted", category='success')
        return redirect(url_for('all_client_names', page=1))

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
                    f"%{search}%") | Client.email.ilike(f"%{search}%")).all()
            if clients:
                clients = Client.query.filter(
                    Client.client_name.ilike(f"%{search}%") | Client.phone_no.ilike(
                        f"%{search}%") | Client.address.ilike(
                        f"%{search}%") | Client.email.ilike(f"%{search}%")).paginate(page=page, per_page=per_page,
                                                                                     error_out=False)
                return render_template(Templates.client_list, clients=clients, search=search)
            else:
                flash(No_Record_Found, category='error')
                return redirect(url_for('all_client_names', page=1))
        return redirect(url_for('all_client_names', page=1))
    return render_template(Templates.login)


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
            sale_order = SalesOrder.query.filter_by(client_id=cli_id).all()
            for i in sale_order:
                if i.status.value == SalesOrderStatus.received.value:
                    overall_payment_total = overall_payment_total + i.total_amount

            final = [client.client_name, client.email, client.phone_no,
                     client.address, overall_payment_total, client.credit_amount]
            print(final)
            write_file.writerow(final)

    return send_from_directory(Client_List_File, file_name, as_attachment=True)


# list of Sales Orders
@app.route('/sales-orders/<int:page>', methods=['GET', 'POST'])
def list_of_sales_order(page):
    if "username" in session:
        per_page = 7

        all_sales_order_paginate = SalesOrder.query.order_by(SalesOrder.bill.desc()).paginate(page=page,
                                                                                              per_page=per_page,
                                                                                              error_out=False)
        all_sales_order_count = db.session.query(SalesOrder).count()

        all_sales_order = SalesOrder.query.all()

        for i in all_sales_order:
            voucher_count = PaymentVoucher.query.filter(PaymentVoucher.sales_order_id == i.id).all()
            print(len(voucher_count))

            client = Client.query.filter_by(id=i.client_id).first()
            print(client.overall_payable)

        tax_total = 0

        total_received = 0
        total_payable = 0

        all_clients = Client.query.all()

        for i in all_clients:
            total_received = round(float(i.overall_received) + total_received, 2)

        for i in all_clients:
            total_payable = round(float(i.overall_payable) + total_payable, 2)

        for i in all_sales_order:
            if i.status.value == SalesOrderStatus.received.value:
                tax_total = round(float(i.gst_amount) + tax_total, 2)

        return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order_paginate,
                               final_deal_total=total_received,
                               pending_final_total=total_payable, all_SalesOrder_count=all_sales_order_count,
                               tax_total=tax_total)
    return render_template(Templates.login)


# onchange get credit amount
@app.route('/get_credit_list/<client_name>')
def get_credit_list(client_name):
    client_results = Client.query.filter_by(id=client_name).all()
    credit_list = []
    for client in client_results:
        client_obj = {

            'client_id': client.id,
            'client_credit_amount': client.credit_amount
        }
        credit_list.append(client_obj)

    return jsonify({'credit_list': credit_list})


# create a new sale order
@app.route('/add-sale-order', methods=['GET', 'POST'])
def add_sale_order():
    date_today = datetime.date.today()
    print(date_today)
    if "username" in session:
        form = Form()
        form.client_name.choices = [(client.id, client.client_name) for client in Client.query.all()]
        bill_no = db.session.query(SalesOrder).order_by(SalesOrder.id.desc()).first()
        if bill_no:
            bill_no = int(bill_no.bill) + 1
        else:
            bill_no = 1

        client_table_len = db.session.query(Client).count()

        if request.method == "POST":

            if client_table_len < 1:
                flash('Please Add a Client before creating Sale Order', category='error')
                return render_template(Templates.add_sale_order, form=form, date_today=date_today, bill_no=bill_no)

            exists = db.session.query(SalesOrder.bill).filter_by(bill=request.form["bill"]).first() is not None
            if exists:
                flash('Bill No. already exists', category='error')
                return render_template(Templates.add_sale_order, form=form)

            get_file = request.files['file']

            if get_file:
                filename = 'Bill No' + '-' + request.form["bill"] + '-' + request.form["date_of_order"] + '.pdf'
                get_file.save(os.path.join(UPLOAD_FOLDER, filename))

                sale_order = SalesOrder(request.form["client_name"], request.form["content_advt"],
                                        request.form["date_of_order"], request.form["dop"], request.form["bill"],
                                        request.form["bill_date"], request.form["amount_by_user"],
                                        request.form["gst_amount"],
                                        gst=request.form['gst'],
                                        total_amount=request.form['total_amount_including_gst'],
                                        filename=os.path.join(UPLOAD_FOLDER, filename), total_paid=0,
                                        total_payable=request.form['total_amount_including_gst'],
                                        adjusted_credit=0
                                        )

                db.session.add(sale_order)
                client = Client.query.filter_by(id=request.form["client_name"]).first()
                client.overall_payable = client.overall_payable + float(request.form["total_amount_including_gst"])
                db.session.commit()
                flash(f'Sales Order With Bill No. {request.form["bill"]} Created Successfully', category='success')
                return redirect(url_for('list_of_sales_order', page=1))
            else:
                sale_order = SalesOrder(client_id=request.form["client_name"],
                                        content_advt=request.form["content_advt"],
                                        date_of_order=date_today,
                                        dop=date_today, bill=bill_no,
                                        bill_date=date_today,
                                        amount=round(float(request.form["amount_by_user"]), 2),
                                        gst_amount=float(request.form["gst_amount"]),
                                        total_amount=request.form['total_amount_including_gst'],
                                        gst=request.form["gst"],
                                        filename=None, total_paid=0,
                                        total_payable=request.form['total_amount_including_gst'], adjusted_credit=0)

                db.session.add(sale_order)
                client = Client.query.filter_by(id=request.form["client_name"]).first()
                client.overall_payable = client.overall_payable + float(request.form["total_amount_including_gst"])

                db.session.commit()
                flash(f'Sales Order With Bill No. {request.form["bill"]} Created Successfully', category='success')
                return redirect(url_for('list_of_sales_order', page=1))
        return render_template(Templates.add_sale_order, form=form, date_today=date_today, bill_no=bill_no)
    return render_template(Templates.login)


# view/update sale order details
@app.route('/sale-order-details/<int:sale_order_id>', methods=['GET', 'POST'])
def sale_order_details(sale_order_id):
    if "username" in session:

        sale_order_to_update = SalesOrder.query.filter_by(id=sale_order_id).first()

        get_gst_percentage = sale_order_to_update.gst

        client = Client.query.filter(Client.id == sale_order_to_update.client_id).first()
        form = Form()

        form.client_name.choices = [(client.id, client.client_name) for client in Client.query.all()]
        total_vouchers_in_sale_order = PaymentVoucher.query.filter_by(sales_order_id=sale_order_id).all()
        total_vouchers = len(total_vouchers_in_sale_order)
        if request.method == "POST":

            client.email = request.form["email"]

            if not re.fullmatch(email_reg, request.form['email']):
                message = valid_email
                flash(message + '.' + ' ' + 'Sale Order Not Updated.', category='danger')
                return redirect(url_for('sale_order_details', sale_order_id=sale_order_id))
            client.phone_no = request.form["phone_no"]

            if not request.form["phone_no"].isdigit():
                message = 'Phone number cannot contain Alphabets or any special symbol. Sale Order Not Updated'
                flash(message, category='error')
                return redirect(url_for('sale_order_details', sale_order_id=sale_order_id))
            if request.form["total_amount_including_gst"].isalpha():
                message = 'Final deal amount cannot contain Alphabets or any special symbol. Record Not Updated'
                flash(message, category='error')
                return redirect(url_for('sale_order_details', sale_order_id=sale_order_id))
            sale_order_to_update.client_id = request.form["client_name"]
            sale_order_to_update.content_advt = request.form["content_advt"]
            sale_order_to_update.date_of_order = request.form["date_of_order"]
            sale_order_to_update.dop = request.form["dop"]
            sale_order_to_update.gst = request.form["gst"]
            sale_order_to_update.gst_amount = request.form["gst_amount"]
            sale_order_to_update.amount = request.form["amount_by_user"]

            if float(request.form['adjust_credit_textbox']) == 0:
                if float(request.form["total_amount_including_gst"]) != float(request.form["previous_total_amount"]):
                    sale_order_to_update.total_amount = request.form["total_amount_including_gst"]
                    client.overall_payable = (client.overall_payable - float(
                        request.form["previous_total_amount"])) + float(request.form["total_amount_including_gst"])
                    print(client.overall_payable, 'cli overall')
                else:
                    sale_order_to_update.total_amount = request.form["total_amount_including_gst"]

            if float(request.form['adjust_credit_textbox']) == float(request.form["total_amount_including_gst"]):
                sale_order_to_update.total_payable = float(request.form['total_payable_amount'])
                sale_order_to_update.adjusted_credit = float(request.form["total_amount_including_gst"]) - float(
                    request.form["total_payable_amount"])
                client.credit_amount = client.credit_amount - sale_order_to_update.adjusted_credit
                sale_order_to_update.total_paid = sale_order_to_update.total_paid + float(
                    request.form["adjust_credit_textbox"])

                client.overall_payable = client.overall_payable - float(request.form['adjust_credit_textbox'])
                client.overall_received = client.overall_received + float(request.form["total_amount_including_gst"])

            if float(request.form['adjust_credit_textbox']) > float(request.form["total_amount_including_gst"]):
                sale_order_to_update.total_payable = float(request.form['total_payable_amount'])
                sale_order_to_update.adjusted_credit = client.credit_amount - float(
                    request.form["total_amount_including_gst"])
                client.credit_amount = client.credit_amount - sale_order_to_update.adjusted_credit

                client.overall_payable = client.overall_payable - float(request.form['adjust_credit_textbox'])
                client.overall_received = client.overall_received + float(request.form["total_amount_including_gst"])

            if float(request.form['adjust_credit_textbox']) < float(request.form["total_amount_including_gst"]):
                sale_order_to_update.total_payable = float(request.form['total_payable_amount'])
                sale_order_to_update.adjusted_credit = float(request.form['adjust_credit_textbox'])

                sale_order_to_update.total_paid = sale_order_to_update.total_paid + float(
                    request.form['adjust_credit_textbox'])

                client.credit_amount = client.credit_amount - float(request.form['adjust_credit_textbox'])
                client.overall_payable = client.overall_payable - float(request.form['adjust_credit_textbox'])
                client.overall_received = client.overall_received + float(request.form['adjust_credit_textbox'])

            if float(request.form["total_amount_including_gst"]) != float(request.form["previous_total_amount"]):

                if float(request.form["total_amount_including_gst"]) > client.overall_payable:
                    client.overall_payable = float(request.form["total_amount_including_gst"]) - client.overall_payable

                    sale_order_to_update.total_amount = request.form["total_amount_including_gst"]
                    sale_order_to_update.total_payable = float(request.form["total_payable_amount"])

                    print(client.overall_payable, 'cli overall')

                elif float(request.form["total_amount_including_gst"]) < client.overall_payable:
                    client.overall_payable = client.overall_payable - float(request.form["total_amount_including_gst"])
                    sale_order_to_update.total_amount = request.form["total_amount_including_gst"]
                    sale_order_to_update.total_payable = float(request.form["total_payable_amount"])

            else:
                sale_order_to_update.total_amount = request.form["total_amount_including_gst"]

            get_file = request.files['file']
            if request.files['file']:
                filename = 'Bill No' + '-' + str(sale_order_to_update.bill) + '-' + str(
                    sale_order_to_update.date_of_order) + '.pdf'
                get_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                sale_order_to_update.filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if float(sale_order_to_update.total_paid) >= float(sale_order_to_update.total_amount):
                print("testing")
                sale_order_to_update.total_paid = sale_order_to_update.total_amount

                sale_order_to_update.status = SalesOrderStatus.received.value
                sale_order_to_update.amount_received_date = date_now

            db.session.commit()

            flash('Sales Order Updated', category='success')
            return redirect(url_for('sale_order_details', sale_order_id=sale_order_to_update.id))

        if get_gst_percentage == str(Gst.percent_12.value):
            form.client_name.default = sale_order_to_update.client_id
            form.gst.default = Gst.percent_12.value
            form.process()
        elif get_gst_percentage == str(Gst.percent_5.value):
            form.client_name.default = sale_order_to_update.client_id
            form.gst.default = Gst.percent_5.value
            form.process()
        elif get_gst_percentage == str(Gst.percent_18.value):
            form.client_name.default = sale_order_to_update.client_id
            form.gst.default = Gst.percent_18.value
            form.process()
        elif get_gst_percentage == str(Gst.percent_28.value):
            form.client_name.default = sale_order_to_update.client_id
            form.gst.default = Gst.percent_28.value
            form.process()

        return render_template(Templates.sale_order_details, sale_order_to_update=sale_order_to_update, form=form,
                               last_updated=last_updated, client=client, last_updated_time=last_updated_time,
                               total_vouchers=total_vouchers, SalesOrderStatus=SalesOrderStatus)

    return render_template(Templates.login)


# opens attachment linked to a sale order
@app.route('/download/<path:filename>/<int:sale_order_id>')
def download(filename, sale_order_id):
    if "username" in session:
        uploads = os.path.join(filename)
        webbrowser.open_new_tab(uploads)
        return redirect(url_for('sale_order_details', sale_order_id=sale_order_id))
    return render_template(Templates.login)


# set sale order payment status to cancelled
@app.route('/set-cancel/<int:sale_order_id>', methods=['GET', 'POST'])
def set_cancel(sale_order_id):
    form = Form()
    sale_order_to_update = SalesOrder.query.filter_by(id=sale_order_id).first()
    client = Client.query.filter(Client.id == sale_order_to_update.client_id).first()

    sale_order_to_update.status = SalesOrderStatus.cancelled.value
    sale_order_to_update.amount_received_date = date_now
    client.overall_payable = client.overall_payable - sale_order_to_update.total_amount
    db.session.commit()
    flash('Sales Order Cancelled', category='success')

    return render_template(Templates.sale_order_details, sale_order_to_update=sale_order_to_update, form=form,
                           last_updated=last_updated, client=client, last_updated_time=last_updated_time,
                           SalesOrderStatus=SalesOrderStatus)


# delete multiple sales orders using checkbox
@app.route('/get_checked_boxes', methods=['GET', 'POST'])
def get_checked_boxes():
    if 'username' in session and request.method == "POST":
        all_vouchers = PaymentVoucher.query.all()

        rec_ids = request.form['rec_ids']
        for ids in rec_ids.split(','):

            delete_rec = SalesOrder.query.filter_by(id=ids).first()
            print(delete_rec.status.value)
            payment_voucher = PaymentVoucher.query.filter_by(sales_order_id=ids).first()
            payment_voucher_list = PaymentVoucher.query.filter_by(sales_order_id=ids).all()
            [print(i) for i in payment_voucher_list]

            if payment_voucher is None:

                client = Client.query.filter_by(id=delete_rec.client_id).first()

                client.overall_payable = client.overall_payable - (delete_rec.total_amount)
            else:
                client = Client.query.filter_by(id=delete_rec.client_id).first()

                client.overall_payable = client.overall_payable - (delete_rec.total_amount - payment_voucher.amount)

            if len(payment_voucher_list) > 0:
                flash(f"Cannot delete Sale order with bill no. {delete_rec.bill} because it contains a voucher",
                      category='error')
                return redirect(url_for('list_of_sales_order', page=1))

            if delete_rec.status.value == SalesOrderStatus.received.value or delete_rec.status.value == SalesOrderStatus.cancelled.value:
                flash(f"Cannot make changes to bill no. {delete_rec.bill}",
                      category='error')
                return redirect(url_for('list_of_sales_order', page=1))
            if delete_rec.adjusted_credit > 0:
                flash(f"Cannot delete Sale order with bill no. {delete_rec.bill}. Some Credit amount is being used.",
                      category='error')
                return redirect(url_for('list_of_sales_order', page=1))

            for voucher in all_vouchers:

                if voucher.bill_no.bill == delete_rec.bill:
                    db.session.delete(voucher)
            if delete_rec.filename:
                os.remove(delete_rec.filename)
            db.session.delete(delete_rec)
            db.session.commit()
            flash(f"Sales Order with bill no. {delete_rec.bill} Deleted", category='success')
        return redirect(url_for('list_of_sales_order', page=1))

    return render_template(Templates.login)


# Search specific keyword in list of sale orders
@app.route('/sales-order/<int:page>', methods=['POST', 'GET'])
def search_sale_orders(page):
    per_page = 8
    if "username" in session:
        if request.method == 'GET':
            search = request.args['search'].lower()

            clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
            client_ids = [client.id for client in clients]
            all_sales_order_count = db.session.query(SalesOrder).count()
            all_sales_order = SalesOrder.query.filter(
                SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).all()
            if all_sales_order:
                all_sales_order = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).paginate(page=page,
                                                                                                          per_page=per_page,
                                                                                                          error_out=False)

                total_amount_total = 0
                pending_final_total = 0

                for i in all_sales_order:
                    if i.status.value == SalesOrderStatus.received.value:
                        total_amount_total = round(float(i.total_amount) + total_amount_total, 2)
                    elif i.status.value == SalesOrderStatus.pending.value:
                        pending_final_total = round(float(i.total_amount) + pending_final_total, 2)

                return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order,
                                       all_SalesOrder_count=all_sales_order_count, search=search,
                                       final_deal_total=total_amount_total, pending_final_total=pending_final_total)

            flash(No_Record_Found)
            return redirect(url_for('list_of_sales_order', page=1))
        return redirect(url_for('list_of_sales_order', page=1))
    return render_template(Templates.login)


# list of sales orders based on payment status
@app.route('/sales-order/<string:filter_by>/<int:page>')
def filter_payment_status(filter_by, page):
    if "username" in session:
        per_page = 8

        if filter_by == 'pending':
            print(filter_by)
            pending_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.pending.value).all()

            pending_total = 0

            for i in pending_amount:
                pending_total = round(float(i.total_amount) + pending_total, 2)

            if request.args.get('search', ''):
                search = request.args['search'].lower()

                clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
                client_ids = [client.id for client in clients]
                all_sales_order_count = db.session.query(SalesOrder).count()
                all_sales_order = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).filter(
                    SalesOrder.status == SalesOrderStatus.pending.value).all()

                pending_total = 0

                for i in all_sales_order:
                    print(i)
                    pending_total = round(float(i.total_amount) + pending_total, 2)
                if all_sales_order:
                    all_sales_order = SalesOrder.query.filter(
                        SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(
                            f"%{search}%")).filter(SalesOrder.status == SalesOrderStatus.pending.value).paginate(
                        page=page,
                        per_page=per_page,
                        error_out=False)

                    return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order,
                                           all_SalesOrder_count=all_sales_order_count, pending_total=pending_total,
                                           search=search,
                                           filter_by=filter_by)
                flash(No_Record_Found)

            all_sales_order = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.pending.value).order_by(
                desc(SalesOrder.id)).paginate(page=page, per_page=per_page, error_out=False)
            return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order,
                                   pending_total=pending_total, filter_by=filter_by)

        elif filter_by == 'received':
            received_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.received.value).all()

            received_total = 0

            for i in received_amount:
                received_total = round(float(i.total_amount) + received_total, 2)

            if request.args.get('search', ''):
                search = request.args['search'].lower()

                clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
                client_ids = [client.id for client in clients]
                all_sales_order_count = db.session.query(SalesOrder).count()
                all_sales_order = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).filter(
                    SalesOrder.status == SalesOrderStatus.received.value).all()

                received_total = 0

                for i in all_sales_order:
                    received_total = round(float(i.total_amount) + received_total, 2)

                if all_sales_order:
                    all_sales_order = SalesOrder.query.filter(
                        SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(
                            f"%{search}%")).filter(SalesOrder.status == SalesOrderStatus.received.value).paginate(
                        page=page,
                        per_page=per_page,
                        error_out=False)

                    return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order,
                                           all_SalesOrder_count=all_sales_order_count, received_total=received_total,
                                           search=search,
                                           filter_by=filter_by)
                flash(No_Record_Found)
            all_sales_order = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.received.value).order_by(
                desc(SalesOrder.id)).paginate(page=page, per_page=per_page, error_out=False)
            return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order,
                                   received_total=received_total,
                                   filter_by=filter_by)

        elif filter_by == 'cancelled':
            received_amount = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.cancelled.value).all()

            cancelled_total = 0

            for i in received_amount:
                cancelled_total = round(float(i.total_amount) + cancelled_total, 2)

            if request.args.get('search', ''):
                search = request.args['search'].lower()

                clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
                client_ids = [client.id for client in clients]
                all_sales_order_count = db.session.query(SalesOrder).count()
                all_sales_order = SalesOrder.query.filter(
                    SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(f"%{search}%")).filter(
                    SalesOrder.status == SalesOrderStatus.received.value).all()

                cancelled_total = 0

                for i in received_amount:
                    cancelled_total = round(float(i.total_amount) + cancelled_total, 2)

                if all_sales_order:
                    all_sales_order = SalesOrder.query.filter(
                        SalesOrder.client_id.in_(client_ids) | SalesOrder.bill.ilike(
                            f"%{search}%")).filter(SalesOrder.status == SalesOrderStatus.cancelled.value).paginate(
                        page=page,
                        per_page=per_page,
                        error_out=False)
                    return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order,
                                           all_SalesOrder_count=all_sales_order_count, cancelled_total=cancelled_total,
                                           search=search,
                                           filter_by=filter_by)
                flash(No_Record_Found)
            all_sales_order = SalesOrder.query.filter(SalesOrder.status == SalesOrderStatus.cancelled.value).order_by(
                desc(SalesOrder.id)).paginate(page=page, per_page=per_page, error_out=False)
            return render_template(Templates.list_of_sales_order, all_SalesOrder=all_sales_order,
                                   cancelled_total=cancelled_total,
                                   filter_by=filter_by)
    return render_template(Templates.login)


# generate csv report for list of sales orders selected
@app.route('/csv_file_sale_order_to_update', methods=['POST', 'GET'])
def csv_file_sale_order_to_update():
    if 'username' in session and request.method == "POST":
        rec_ids = request.form["check_rec_ids"]
        # if update_record checkbox is checked, id's of clients and record is included in the csv file else excluded
        if request.form.get("update_check"):

            file_name = 'Update_sale_order.csv'
            with open(os.path.join(Report_Generated_File, file_name), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow(
                    ['Id', 'Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Amount(Rs.)', 'GST(%)',
                     'GST(Rs.)',
                     'Total(Including GST)', 'Amount Received Date'])
                for rec_id in rec_ids.split(','):
                    sale_order = SalesOrder.query.filter_by(id=rec_id).first()
                    if sale_order.status.value == SalesOrderStatus.pending.value:
                        final = [sale_order.id, sale_order.client_id, sale_order.content_advt, sale_order.date_of_order,
                                 sale_order.dop, sale_order.bill,
                                 sale_order.bill_date, sale_order.amount, sale_order.gst, sale_order.gst_amount,
                                 sale_order.total_amount, sale_order.amount_received_date]
                        write_file.writerow(final)
        else:
            file_name = 'sale_order.csv'
            with open(os.path.join(Report_Generated_File, file_name), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow(['Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Amount(Rs.)',
                                     'GST(%)', 'GST(Rs.)',
                                     'Total(Including GST)', 'Amount Received Date'])
                for rec_id in rec_ids.split(','):
                    sale_order = SalesOrder.query.filter_by(id=rec_id).first()

                    final = [sale_order.client_name.client_name, sale_order.content_advt, sale_order.date_of_order,
                             sale_order.dop, sale_order.bill,
                             sale_order.bill_date, sale_order.amount, sale_order.gst, sale_order.gst_amount,
                             sale_order.total_amount, sale_order.amount_received_date]
                    write_file.writerow(final)
        return send_from_directory(Report_Generated_File, file_name, as_attachment=True)


# List of payment vouchers
@app.route('/all-vouchers-list/<int:page>', methods=['GET', 'POST'])
def all_vouchers_list(page):
    per_page = 8
    if "username" in session:
        all_vouchers = PaymentVoucher.query.order_by(desc(PaymentVoucher.id)).paginate(page=page, per_page=per_page,
                                                                                       error_out=False)
        return render_template('list_of_all_payment_vouchers.html', all_vouchers=all_vouchers)
    return render_template(Templates.login)


# delete multiple payment vouchers in different sales order using checkbox
@app.route('/get_checked_boxes_for_all_payment_vouchers', methods=['GET', 'POST'])
def get_checked_boxes_for_all_payment_vouchers():
    if 'username' in session and request.method == "POST":
        rec_ids = request.form['rec_ids']
        for ids in rec_ids.split(','):

            get_sale_order = SalesOrder.query.filter(PaymentVoucher.id == ids).first()
            delete = PaymentVoucher.query.filter_by(id=ids).first()

            if get_sale_order.status.value == SalesOrderStatus.received.value:
                flash("Cannot make changes to Sales order voucher with status Received", category='error')
                return redirect(url_for('all_vouchers_list', page=1))
            if delete.status.value == PaymentStatus.approved.value:
                flash("Cannot make changes to voucher with status Approved", category='error')
                return redirect(url_for('all_vouchers_list', page=1))

            db.session.delete(delete)
            db.session.commit()
        flash("Voucher Deleted", category='success')
        return redirect(url_for('all_vouchers_list', page=1))

    return render_template(Templates.login)


# List of payment vouchers for particular sales order
@app.route('/voucher-list/<int:sale_order_id>', methods=['GET', 'POST'])
def voucher_list(sale_order_id):
    if 'username' in session:
        sale_order = SalesOrder.query.filter_by(id=sale_order_id).first()
        client = Client.query.filter(Client.id == sale_order.client_id).first()
        total_amount = 0
        total_vouchers = PaymentVoucher.query.filter_by(sales_order_id=sale_order.id).all()
        total_voucher_count = len(total_vouchers)
        for voucher in total_vouchers:
            if voucher.status.value == PaymentStatus.approved.value:
                total_amount = total_amount + voucher.amount
        if float(total_amount) >= sale_order.total_amount:
            sale_order.status = SalesOrderStatus.received.value
            db.session.commit()

        return render_template('list_of_sale_order_vouchers.html', total_vouchers=total_vouchers, sale_order=sale_order,
                               total_amount=total_amount, client=client, SalesOrderStatus=SalesOrderStatus,
                               total_voucher_count=total_voucher_count)
    return render_template(Templates.login)


# create new payment voucher
@app.route('/create-payment-voucher/<int:sale_order_id>', methods=['GET', 'POST'])
def create_payment_voucher(sale_order_id):
    if "username" in session:
        sale_order = SalesOrder.query.filter_by(id=sale_order_id).first()
        date_today = datetime.date.today()
        payment_voucher_count = db.session.query(PaymentVoucher).count()

        last_voucher_ref_no = db.session.query(PaymentVoucher).order_by(PaymentVoucher.id.desc()).first()

        if request.method == "POST":

            if payment_voucher_count < 1:
                voucher_no = 0

                voucher_no += 1
                ref_no = f"PAY-{sale_order.bill}-{voucher_no + 1}"
                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=sale_order.id,
                                         client_id=sale_order.client_id)
                db.session.add(voucher)
                db.session.commit()
                flash('Payment Voucher Created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
            else:

                ref_no = f"PAY-{sale_order.bill}-{int(last_voucher_ref_no.reference_no.split('-')[-1]) + 1}"

                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=sale_order.id,
                                         client_id=sale_order.client_id)
                db.session.add(voucher)
                db.session.commit()
                flash('Payment Voucher Created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
        return render_template('create_payment_voucher.html', sale_order=sale_order, date_today=date_today)
    return render_template(Templates.login)


# get client dropdown based on bill number
@app.route('/get_client_list/<bill_no>')
def get_client_list(bill_no):
    sale_orders = SalesOrder.query.filter_by(id=bill_no).first()
    client_results = SalesOrder.query.filter_by(bill=sale_orders.bill).all()
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


# create sale order payment voucher using bill number dropdown
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

                ref_no = f"PAY-{request.form['bill_no']}-{voucher_no + 1}"
                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=bill_no.id,
                                         client_id=client.id)
                db.session.add(voucher)
                db.session.commit()
                flash('Voucher created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
            else:

                ref_no = f"PAY-{request.form['bill_no']}-{int(last_voucher_ref_no.reference_no.split('-')[-1]) + 1}"

                voucher = PaymentVoucher(reference_no=ref_no, payment_date=date_today,
                                         amount=request.form["amount"], sales_order_id=bill_no.id,
                                         client_id=client.id)
                db.session.add(voucher)
                db.session.commit()
                flash('Voucher created', category='success')
                return redirect(url_for('voucher_details', voucher_id=voucher.id))
        return render_template('create_payment_voucher_with_bill.html', form=form, date_today=date_today)
    return render_template(Templates.login)


# view payment voucher details
@app.route('/voucher-details/<int:voucher_id>', methods=['GET', 'POST'])
def voucher_details(voucher_id):
    if "username" in session:
        voucher = PaymentVoucher.query.filter_by(id=voucher_id).first()
        sale_order = SalesOrder.query.filter_by(bill=voucher.bill_no.bill).first()
        return render_template('payment_voucher_details.html', voucher=voucher, PaymentStatus=PaymentStatus,
                               sale_order=sale_order)
    return render_template(Templates.login)


# approve a payment voucher created
@app.route('/approve-voucher/<int:voucher_id>', methods=['GET', 'POST'])
def approve_voucher(voucher_id):
    if "username" in session:

        date_today = datetime.date.today()
        voucher_to_update = PaymentVoucher.query.filter_by(id=voucher_id).first()
        voucher_to_update.approval_date = date_today
        voucher_to_update.status = PaymentStatus.approved.value
        total_amount = 0
        sale_order = SalesOrder.query.filter_by(bill=voucher_to_update.bill_no.bill).first()
        client = Client.query.filter_by(id=sale_order.client_id).first()
        total_vouchers = PaymentVoucher.query.filter(PaymentVoucher.sales_order_id == sale_order.id).all()


        if client.credit_amount == 0 and voucher_to_update.amount == client.overall_payable:
            print("test")
            if voucher_to_update.amount < sale_order.total_payable:
                print("smaller")
                sale_order.total_payable = sale_order.total_payable - voucher_to_update.amount
                sale_order.total_paid = sale_order.total_paid + voucher_to_update.amount
                client.overall_payable = client.overall_payable - voucher_to_update.amount
                client.overall_received = client.overall_received + voucher_to_update.amount

            else:
                print("greater")
                client.credit_amount = client.credit_amount + (voucher_to_update.amount - sale_order.total_payable)
                sale_order.total_paid = sale_order.total_paid + sale_order.total_payable
                client.overall_payable = client.overall_payable - sale_order.total_payable
                client.overall_received = client.overall_received + sale_order.total_payable
                sale_order.total_payable = 0

        elif client.credit_amount == 0 and voucher_to_update.amount < client.overall_payable:
            print("voucher smaller")
            if voucher_to_update.amount < sale_order.total_payable:
                print("smaller")
                sale_order.total_payable = sale_order.total_payable - voucher_to_update.amount
                sale_order.total_paid = sale_order.total_paid + voucher_to_update.amount
                client.overall_payable = client.overall_payable - voucher_to_update.amount
                client.overall_received = client.overall_received + voucher_to_update.amount

            else:
                print("greater")
                client.credit_amount = client.credit_amount + (voucher_to_update.amount - sale_order.total_payable)
                sale_order.total_paid = sale_order.total_paid + sale_order.total_payable
                client.overall_payable = client.overall_payable - sale_order.total_payable
                client.overall_received = client.overall_received + sale_order.total_payable
                sale_order.total_payable = 0


        elif client.credit_amount == 0 and voucher_to_update.amount > client.overall_payable:
            print("voucher greater")
            client.credit_amount = client.credit_amount + (voucher_to_update.amount - client.overall_payable)
            client.overall_received = client.overall_received + client.overall_payable
            client.overall_payable = 0
            sale_order.total_payable = 0
            sale_order.total_paid = sale_order.total_amount

        elif client.credit_amount > voucher_to_update.amount:
            print("credit greater")
            client.overall_payable = client.overall_payable - voucher_to_update.amount
            client.overall_received = client.overall_received + voucher_to_update.amount
            # client.credit_amount = client.credit_amount - voucher_to_update.amount

            sale_order.total_payable = sale_order.total_payable - voucher_to_update.amount
            sale_order.total_paid = sale_order.total_paid + voucher_to_update.amount
            # client.credit_amount = 0

        elif client.credit_amount < voucher_to_update.amount:
            print("credit less")
            # client.overall_received = client.overall_received + (voucher_to_update.amount - client.overall_payable)
            # client.overall_payable = client.overall_payable - (voucher_to_update.amount - client.overall_payable)

            if voucher_to_update.amount < sale_order.total_payable:
                sale_order.total_payable = sale_order.total_payable - voucher_to_update.amount
                # if sale_order.total_payable < 0:
                #     sale_order.total_payable = 0
                sale_order.total_paid = sale_order.total_paid + voucher_to_update.amount
                client.overall_received = client.overall_received + voucher_to_update.amount
                client.overall_payable = client.overall_payable - voucher_to_update.amount
            else:
                client.credit_amount = client.credit_amount + (voucher_to_update.amount - sale_order.total_payable)
                sale_order.total_paid = sale_order.total_paid + sale_order.total_payable
                client.overall_payable = client.overall_payable - sale_order.total_payable
                client.overall_received = client.overall_received + sale_order.total_payable
                sale_order.total_payable = 0




        elif client.credit_amount == voucher_to_update.amount:
            print("equal")
            if voucher_to_update.amount < sale_order.total_payable:
                sale_order.total_payable = sale_order.total_payable - voucher_to_update.amount
                sale_order.total_paid = sale_order.total_paid + voucher_to_update.amount
                client.overall_received = client.overall_received + voucher_to_update.amount
                client.overall_payable = client.overall_payable - voucher_to_update.amount
            else:
                client.credit_amount = client.credit_amount + (voucher_to_update.amount - sale_order.total_payable)
                sale_order.total_paid = sale_order.total_paid + sale_order.total_payable
                client.overall_payable = client.overall_payable - sale_order.total_payable
                client.overall_received = client.overall_received + sale_order.total_payable
                sale_order.total_payable = 0


        if sale_order.total_paid >= sale_order.total_amount:
            sale_order.status = SalesOrderStatus.received.value
            sale_order.amount_received_date = date_today

        print(total_amount)

        db.session.commit()
        flash('Voucher Updated', category='success')
        return redirect(url_for('voucher_details', voucher_id=voucher_id))
    return render_template(Templates.login)


# cancel a payment voucher created
@app.route('/cancel-voucher/<int:voucher_id>', methods=['GET', 'POST'])
def cancel_voucher(voucher_id):
    if "username" in session:
        voucher_to_update = PaymentVoucher.query.filter_by(id=voucher_id).first()

        voucher_to_update.status = PaymentStatus.cancelled.value
        db.session.commit()
        flash('Voucher Updated', category='success')
        return redirect(url_for('voucher_details', voucher_id=voucher_id))
    return render_template(Templates.login)


# delete multiple payment vouchers in specific sales order using checkbox
@app.route('/get_checked_boxes_for_payment_vouchers/<int:sale_order_id>', methods=['GET', 'POST'])
def get_checked_boxes_for_payment_vouchers(sale_order_id):
    if 'username' in session and request.method == "POST":
        rec_ids = request.form['rec_ids']
        for ids in rec_ids.split(','):
            check_sale_order_status = SalesOrder.query.filter_by(id=sale_order_id).first()
            if check_sale_order_status.status.value == SalesOrderStatus.received.value:
                flash("Cannot make changes to this record.", category='error')
                return redirect(url_for('voucher_list', sale_order_id=sale_order_id))
            delete = PaymentVoucher.query.filter_by(id=ids).first()
            if delete.status.value == PaymentStatus.approved.value:
                flash("Cannot make changes to Approved Voucher", category='error')
                return redirect(url_for('voucher_list', sale_order_id=sale_order_id))
            db.session.delete(delete)
            db.session.commit()
        flash("Voucher Deleted", category='success')
        return redirect(url_for('voucher_list', sale_order_id=sale_order_id))

    return render_template(Templates.login)


# search specific keyword in list of all payment vouchers
@app.route('/search-vouchers', methods=['POST', 'GET'])
def search_vouchers():
    if "username" in session:

        if request.method == 'GET':

            search = request.args['search'].lower()
            sale_orders = SalesOrder.query.filter(SalesOrder.bill.ilike(f"%{search}%")).all()
            clients = Client.query.filter(Client.client_name.ilike(f"%{search}%")).all()
            sale_order_ids = [sale_order.id for sale_order in sale_orders]
            client_ids = [client.id for client in clients]
            all_vouchers = PaymentVoucher.query.filter(PaymentVoucher.reference_no.ilike(f"%{search}%") |
                                                       PaymentVoucher.sales_order_id.in_(
                                                           sale_order_ids) | PaymentVoucher.client_id.in_(
                client_ids)).all()
            if all_vouchers:
                return render_template('list_of_all_payment_vouchers.html', all_vouchers=all_vouchers)
            flash(No_Record_Found)
            return redirect(url_for('all_vouchers_list', page=1))
        return redirect(url_for('all_vouchers_list'))
    return render_template(Templates.login)


# add/update new sales orders using a csv file
@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
    if 'username' in session and request.method == "POST":
        uploaded_file = request.files['file']
        uploaded_file.save(os.path.join(Report_Generated_File, uploaded_file.filename))
        read_file = pd.read_csv(Report_Generated_File + '\\' + uploaded_file.filename)
        sale_order = SalesOrder.query.all()
        count = 0
        while count != len(read_file):

            if 'Id' in read_file.columns:
                if count >= len(read_file):
                    break
                else:

                    for row in sale_order:
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
                            row.amount = float(read_file.loc[count, 'Amount(Rs.)']),
                            row.gst_amount = float(read_file.loc[count, 'GST(Rs.)']),
                            row.total_amount = float(read_file.loc[count, 'Total(Including GST)']),
                            row.gst = str(read_file.loc[count, 'GST(%)']),

                            row.amount_received_date = read_file.loc[count, 'Amount Received Date']
                            db.session.commit()
                            count += 1
            else:
                exists = db.session.query(db.exists().where(
                    Client.client_name == read_file.loc[count, 'Client'])).scalar()
                get_client_id = Client.query.filter_by(client_name=read_file.loc[count, 'Client']).first()
                print(get_client_id, 'test')
                print(exists)
                if not exists:
                    new_client = Client(client_name=read_file.loc[count, 'Client'], email=None, phone_no=None,
                                        address=None, credit_amount=0, overall_received=None, overall_payable=None)
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
                            get_sale_order_id = SalesOrder.query.filter_by(
                                bill=str(read_file.loc[count, 'Bill No.'])).first()
                            if get_sale_order_id:
                                flash(f"Bill no {get_sale_order_id.bill} already exists in the Database! \n"
                                      f"Duplicate Bill No. at Row No. {count + 2}.")
                                return redirect(url_for('file_upload'))

                            new_sale_order = SalesOrder(client_id=get_client_id.id,
                                                        content_advt=read_file.loc[count, 'AD/GP/Others'],
                                                        date_of_order=
                                                        read_file.loc[count, 'RO Date'],
                                                        dop=read_file.loc[count, 'DoP'],

                                                        bill=int(read_file.loc[count, 'Bill No.']),
                                                        bill_date=
                                                        read_file.loc[count, 'Bill Date'],
                                                        amount=float(read_file.loc[count, 'Amount(Rs.)']),
                                                        gst_amount=float(read_file.loc[count, 'GST(Rs.)']),
                                                        total_amount=float(
                                                            read_file.loc[count, 'Total(Including GST)']),
                                                        gst=str(read_file.loc[count, 'GST(%)']),
                                                        amount_received_date=read_file.loc[
                                                            count, 'Amount Received Date'],
                                                        total_paid=0, total_payable=float(
                                    read_file.loc[count, 'Total(Including GST)']), adjusted_credit=0
                                                        )
                            client = Client.query.filter_by(id=get_client_id.id).first()
                            client.overall_payable = client.overall_payable + new_sale_order.total_amount

                            db.session.add(new_sale_order)
                            db.session.commit()
                            count += 1
        flash(f"{count} Record added", category="success")
    return render_template(Templates.file_upload)


# ui = FlaskUI(app)
#
# if __name__ == "__main__":
#     # app.run(host='0.0.0.0')
#     ui.run()


# def start_flask(**server_kwargs):
#
#     app = server_kwargs.pop("app", None)
#     server_kwargs.pop("debug", None)
#
#     try:
#         import waitress
#
#         waitress.serve(app, **server_kwargs)
#     except:
#         app.run(**server_kwargs)


if __name__ == "__main__":
    app.run(debug=True)

    # Default start flask
    # FlaskUI(
    #     app=app,
    #     server="flask",
    #     width=800,
    #     height=600,
    # ).run()
