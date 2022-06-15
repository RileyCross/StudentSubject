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
# Make Home Page [PLACEHOLDER MADE]
# Make Login / Signup Page [DONE]
# Make Dashboard Table Page
# Make [bro?]

#@app.before_request
#def restrict():
    #restricted_pages = ['user_list','view_user','edit_user','delete_user']
    #admin_only = ['delete_user','edit_user','user_list']
    #if 'logged_in' not in session and request.endpoint in restricted_pages:
        #flash("You lack permissions to access that page.")
        #return redirect('/')

@app.errorhandler(403)
def forbidden():
    return render_template("forbiddenpage.html",403)

@app.errorhandler(404)
def missing():
    return render_template("missingpage.html",404)

# Home Page
@app.route('/home')
def home():
    return render_template("homepage.html")

# Registering
@app.route('/signup', methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':

        # Password Encrypter
        password = request.form['password']
        encrypted_password = hashlib.sah256(password.encode()).hexdigest()

        # Avatar encoded name here or something idk lol

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql="""insert into users (name, email, dob, yearlevel, password)
                    values=(%s, %s, %s, %s, %s, %s)"""
                values=(
                    request.form['name'],
                    request.form['email'],
                    request.form['dob'],
                    request.form['yearlevel'],
                    #request.form['password'],
                    encrypted_password
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

        password = request.form['password']
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()

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
            session['first_name'] = result['first_name']
            session['role'] = result['role']
            session['id'] = result['id']
            return redirect("/home")
        else:
            flash("Incorrect Password")
            return redirect("/")
    else:
        return render_template('user_login.html')

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
