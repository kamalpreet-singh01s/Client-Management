import csv
import datetime
import os
import re
from datetime import timedelta
import pandas as pd
from flask import render_template, request, url_for, flash, redirect, send_file, session, send_from_directory
from flask_migrate import Migrate
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash

from form import Form
from models import db, create_app, Customer, Records, Status, Users
from werkzeug.utils import secure_filename
import webbrowser

app = create_app()
migrate = Migrate(app, db, render_as_batch=True)

UPLOAD_FOLDER = r'W:\work\flask new\client management\Uploaded_Bills'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userpass = request.form["password"]
        confirm_userpass = request.form["confirm_password"]
        hash_pass = generate_password_hash(userpass)

        add_user = Users(username=request.form["username"], password=hash_pass)

        exists = db.session.query(db.exists().where(
            Users.username == request.form["username"])).scalar()
        if exists:
            flash("User with same username already exists", category='error')
            return render_template('register.html')
        if userpass != confirm_userpass:
            flash("Password does not match", category='error')
            return render_template('register.html')
        else:
            db.session.add(add_user)
            db.session.commit()
            flash('User Created', category='success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/users', methods=['GET', 'POST'])
def manage_users():
    if 'username' in session:
        users = Users.query.all()
        return render_template('users.html', users=users)
    return render_template('login.html')


@app.route('/delete-user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if 'username' in session:
        user_to_del = Users.query.filter_by(id=user_id).first()
        if session["username"] == user_to_del.username:
            flash('Cannot delete a user that is logged in', category='error')
            return redirect(url_for('manage_users'))
        elif user_to_del:
            db.session.delete(user_to_del)
            db.session.commit()
            flash("User Deleted", category='success')
        return redirect(url_for('manage_users'))
    return render_template('login.html')


@app.route('/update-user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if 'username' in session:
        user_to_update = Users.query.filter_by(id=user_id).first()
        if request.method == 'POST':
            user_to_update.username = request.form["username"]
            user_to_update.password = generate_password_hash(request.form["password"])

            db.session.commit()
            flash('User Updated', category='success')
            return redirect(url_for('manage_users'))
        return render_template('update_user.html', user_to_update=user_to_update)
    return render_template('login.html')


@app.route('/client-names')
def all_customer_names():
    if "username" in session:
        customers = Customer.query.order_by(desc(Customer.id))
        return render_template("client_list.html", customers=customers)
    return render_template('login.html')


@app.route("/new-client", methods=['GET', 'POST'])
def add_client():
    if "username" in session:
        if request.method == "POST":
            message = ''
            if request.form["customer_name"].isnumeric():
                message = 'Name cannot contain numbers or any special symbol'
                flash(message, category='error')

            if request.form["phone_no"].isalpha():
                message = 'Phone number cannot contain Alphabets or any special symbol'
                flash(message, category='error')

            email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.fullmatch(email_reg, request.form['email']):
                message = "Enter a Valid Email"
                flash(message, category='error')

            if request.form["final_deal"].isalpha():
                message = 'Final deal amount cannot contain Alphabets or any special symbol'
                flash(message, category='error')

            if message:
                flash('Record not added', category='error')
                return redirect('add_customer')
            else:
                gst = (18 / 100) * float(request.form['final_deal'])
                print(type(gst))
                added_customers = Customer(customer_name=request.form["customer_name"], email=request.form["email"],
                                           phone_no=request.form["phone_no"],
                                           address=request.form["address"],
                                           final_deal=float(request.form["final_deal"]) + gst, gst=gst)

                db.session.add(added_customers)
                db.session.commit()
                flash('Customer Added', category='success')
                return redirect(url_for('all_customer_names'))
        return render_template('add_client.html')
    return render_template('login.html')


@app.route('/delete-client/<int:customer_id>')
def delete_customer(customer_id):
    if "username" in session:
        customer_to_delete = Customer.query.filter_by(id=customer_id).first()

        if Records.query.filter_by(customer_id=customer_id).first():
            flash("Client in use", category='error')
            return redirect(url_for('all_customer_names'))

        else:
            db.session.delete(customer_to_delete)
            db.session.commit()
            flash('Client Deleted', category='success')
            return redirect(url_for('all_customer_names'))
    return render_template('login.html')


@app.route('/update-client/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    if "username" in session:
        customer_to_update = Customer.query.filter_by(id=customer_id).first()
        get_customer = Customer.query.filter_by(id=customer_id).first()
        old_final_deal = get_customer.final_deal
        if request.method == "POST":
            message = ''
            if request.form["customer_name"].isnumeric():
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
                return render_template('update_customer.html', customer_to_update=customer_to_update)
            else:
                customer_to_update.customer_name = request.form["customer_name"]
                customer_to_update.email = request.form["email"]
                customer_to_update.phone_no = request.form["phone_no"]
                customer_to_update.address = request.form["address"]
                if float(request.form["final_deal"]) == float(request.form["old_final_deal"]):
                    gst = get_customer.gst
                    customer_to_update.final_deal = float(request.form["old_final_deal"])
                    customer_to_update.gst = gst
                    print('if')
                else:
                    gst = float((18 / 100) * float(request.form["final_deal"]))
                    customer_to_update.final_deal = float(request.form["final_deal"]) + gst
                    customer_to_update.gst = gst
                    print('else')
                db.session.commit()
                flash('Client Updated.', category='success')
                return redirect(url_for('all_customer_names'))
        return render_template("update_customer.html", customer_to_update=customer_to_update,
                               old_final_deal=old_final_deal)
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "username" in session:
        all_records = Records.query.order_by(Records.bill.desc())
        print(all_records)
        return render_template("dashboard.html", all_records=all_records)
    return render_template('login.html')


@app.route('/add-record', methods=['GET', 'POST'])
def add_record():
    if "username" in session:
        form = Form()
        form.customer_name.choices = [(customer.id, customer.customer_name) for customer in Customer.query.all()]
        form.status_name.choices = [(status.id, status.status_name) for status in Status.query.all()]

        if request.method == "POST":
            file = request.files['file']

            filename = 'Bill No' + '-' + request.form["bill"] + '-' + request.form["date_of_order"] + '.pdf'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            record = Records(request.form["customer_name"], request.form["content_advt"], request.form["date_of_order"],
                             request.form["dop"], request.form["bill"], request.form["bill_date"],
                             status_id=request.form["status_name"],
                             filename=os.path.join(app.config['UPLOAD_FOLDER'], filename))

            db.session.add(record)
            db.session.commit()
            flash('Record Added', category='success')
            return redirect(url_for('dashboard'))
        form.status_name.default = 1
        form.process()
        return render_template("add_record.html", form=form)
    return render_template('login.html')


@app.route('/delete-record/<int:record_id>')
def delete_record(record_id):
    if "username" in session:
        record_to_delete = Records.query.filter_by(id=record_id).first()
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()
            flash(f'Record of {record_to_delete} Deleted', category='success')
            return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/record-details/<int:record_id>', methods=['GET', 'POST'])
def record_details(record_id):
    if "username" in session:
        date_now = datetime.date.today()
        time_now = datetime.datetime.now()
        last_updated = date_now.strftime("%d/%b/%Y")
        last_updated_time = time_now.strftime("%I:%M %p")
        record_to_update = Records.query.filter_by(id=record_id).first()
        customer = Customer.query.filter(Customer.id == record_to_update.customer_id).first()
        form = Form()
        form.status_name.choices = [(status.id, status.status_name) for status in Status.query.all()]
        form.customer_name.choices = [(customer.id, customer.customer_name) for customer in Customer.query.all()]

        if request.method == "POST":

            get_customer = Customer.query.filter_by(id=request.form["customer_name"]).first()
            print(get_customer)

            customer.email = request.form["email"]
            customer.phone_no = request.form["phone_no"]
            customer.final_deal = request.form["final_deal"]

            record_to_update.customer_id = request.form["customer_name"]
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
            print('test')
            flash('Record Updated', category='success')

        form.customer_name.default = record_to_update.customer_id
        form.status_name.default = record_to_update.status_id
        form.process()

        return render_template("record_details.html", record_to_update=record_to_update, form=form,
                               last_updated=last_updated, customer=customer, last_updated_time=last_updated_time)

    return render_template('login.html')


@app.route('/set-receive/<int:record_id>', methods=['GET', 'POST'])
def set_receive(record_id):
    form = Form()
    record_to_update = Records.query.filter_by(id=record_id).first()
    customer = Customer.query.filter(Customer.id == record_to_update.customer_id).first()
    print(record_to_update.id)
    date_now = datetime.date.today()
    time_now = datetime.datetime.now()
    last_updated = date_now.strftime("%d/%b/%Y")
    last_updated_time = time_now.strftime("%I:%M %p")
    record_to_update.status_id = 2
    record_to_update.amount_received_date = date_now
    db.session.commit()
    flash('Status Updated', category='success')
    # return redirect(url_for('record_details'))
    return render_template("record_details.html", record_to_update=record_to_update, form=form,
                           last_updated=last_updated, customer=customer, last_updated_time=last_updated_time)


@app.route('/set-cancel/<int:record_id>', methods=['GET', 'POST'])
def set_cancel(record_id):
    form = Form()
    record_to_update = Records.query.filter_by(id=record_id).first()
    customer = Customer.query.filter(Customer.id == record_to_update.customer_id).first()
    print(record_to_update.id)
    date_now = datetime.date.today()
    time_now = datetime.datetime.now()
    last_updated = date_now.strftime("%d/%b/%Y")
    last_updated_time = time_now.strftime("%I:%M %p")
    record_to_update.status_id = 3
    record_to_update.amount_received_date = date_now
    db.session.commit()
    flash('Status Updated', category='success')

    return render_template("record_details.html", record_to_update=record_to_update, form=form,
                           last_updated=last_updated, customer=customer, last_updated_time=last_updated_time)


@app.route('/payment-status-list')
def show_all_payment_status():
    if "username" in session:
        return render_template('pen_rec.html', all_status=Status.query.all())
    return render_template('login.html')


@app.route('/payment-status', methods=['GET', 'POST'])
def payment_status():
    if "username" in session:
        if request.method == "POST":
            add_status = Status(request.form["status_name"])
            db.session.add(add_status)
            db.session.commit()
            return redirect(url_for('show_all_payment_status'))
        return render_template("pen_rec.html")
    return render_template('login.html')


@app.route('/delete-payment-status/<int:status_id>')
def delete_payment_status(status_id):
    if "username" in session:
        status_to_delete = Status.query.filter_by(id=status_id).first()
        if status_to_delete:
            db.session.delete(status_to_delete)
            db.session.commit()
            flash('Record Deleted', category='success')
            return redirect(url_for('show_all_payment_status'))
    return render_template('login.html')


@app.route('/update-payment-status/<int:status_id>', methods=['GET', 'POST'])
def update_payment_status(status_id):
    if "username" in session:
        status_to_update = Status.query.filter_by(id=status_id).first()

        if request.method == "POST":
            status_to_update.status_name = request.form["status_name"]

            db.session.commit()
            flash('Record Updated', category='success')
            return redirect(url_for('show_all_payment_status'))
        return render_template("update_status.html", status_to_update=status_to_update)
    return render_template('login.html')


@app.route('/pending-payment-list')
def pending_payment_list():
    if "username" in session:

        records = Records.query.filter(Records.status_id == '1').all()
        total = 0
        for i in records:
            customer = Customer.query.filter_by(id=i.customer_id).first()
            total = float(customer.final_deal) + total

        pending_list = Records.query.filter(Records.status_id == '1').order_by(desc(Records.id)).all()
        return render_template('pending_list.html', pending_list=pending_list, total=total)
    return render_template('login.html')


@app.route('/paid-payment-list')
def paid_payment_list():
    if "username" in session:

        total_amount = Records.query.filter(Records.status_id == '2').all()
        total = 0
        for i in total_amount:
            customer = Customer.query.filter_by(id=i.customer_id).first()
            total = float(customer.final_deal) + total

        paid_list = Records.query.filter(Records.status_id == '2').order_by(desc(Records.id)).all()
        return render_template('paid_list.html', paid_list=paid_list, total=total)
    return render_template('login.html')


@app.route('/download/<path:filename>')
def download(filename):
    if "username" in session:
        uploads = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        webbrowser.open_new_tab(uploads)
    return render_template('login.html')


# Search records
@app.route('/search', methods=['POST'])
def search_records():
    if "username" in session:
        all_records_for_search = Records.query.all()
        if request.method == 'POST':
            search = request.form['search'].lower()
            if not search.isdigit():
                for i in all_records_for_search:
                    if search in i.customer_name.customer_name.lower():
                        rec = Records.query.filter(Records.customer_id == i.customer_id).all()
                        if rec:
                            return render_template("search_dashboard.html", rec=rec)
                        flash(f'No Record Found with Name - {search}')
                        return redirect(url_for('dashboard'))
                flash(f'No Record Found with Name - {search}')
                return redirect(url_for('dashboard'))
            else:
                rec = Records.query.filter(Records.bill == search).all()
                if rec:
                    return render_template("search_dashboard.html", rec=rec)
                flash(f'No Record Found with Bill No. - {search}')
                return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/get_checked_boxes', methods=['GET', 'POST'])
def get_checked_boxes():
    if 'username' in session and request.method == "POST":
        rec_ids = request.form['rec_ids']
        for ids in rec_ids.split(','):
            delete_rec = Records.query.filter_by(id=ids).first()
            db.session.delete(delete_rec)
            db.session.commit()
        flash("record_deleted", category='success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')



@app.route('/send_rec_id', methods=['GET', 'POST'])
def send_rec_id():
    form = Form()
    form.status_name.choices = [(status.id, status.status_name) for status in Status.query.all()]
    if 'username' in session and request.method == "POST":
        send_rec_ids = request.form["send_rec_ids"]
        for ids in send_rec_ids.split(','):
            print(ids)
            record_status_to_update = Records.query.filter_by(id=ids).first()
            if record_status_to_update.status_id == 2 or record_status_to_update.status_id == 3:
                flash("Please Uncheck Records with status Received/Cancelled", category='error')
                return redirect(url_for('dashboard', form=form))

        return render_template('update_check_status.html', stu_ids=send_rec_ids, form=form)
    return render_template('login.html')


@app.route('/update_class', methods=['GET', 'POST'])
def update_class():
    form = Form()
    form.status_name.choices = [(status.id, status.status_name) for status in Status.query.all()]
    if 'username' in session and request.method == "POST":
        status_id = request.form["status_id"]
        for ids in status_id.split(','):
            record_status_to_update = Records.query.filter_by(id=ids).first()
            print(request.form['status_name'])

            record_status_to_update.status_id = request.form["status_name"]
            db.session.commit()
        flash("record_updated", category='success')
        return redirect(url_for('dashboard', form=form))
    return render_template('login.html')

@app.route('/get_checked_boxes_for_client', methods=['GET', 'POST'])
def get_checked_boxes_for_client():
    if 'username' in session and request.method == "POST":
        record_ids = request.form['rec_ids']
        print(record_ids)
        for ids in record_ids.split(','):
            delete = Customer.query.filter_by(id=ids).first()
            if Records.query.filter_by(customer_id=delete.id).first():
                flash("Client in use", category='error')
                return redirect(url_for('all_customer_names'))
            db.session.delete(delete)
            db.session.commit()
        flash("Customer Deleted", category='success')
        return redirect(url_for('all_customer_names'))

    return render_template('login.html')




Report_Generated_File = os.path.join(os.curdir, 'Report_Generated')

app.config['Report_Generated'] = Report_Generated_File


@app.route('/csv_file_record_to_update', methods=['POST', 'GET'])
def csv_file_record_to_update():
    if 'username' in session and request.method == "POST":
        rec_ids = request.form["check_rec_ids"]

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
                    print(record.bill, type(record.bill))
                    customer = Customer.query.filter_by(id=Records.customer_id).first()
                    final = [record.id, record.customer_id, record.content_advt, record.date_of_order,
                             record.dop, record.bill,
                             record.bill_date,
                             customer.final_deal, record.amount_received_date, record.status_name.status_name]
                    write_file.writerow(final)
        else:
            file_name = 'Record.csv'
            with open(Report_Generated_File + '\\' + file_name, mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow(
                    ['Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Amount(Rs.)',
                     'Amount Received Date', 'Status',
                     'Pending(Rs.)'])
                for rec_id in rec_ids.split(','):
                    record = Records.query.filter_by(id=rec_id).first()
                    customer = Customer.query.filter_by(id=Records.customer_id).first()
                    print(customer)
                    final = [record.customer_name.customer_name, record.content_advt, record.date_of_order,
                             record.dop, record.bill,
                             record.bill_date,
                             customer.final_deal, record.amount_received_date, record.status_name.status_name]
                    write_file.writerow(final)
        return send_from_directory(Report_Generated_File, file_name, as_attachment=True)


@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
    if 'username' in session and request.method == "POST":
        uploaded_file = request.files['file']
        uploaded_file.save(os.path.join(Report_Generated_File, uploaded_file.filename))
        read_file = pd.read_csv(Report_Generated_File + '\\' + uploaded_file.filename)
        record = Records.query.all()
        count = 0
        while count != len(read_file):
            if count >= len(read_file):
                break

            for row in record:
                if read_file.loc[count, 'Status'] == 'Pending':
                    read_file.loc[count, 'Status'] = 1
                elif read_file.loc[count, 'Status'] == 'Received':
                    read_file.loc[count, 'Status'] = 2
                elif read_file.loc[count, 'Status'] == 'Cancel':
                    read_file.loc[count, 'Status'] = 3
                if row.id == int(read_file.loc[count, 'Id']):
                    row.customer_id = int(read_file.loc[count, 'Client'])
                    row.content_advt = read_file.loc[count, 'AD/GP/Others']
                    row.date_of_order = read_file.loc[count, 'RO Date']
                    row.dop = read_file.loc[count, 'DoP']
                    row.bill = int(read_file.loc[count, 'Bill No.'])
                    row.bill_date = read_file.loc[count, 'Bill Date']
                    # row.amount = float(read_file.loc[count, 'Amount(Rs.)'])
                    row.amount_received_date = read_file.loc[count, 'Amount Received Date']
                    row.status_id = read_file.loc[count, 'Status']
                    db.session.commit()
                    count += 1
            if count >= len(read_file):
                break
            else:
                print('else', count)
                if read_file.loc[count, 'Status'] == 'Pending':
                    read_file.loc[count, 'Status'] = 1
                elif read_file.loc[count, 'Status'] == 'Received':
                    read_file.loc[count, 'Status'] = 2
                elif read_file.loc[count, 'Status'] == 'Cancel':
                    read_file.loc[count, 'Status'] = 3
                new_record = Records(customer_id=read_file.loc[count, 'Client'],
                                     content_advt=read_file.loc[count, 'AD/GP/Others'],
                                     date_of_order=read_file.loc[count, 'RO Date'],
                                     dop=read_file.loc[count, 'DoP'], bill=read_file.loc[count, 'Bill No.'],
                                     bill_date=read_file.loc[count, 'Bill Date'],

                                     amount_received_date=read_file.loc[count, 'Amount Received Date'],

                                     status_id=read_file.loc[count, 'Status'])
                db.session.add(new_record)
                db.session.commit()
            count += 1

        # from tqdm.gui import tqdm_gui
        # from time import sleep
        # file_name = 'Custom_Record.csv'
        # with open(Report_Generated_File + '\\' + file_name, 'r') as csvFile:
        #     lines = [line for line in csvFile]
        #     currentRow = 1
        #
        #     for row in tqdm_gui(csv.reader(lines), total=len(lines)):
        #         print(row)
        #         currentRow += 1
        #         sleep(1)
    return render_template('file_upload.html')


@app.route('/file_upload/<action>', methods=['POST', 'GET'])
def file_upload_actions(action):
    if request.method == 'GET':
        if action == 'create':
            print("create method")
        elif action == 'update':
            print("write method")
        else:
            raise ValueError


if __name__ == "__main__":
    app.run()
