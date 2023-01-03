import csv
import re
from datetime import timedelta
from io import BytesIO

from flask import render_template, request, url_for, flash, redirect, send_file, session, send_from_directory
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash

from Form import Form
from models import Customer, Records, app, db, Status, Users

import pandas as pd
import os


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
                # access_token = create_access_token(identity=username)
                # return jsonify(access_token=access_token)
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


@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'username' in session:
        users = Users.query.all()
        return render_template('users.html', users=users)
    return render_template('login.html')


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
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


@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
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


@app.route('/all_customer_names')
def all_customer_names():
    if "username" in session:
        customers = Customer.query.order_by(desc(Customer.id))
        return render_template("show_customer_name_list.html", customers=customers)
    return render_template('login.html')


@app.route("/add_customer", methods=['GET', 'POST'])
def add_customer():
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
            if re.fullmatch(email_reg, request.form['email']):
                pass
            else:
                message = "Enter a Valid Email"
                flash(message, category='error')

            if request.form["final_deal"].isalpha():
                message = 'Final deal amount cannot contain Alphabets or any special symbol'
                flash(message, category='error')

            if message:
                flash('Record not added', category='error')
                return redirect('add_customer')
            else:
                gst = int((18 / 100) * int(request.form['final_deal']))
                print(type(gst))
                added_customers = Customer(customer_name=request.form["customer_name"], email=request.form["email"],
                                           phone_no=request.form["phone_no"],
                                           address=request.form["address"],
                                           final_deal=float(request.form["final_deal"]) + gst, gst=gst)

                db.session.add(added_customers)
                db.session.commit()
                flash('Customer Added', category='success')
                return redirect(url_for('all_customer_names'))
        return redirect(url_for('all_customer_names'))
    return render_template('login.html')


@app.route('/delete_customer/<int:customer_id>')
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


@app.route('/update_customer/<int:customer_id>', methods=['GET', 'POST'])
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
        return render_template("dashboard.html", all_records=all_records)
    return render_template('login.html')


@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if "username" in session:
        form = Form()
        form.customer_name.choices = [(customer.id, customer.customer_name) for customer in Customer.query.all()]
        form.status_name.choices = [(status.id, status.status_name) for status in Status.query.all()]

        if request.method == "POST":
            file = request.files['file']
            getcustomer = Customer.query.filter_by(id=request.form["customer_name"]).first()
            final_deal = getcustomer.final_deal
            record = Records(request.form["customer_name"], request.form["content_advt"], request.form["date_of_order"],
                             request.form["dop"], request.form["bill"], request.form["bill_date"],
                             float(request.form["amount"]),
                             pending_amount=float(final_deal) - float(request.form["amount"]),
                             amount_received_date=request.form["amount_received_date"],
                             pending_amount_received_date=request.form["pending_amount_received_date"],
                             status_id=request.form["status_name"],
                             filename=file.filename, data=file.read())

            db.session.add(record)
            db.session.commit()
            flash('Record Added', category='success')
            return redirect(url_for('dashboard'))
        return render_template("add_record.html", form=form)
    return render_template('login.html')


@app.route('/delete_record/<int:record_id>')
def delete_record(record_id):
    if "username" in session:
        record_to_delete = Records.query.filter_by(id=record_id).first()
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()
            flash(f'Record of {record_to_delete} Deleted', category='success')
            return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/record_details/<int:record_id>', methods=['GET', 'POST'])
def record_details(record_id):
    if "username" in session:

        record_to_update = Records.query.filter_by(id=record_id).first()
        form = Form()
        form.status_name.choices = [(status.id, status.status_name) for status in Status.query.all()]
        form.customer_name.choices = [(customer.id, customer.customer_name) for customer in Customer.query.all()]

        if request.method == "POST":

            getcustomer = Customer.query.filter_by(id=request.form["customer_name"]).first()
            final_deal = getcustomer.final_deal

            record_to_update.customer_id = request.form["customer_name"]
            record_to_update.content_advt = request.form["content_advt"]
            record_to_update.date_of_order = request.form["date_of_order"]
            record_to_update.dop = request.form["dop"]

            record_to_update.bill = request.form["bill"]

            record_to_update.status_id = request.form["status_name"]

            record_to_update.amount_received_date = request.form["amount_received_date"]

            record_to_update.pending_amount_received_date = request.form["pending_amount_received_date"]

            # record_to_update.amount = request.form["amount"]
            # record_to_update.pending_amount = int(final_deal) - int(request.form["amount"])
            file = request.files['file']
            if request.files['file']:
                record_to_update.filename = request.files['file'].filename
                record_to_update.data = file.read()
            print(type(record_to_update.status_id))
            if record_to_update.status_id == '2':
                record_to_update.amount = float(request.form['backup'])
                record_to_update.pending_amount = float(final_deal) - float(record_to_update.amount)
            # record_to_update.amount = request.form["amount"]
            # record_to_update.pending_amount = int(final_deal) - int(request.form["amount"])
            db.session.commit()
            flash(f'Record of {record_to_update.customer_id} Updated', category='success')
            return redirect(url_for('dashboard'))
        form.customer_name.default = record_to_update.customer_id
        form.status_name.default = record_to_update.status_id
        form.process()

        return render_template("record_details.html", record_to_update=record_to_update, form=form,
                               final_deal=float(record_to_update.amount) + record_to_update.pending_amount)
    return render_template('login.html')


@app.route('/show_all_payment_status')
def show_all_payment_status():
    if "username" in session:
        return render_template('pen_rec.html', all_status=Status.query.all())
    return render_template('login.html')


@app.route('/payment_status', methods=['GET', 'POST'])
def payment_status():
    if "username" in session:
        if request.method == "POST":
            add_status = Status(request.form["status_name"])
            db.session.add(add_status)
            db.session.commit()
            return redirect(url_for('show_all_payment_status'))
        return render_template("pen_rec.html")
    return render_template('login.html')


@app.route('/delete_payment_status/<int:status_id>')
def delete_payment_status(status_id):
    if "username" in session:
        status_to_delete = Status.query.filter_by(id=status_id).first()
        if status_to_delete:
            db.session.delete(status_to_delete)
            db.session.commit()
            flash('Record Deleted', category='success')
            return redirect(url_for('show_all_payment_status'))
    return render_template('login.html')


@app.route('/update_payment_status/<int:status_id>', methods=['GET', 'POST'])
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


@app.route('/pending_payment_list')
def pending_payment_list():
    if "username" in session:

        total_amount = Records.query.filter(Records.status_id == '1').all()
        total = 0
        for i in total_amount:
            total = float(i.pending_amount) + total

        pending_list = Records.query.filter(Records.status_id == '1').order_by(desc(Records.id)).all()
        return render_template('pending_list.html', pending_list=pending_list, total=total)
    return render_template('login.html')


@app.route('/paid_payment_list')
def paid_payment_list():
    if "username" in session:

        total_amount = Records.query.filter(Records.status_id == '2').all()
        total = 0
        for i in total_amount:
            total = float(i.amount) + total

        paid_list = Records.query.filter(Records.status_id == '2').order_by(desc(Records.id)).all()
        return render_template('paid_list.html', paid_list=paid_list, total=total)
    return render_template('login.html')


@app.route('/download/<record_id>')
def download(record_id):
    if "username" in session:
        upload = Records.query.filter_by(id=record_id).first()
        print(upload.filename)
        return send_file(BytesIO(upload.data), download_name=upload.filename,
                         as_attachment=True)

    return render_template('login.html')


@app.route('/search', methods=['POST'])
def search():
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
    if 'username' in session:
        send_rec_ids = request.form["send_rec_ids"]
        if request.method == "POST":
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
            if int(request.form['status_name']) == 2:
                record_status_to_update.amount = float(record_status_to_update.amount) + float(
                    record_status_to_update.pending_amount)
                record_status_to_update.pending_amount = 0
            record_status_to_update.status_id = request.form["status_name"]
            db.session.commit()
        flash("record_updated", category='success')
        return redirect(url_for('dashboard', form=form))
    return render_template('login.html')


Report_Generated_File = r'W:\flask new\client management\Report_Generated'

app.config['Report_Generated'] = Report_Generated_File


@app.route('/generate_report', methods=['POST'])
def generate_report():
    if request.method == 'POST':
        file_name = 'report.csv'

        data = Records.query.all()
        with open(Report_Generated_File + '\\' + file_name, mode='w', newline='') as file:
            write_file = csv.writer(file)
            write_file.writerow(
                ['No', 'Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Amount(Rs.)',
                 'Amount Received Date', 'Status',
                 'Pending(Rs.)', 'PP Received', 'File Name', 'Data'])
            for i in data:
                final = [i.id, i.customer_name.customer_name, i.content_advt, i.date_of_order, i.dop, i.bill,
                         i.bill_date,
                         i.amount, i.amount_received_date, i.status_name.status_name, i.pending_amount,
                         i.pending_amount_received_date, i.filename, i.data]
                write_file.writerow(final)

        return send_from_directory(Report_Generated_File, file_name, as_attachment=True)

        # return redirect(url_for('dashboard'))


@app.route('/csv_file_record_to_update', methods=['POST', 'GET'])
def csv_file_record_to_update():
    if 'username' in session and request.method == "POST":
        rec_id = request.form["check_rec_ids"]
        file_name = 'Custom_Record.csv'
        with open(Report_Generated_File + '\\' + file_name, mode='w', newline='') as file:
            write_file = csv.writer(file)
            write_file.writerow(
                ['No', 'Client', 'AD/GP/Others', 'RO Date', 'DoP', 'Bill No.', 'Bill Date', 'Amount(Rs.)',
                 'Amount Received Date', 'Status',
                 'Pending(Rs.)', 'PP Received', 'File Name', 'Data'])
            for ids in rec_id.split(','):
                record = Records.query.filter_by(id=ids).first()
                final = [record.id, record.customer_name.customer_name, record.content_advt, record.date_of_order,
                         record.dop, record.bill,
                         record.bill_date,
                         record.amount, record.amount_received_date, record.status_name.status_name,
                         record.pending_amount,
                         record.pending_amount_received_date, record.filename, record.data]
                write_file.writerow(final)
                print(ids)
        return send_from_directory(Report_Generated_File, file_name, as_attachment=True)


@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
    if 'username' in session and request.method == "POST":
        file = request.files['file']
        file.save(os.path.join(Report_Generated_File, file.filename))
        read_file = pd.read_csv(Report_Generated_File + '\\' + file.filename)
        record = Records.query.all()
        count = 0
        while count != len(read_file):
            customer = Customer.query.filter(Customer.id).filter_by(
                customer_name=read_file.loc[count, 'Client']).first()
            for row in record:
                if count == len(read_file):
                    break
                if read_file.loc[count, 'Status'] == 'Pending':
                    read_file.loc[count, 'Status'] = 1
                elif read_file.loc[count, 'Status'] == 'Received':
                    read_file.loc[count, 'Status'] = 2
                elif read_file.loc[count, 'Status'] == 'Cancel':
                    read_file.loc[count, 'Status'] = 3

                if row.id == read_file.loc[count, 'No']:
                    if row.customer_id == customer.id:
                        print('if', count)
                        row.customer_id = customer.id
                        row.content_advt = read_file.loc[count, 'AD/GP/Others']
                        row.date_of_order = read_file.loc[count, 'RO Date']
                        row.dop = read_file.loc[count, 'DoP']
                        row.bill = int(read_file.loc[count, 'Bill No.'])
                        row.bill_date = read_file.loc[count, 'Bill Date']
                        row.amount = float(read_file.loc[count, 'Amount(Rs.)'])
                        row.amount_received_date = read_file.loc[count, 'Amount Received Date']
                        row.pending_amount = int(read_file.loc[count, 'Pending(Rs.)'])
                        row.pending_amount_received_date = read_file.loc[count, 'PP Received']
                        row.status_id = read_file.loc[count, 'Status']
                        db.session.commit()
                    count += 1
            else:
                print('else', count)
                if read_file.loc[count, 'Status'] == 'Pending':
                    read_file.loc[count, 'Status'] = 1
                elif read_file.loc[count, 'Status'] == 'Received':
                    read_file.loc[count, 'Status'] = 2
                elif read_file.loc[count, 'Status'] == 'Cancel':
                    read_file.loc[count, 'Status'] = 3
                new_record = Records(customer_id=customer.id, content_advt=read_file.loc[count, 'AD/GP/Others'],
                                     date_of_order=read_file.loc[count, 'RO Date'],
                                     dop=read_file.loc[count, 'DoP'], bill=int(read_file.loc[count, 'Bill No.']),
                                     bill_date=read_file.loc[count, 'Bill Date'],
                                     amount=float(read_file.loc[count, 'Amount(Rs.)']),
                                     amount_received_date=read_file.loc[count, 'Amount Received Date'],
                                     pending_amount=int(read_file.loc[count, 'Pending(Rs.)']),
                                     pending_amount_received_date=read_file.loc[count, 'PP Received'],
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


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
