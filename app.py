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

    ]
    admin_only = [
        'board'
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
                sql="""insert into users (name, email, dob, yearlevel, password)
                    values(%s, %s, %s, %s, %s)"""
                values=(
                    request.form['name'],
                    request.form['email'],
                    request.form['dob'],
                    request.form['yearlevel'],
                    #request.form['password'],
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
            session['id'] = result['id'],
            return redirect("/home")
        else:
            flash("Incorrect Password")
            return redirect("/")
    else:
        return render_template('user_login.html')

# User Dashboard
@app.route('/dash')
def board():
    """Dash Board"""
    # Not doing this right now :)

# Profile
@app.route('/view')
def view_user():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from users where id=%s", request.args['id'])
            result = cursor.fetchone()
    return render_template('user_profile.html', result=result)

@app.route('/select-subject', methods=['GET','POST'])
def select():
    if request.method == 'POST':

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """insert into users (subject_name, subject_code, subject_leader, subject_description, subject_maxstudents) 
                values (%s,%s,%s,%s,%s)"""
                values = (
                    request.form['subject_name'],
                    request.form['subject_code'],
                    request.form['subject_leader'],
                    request.form['subject_description'],
                    request.form['subject_maxstudents']
                )
                cursor.execute(sql,values)
                connection.commit()

    return render_template('subject_select.html')


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
