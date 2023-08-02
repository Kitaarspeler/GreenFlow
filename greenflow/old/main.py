"""GreenFlow RPi based garden watering system

This program allows the user to set up multiple solenoids for turning
on and off multiple hoses to water different parts of their garden.
"""


import sys
import bcrypt
import RPi.GPIO as GPIO
from database import Database
from solenoid import Solenoid
from models import User
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "akl;wejr,q2bjk35jh2wv35tugyaiu"


def main():
    """Initialises GPIO pins, solenoids, schedules and flask app

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    solenoids = {}

    for i in range(1, 5):
        solenoids[i] = Solenoid(i + 1)
        print(f"Solenoid {i}: {solenoids[i]}")

    DBINFO = {"host": "localhost", "user": "greenflowuser", "password": "fasc1st-$hoot-c4rbine-WARINESS", "database": "greenflow"}

    salt = bcrypt.gensalt()

    mydb = Database(DBINFO)
    mydb.write_password("jull", b"hiimashasheepshagger", salt)
    print(mydb.get_password("jull"))

    app.run(
        debug = True,
        host = "0.0.0.0",
        port = 5000,
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