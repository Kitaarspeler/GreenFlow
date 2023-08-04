import sys
import logging
import mysql.connector
import RPi.GPIO as GPIO
from solenoid import Solenoid
#from models import Users
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_classful import FlaskView, route
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "akl;wejr,q2bjk35jh2wv35tugyaiu"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://greenflowuser:fasc1st-$hoot-c4rbine-WARINESS@localhost/greenflow"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Interface:login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    """A user capable of logging in and out.

    Attributes
    ----------

    id
        identifier for each user
    username
        username of user
    password_hash
        encrypted password for the user
    """

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
        return f"<Name {self.user}"
    

class Solenoids(db.Model):
    """A solenoid capable of turning off and on, with a GPIO pin and a name
    
    Attributes
    ----------

    id
        identifier for each solenoid
    pin
        GPIO pin to interact with the solenoid
    state
        whether the solenoid is on or off (True or False)
    name
        identifier given by the user
    """

    id = db.Column(db.Integer, primary_key=True)
    pin = db.Column(db.Integer, nullable=False, unique=True)
    state = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Solenoid on pin {self.pin} is {self.state} with name {self.name}"


class Interface(FlaskView):
    """Flask web interface to interact with the garden watering system
    
    """

    @classmethod
    def _initilization(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for i in range(1, 5):       # Sets up solenoids
            solenoid = Solenoids.query.filter_by(pin=i+1).first()
            if solenoid is None:
                solenoid = Solenoids(id=i, pin=i+1, state=False, name=f"Hose {i}")
                db.session.add(solenoid)
                db.session.commit()
            solenoid = Solenoids.query.filter_by(pin=i+1).first()
            print(solenoid.id, solenoid.pin, solenoid.state, solenoid.name)

    default_methods = ['GET', 'POST']
    def login(self):
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            if self.is_authenticated(username, password):
                return redirect(url_for("Interface:index"))
            else:
                return render_template("login.html")
        else:
            return render_template("login.html")

    @login_required
    def index(self):
        #session["_user_id"]
        return render_template("index.html", solenoids=Solenoids.query.all())

    @login_required
    def water(self):
        return render_template("water.html")

    @login_required
    def schedule(self):
        return render_template("schedule.html", solenoids=Solenoids.query.all())

    @login_required
    def settings(self):
        return render_template("settings.html", solenoids=Solenoids.query.all())
    
    @login_required
    def logout(self):
        """
        
        """
        
        logout_user()
        return redirect(url_for("Interface:login"))
    
    @login_required
    @app.route("/Interface:toggle_solenoid/<int:id>")
    def toggle_solenoid(self, id):
        """
                FIX SOLENOID TOGGLE
        """
        
        self.solenoids[int(id)].toggle_state()
        return redirect(url_for("Interface:index"))
    
    def is_authenticated(self, username, password):
        """
        
        """
        
        user_to_check = Users.query.filter_by(username=username).first()
        if user_to_check != None:
            if check_password_hash(user_to_check.password_hash, password):
                login_user(user_to_check)
                return True
        else:
            return False
        
    @login_required
    def add_user_to_db(self, username, password):
        """
        
        """
        
        user_to_check = Users.query.filter_by(username="Jull").first()
        if user_to_check != None:
            user = Users(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()

    @login_required
    @app.route("/Interface:update_solenoid_names")
    def update_solenoid_names(self):
        """
        
        """
        
        if request.method == 'POST' and (request.form['1'] != "" or request.form['2'] != "" or request.form['3'] != "" or request.form['4'] != ""):
            if request.form['1'] != "":
                update_0 = Solenoids.query.get_or_404('1')
                update_0.name = request.form['1']
            if request.form['2'] != "":
                update_1 = Solenoids.query.get_or_404('2')
                update_1.name = request.form['2']
            if request.form['3'] != "":
                update_2 = Solenoids.query.get_or_404('3')
                update_2.name = request.form['3']
            if request.form['4'] != "":
                update_3 = Solenoids.query.get_or_404('4')
                update_3.name = request.form['4']
            try:
                db.session.commit()
                flash("Name update successful")
            except:
                logging.error("Solenoid update failed")
                flash("Name Update Failed")
        return redirect(url_for("Interface:settings"))


Interface._initilization()
Interface.register(app, route_base='/')
logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def main():
    try:
        app.run(
            debug = True,
            host = "0.0.0.0",
            port = 5000,
            )
    except (KeyboardInterrupt,EOFError):
        GPIO.cleanup()
        logging.info("Program ended by user")
        print("Program ended by user")
        sys.exit()


if __name__ == "__main__":
    main()
    GPIO.cleanup()