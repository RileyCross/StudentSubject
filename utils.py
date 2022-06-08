import pymysql, os, dotenv
from flask import Blueprint, render_template, request, redirect, flash

# This is like `app = Flask(__name__)` but for importing from separate files
setup = Blueprint('setup', __name__)

# Load settings from '.env'
dotenv.load_dotenv('.env')

# Store the settings in global variables
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DATABASE = os.environ.get('DB_DATABASE')

# Create the connection using the global variables
def create_connection():
  return pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_DATABASE,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
  )

# Before every request, test the database connection,
#  and redirect to '/setup' if there are any errors.
@setup.before_app_request
def test_connection():
  try:
    create_connection()
  except Exception as e:
    if request.path != '/setup':
      flash("Error! %s" % e)
      flash("Redirected from '%s'" % request.path)
      return redirect('/setup')

# Handle the '/setup' route
@setup.route('/setup', methods=['GET', 'POST'])
def setup_database():
  # If the form has been submitted, use it to setup the database connection
  if request.method == 'POST':
    # 'global' means that when we update these values
    #  in the function, they will also be updated globally
    global DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE
    DB_HOST = request.form['host']
    DB_USER = request.form['user']
    DB_PASSWORD = request.form['password']
    DB_DATABASE = request.form['db']
    # Try the connection with the new settings, and redirect again if it still fails
    try:
      create_connection()
    except Exception as e:
      flash("Error! %s" % e)
      return redirect('/setup')
    # If the connection succeeded, save the settings in the '.env' file
    dotenv.set_key('.env', 'DB_HOST', DB_HOST)
    dotenv.set_key('.env', 'DB_USER', DB_USER)
    dotenv.set_key('.env', 'DB_PASSWORD', DB_PASSWORD)
    dotenv.set_key('.env', 'DB_DATABASE', DB_DATABASE)
    # Setup complete, return to the homepage
    return redirect('/')
  else:
    # If we are connecting to the page normally (using GET),
    #  then display the form, with fields filled out if possible
    return render_template('setup.html', env={
      'host': DB_HOST,
      'user': DB_USER,
      'password': DB_PASSWORD,
      'db': DB_DATABASE,
    })
