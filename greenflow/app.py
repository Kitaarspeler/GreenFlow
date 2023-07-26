import bcrypt
import logging
import RPi.GPIO as GPIO
from database import Database
from solenoid import Solenoid
from models import User
from flask import Flask, render_template, request, redirect, url_for, session
from flask_classful import FlaskView, route


app = Flask(__name__)
app.secret_key = "akl;wejr,q2bjk35jh2wv35tugyaiu"


class Interface(FlaskView):
    @classmethod
    def _initilization(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        solenoids = {}

        for i in range(1, 5):
            solenoids[i] = Solenoid(i + 1)
            print(f"Solenoid {i} created: {solenoids[i]}")

        DBINFO = {"host": "localhost", "user": "greenflowuser", "password": "fasc1st-$hoot-c4rbine-WARINESS", "database": "greenflow"}
        salt = bcrypt.gensalt()
        mydb = Database(DBINFO)
        #mydb.write_password("jull", b"hiimashasheepshagger", salt)
        #print(mydb.get_password("jull"))


    #@app.route("/")
    def index(self):
        return render_template("index.html")

    default_methods = ['GET', 'POST']
    #@app.route("/login", methods=["GET", "POST"])
    def login(self):
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            if self.is_authenticated(username, password):
                return redirect(url_for("Interface:index"))
            else:
                return render_template("login.html")
        else:
            return render_template("login.html")
        

    #@app.route("/schedule")
    def schedule(self):
        return render_template("schedule.html")
    

    def is_authenticated(self, username, password):
        encoded_pw = password.encode('utf-8')
        hashed = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
        if bcrypt.checkpw(b'asdf', hashed):
            return True
        else:
            return False


Interface._initilization()
Interface.register(app, route_base='/')
logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


if __name__ == "__main__":
    app.run(
        debug = True,
        host = "0.0.0.0",
        port = 5000,
        )
    GPIO.cleanup()