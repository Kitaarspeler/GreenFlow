import logging
import mysql.connector
import RPi.GPIO as GPIO
from solenoid import Solenoid
#from models import Users
from flask import Flask, render_template, request, redirect, url_for, session
from flask_classful import FlaskView, route
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "akl;wejr,q2bjk35jh2wv35tugyaiu"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://greenflowuser:fasc1st-$hoot-c4rbine-WARINESS@localhost/greenflow"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<Name %r" % self.user


# Adding user
#hashed_pw = generate_password_hash("asdf")
#user = Users(username="Jull", password_hash=hashed_pw)
#db.session.add(user)
#db.session.commit()


class Interface(FlaskView):
    @classmethod
    def _initilization(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        solenoids = {}
        for i in range(1, 5):
            solenoids[i] = Solenoid(i + 1)
            print(f"Solenoid {i} created: {solenoids[i]}")

        #DBINFO = {"host": "localhost", "user": "greenflowuser", "password": "fasc1st-$hoot-c4rbine-WARINESS", "database": "greenflow"}
        #mydb = Database(DBINFO)
        #mydb.write_password("jull", b"hiimashasheepshagger", salt)
        #print(mydb.get_password("jull"))


    def index(self):
        return render_template("index.html")

    default_methods = ['GET', 'POST']
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
        

    def schedule(self):
        return render_template("schedule.html")
    

    def settings(self):
        return render_template("settings.html")
    

    def is_authenticated(self, username, password):
        user_to_check = Users.query.filter_by(username=username).first()
        if check_password_hash(user_to_check.password_hash, password):
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