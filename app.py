# Imports
from re import A
import pymysql
import uuid, os, hashlib
from flask import Flask, render_template, request, abort, redirect, url_for, session, flash, jsonify
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
# TO DO LIST
# Make Home Page
# Make Login / Signup Page
# Make Dashboard Table Page
# Make 

@app.route('/')
def home():
    """Renders a sample page."""
    return render_template("homepage.html")

if __name__ == '__main__':
    import os

    app.secret_key = os.urandom(32)

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '3333'))
    except ValueError:
        PORT = 3333
    app.run(HOST, PORT, debug=True)
