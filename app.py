# Imports
import re
import pymysql
import uuid, os, hashlib
from flask import Flask, render_template, request, abort, redirect, url_for, session, flash, jsonify
app = Flask(__name__)

from utils import create_connection, setup
app.register_blueprint(setup)
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
# TO DO LIST
# Make Home Page [ALMOST DONE]
# Make Login / Signup Page [DONE]
# Make Dashboard Table Page
# Make [bro?]

@app.before_request
def restrict():
    restricted_pages = [
        'board',
        'view_user',
        'select'
    ]
    admin_only = [
        'board',
        'addsubject',
        'delete',
        'addsubject',
        'adminpage',
        'deletesubject'

    ]
    if 'logged_in' not in session and request.endpoint in restricted_pages:
        flash("You lack permissions to access that page.")
        return redirect('/')

# Remade version of the 403 error page
@app.errorhandler(403)
def forbidden(error):
    return render_template("forbiddenpage.html"), 403

# Remade version of the 404 error page
@app.errorhandler(404)
def missing(error):
    return render_template("missingpage.html"), 404

# Home Page
@app.route('/home')
def home():
    return render_template("homepage.html")

# Registering
@app.route('/signup', methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':

        # Encrypts password with sha256, which is 64bit
        password = request.form['password']
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()

        # Encoded File Names (Purpose of making it unique names so Python doesn't have a seizure)
        if request.files['avatar'].filename:
            avatar_image = request.files["avatar"]
            ext = os.path.splitext(avatar_image.filename)[1]
            avatar_filename = str(uuid.uuid4())[:32] + ext
            avatar_image.save("static/images/" + avatar_filename)
        else:
            avatar_filename = "deleted.png"

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql="""insert into users (name, email, dob, yearlevel, password, avatar)
                    values(%s, %s, %s, %s, %s, %s)"""
                values=(
                    request.form['name'],
                    request.form['email'],
                    request.form['dob'],
                    request.form['yearlevel'],
                    encrypted_password,
                    avatar_filename
                    )
                try:
                    cursor.execute(sql,values)
                    connection.commit()
                except pymysql.err.IntegrityError:
                    flash("Email already exists")
                    return redirect('/')
    
            return redirect('/home')
    return render_template('user_register.html')

# User Login
@app.route('/', methods=['GET','POST'])
def userlogin():
    if request.method == 'POST':

        # Makes entered password also work with encrypted password
        password = request.form['password']
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()

        # Uses SQL to check if the user exists
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "select * from users where email=%s AND password=%s"
                values = (
                    request.form['email'],
                    encrypted_password
                )
                cursor.execute(sql, values)
                result = cursor.fetchone()
        if result: # Checks sessions
            session['logged_in'] = True
            session['name'] = result['name']
            session['role'] = result['role']
            session['id'] = result['id']
            flash("Welcome, " +result["name"])
            return redirect("/home")    
        else:
            flash("Incorrect Password")
            return redirect("/")
    else:
        return render_template('user_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully logged out")
    return redirect('/')

# User Dashboard
@app.route('/dash')
def board():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT * FROM users
                        """)
            result = cursor.fetchall()
    return render_template('dash.html', result=result)

# Profile
@app.route('/view')
def view_user():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from users where id=%s", request.args['id'])
            result = cursor.fetchone()
        with connection.cursor() as cursor:
            cursor.execute("""SELECT users.name, users.email, users.id, subjects.subject_id, subjects.subject_name, subjects.subject_code
                FROM users INNER JOIN (subjects INNER JOIN connectsubjects ON subjects.subject_id = connectsubjects.subject_id) ON users.id = connectsubjects.user_id
                WHERE (((users.id)=%s));""", request.args['id'])
            subjects = cursor.fetchall()
    return render_template('user_profile.html', result=result, subjects=subjects)

# Delete User
@app.route('/delete')
def delete():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("delete from users where id=%s", request.args['id'])
            connection.commit()
    flash('Successfully deleted')
    return redirect('/home')

# Add subjects to list for students to choose from
@app.route('/add-subject', methods=['GET','POST'])
def addsubject():
    if request.method == 'POST':
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """insert into subjects (subject_name, subject_code) 
                values (%s,%s)"""
                values = (
                    request.form['subject_name'],
                    request.form['subject_code']
                )
                cursor.execute(sql,values)
                connection.commit()
        flash('Successfully added subject')
        return redirect('/home')
    else:
        return render_template("add_subject.html")

# Add Subject
@app.route('/select-subjects', methods=['GET','POST'])
def select():
    if request.method == 'POST':
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "insert into connectsubjects (user_id, subject_id) values (%s,%s)"
                values = (
                    session['id'],
                    request.form['subject_id']
                )
                cursor.execute(sql,values)
                connection.commit()
            flash('Updated Subjects')
            return redirect('/home')

    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from subjects")
            subjects = cursor.fetchall()
    return render_template('subject_select.html', subjects=subjects)

@app.route('/delete-subject', methods=['GET','POST'])
def deletesubject():
    if request.method == 'POST':
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("delete from subjects where subject_id=%s", request.form['subject_id'])
                connection.commit()
        flash('Successfully deleted subject')
        return redirect('/home')

    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from subjects")
            subjects = cursor.fetchall()
    return render_template('delete_subject.html', subjects=subjects)


@app.route('/admin')
def adminpage():
    return render_template('_admin.html')
        


if __name__ == '__main__':
    import os
    # We might use cookies for this idk
    app.secret_key = os.urandom(32)

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '3333')) # Port Number (localhost://PORTNUMBER)
    except ValueError:
        PORT = 3333
    app.run(HOST, PORT, debug=True)