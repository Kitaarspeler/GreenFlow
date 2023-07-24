"""GreenFlow RPi based garden watering system

This program allows the user to set up multiple solenoids for turning
on and off multiple hoses to water different parts of their garden.
"""


import sys
import RPi.GPIO as GPIO
from solenoid import Solenoid
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_required
import bcrypt
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = "akl;wejr,q2bjk35jh2wv35tugyaiu"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'greenflowuser'
app.config['MYSQL_PASSWORD'] = 'fasc1st-$hoot-c4rbine-WARINESS'
app.config['MYSQL_DB'] = 'greenflow'
mysql = MySQL(app)

cursor = mysql.connection.cursor()
cursor.execute("show tables")
#cursor.execute("SELECT pass FROM users WHERE username = 'jull'")
db_pass = cursor.fetchall()
print(db_pass)


"""
login_manager = LoginManager()
login_manager.init_app(app)
"""


def main():
    """Initialises GPIO pins, solenoids and schedules

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    solenoids = {}

    num_solenoids = int(get_num_solenoids())
    for i in range(1, num_solenoids+1):
        try:
            solenoids[i] = Solenoid(i + 1)
        except ValueError:
            sys.exit("Too many solenoids. Re-run program with 27 or fewer solenoids")

    print(**solenoids)

    app.run(
        debug = True,
        host = "0.0.0.0",
        port = 80,
        )


def get_num_solenoids():
    """Gets and returns the number of solenoids needed for this install
    
    Returns
    -------
    int
        The number of solenoids needed for this implementation

    Raises
    ------
    ValueError
        If there are too many solenoids for the number of GPIO pins
    """

    num_solenoids = 0
    while True:
        if num_solenoids < 1 or num_solenoids > 27:
            try:
                num_solenoids = int(input("Please enter the number of solenoids needed for this install: "))
            except ValueError:
                pass
        else:
            break
    return num_solenoids


def is_authenticated(username, password):
        encoded_pw = password.encode('utf-8')
        hashed = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
        if bcrypt.checkpw(b'asdf', hashed):
            return True
        else:
            return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        if is_authenticated(username, password):
            return redirect(url_for("index"))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")
    

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")


if __name__ == "__main__":
    main()
    GPIO.cleanup()