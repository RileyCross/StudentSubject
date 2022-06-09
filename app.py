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
# Make Home Page
# Make Login / Signup Page
# Make Dashboard Table Page
# Make 

# Home Page
@app.route('/home')
def home():
    """Renders a sample page."""
    return render_template("homepage.html")

# Registering
@app.route('/', methods=['GET', 'POST'])
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



if __name__ == '__main__':
    import os
    # We might use cookies for this idk
    app.secret_key = os.urandom(32)

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '3333'))
    except ValueError:
        PORT = 3333
    app.run(HOST, PORT, debug=True)
