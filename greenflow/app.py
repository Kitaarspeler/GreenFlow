#!/usr/bin/env python

import sys
import logging
import mysql.connector
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from flask_classful import FlaskView, route
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "akl;wejr,q2bjk35jh2wv35tugyaiu"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://greenflowuser:fasc1st-$hoot-c4rbine-WARINESS@localhost/greenflow"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    is_admin
        whether the user is an admin

    Methods
    -------

    verify_password
        Checks given password against password hash from database
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password, pw_to_check):
        """Checks given password against password hash from database
        
        """
        return check_password_hash(pw_to_check, password)

    def __repr__(self):
        """Returns f string giving username for identification
        
        """
        
        return f"User: {self.username}"



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
    
    def toggle_state(self):
        """Switches state attribute and sets GPIO pin output
        
        """

        self.state = not self.state
        GPIO.output(self.pin, self.state)



class Interface(FlaskView):
    """Flask web interface to interact with the garden watering system
    
    """

    @classmethod
    def _initilization(self):
        """Sets up Flask web interface

        Sets GPIO pin numbering system and solenoids
        """
        
        print("Flask Web server (re)starting")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for i in range(1, 5):       # Sets up solenoids
            solenoid = Solenoids.query.filter_by(pin=i+1).first()
            if solenoid is None:
                solenoid = Solenoids(id=i, pin=i+1, state=False, name=f"Hose {i}")
                db.session.add(solenoid)
                db.session.commit()
            solenoid = Solenoids.query.filter_by(pin=i+1).first()
            GPIO.setup(i+1, GPIO.OUT)

    default_methods = ["GET", "POST"]
    def login(self):
        """
        
        """
        
        user_to_add = Users.query.all()
        if not user_to_add:
            self.add_to_db("admin", "admin", True)
        if request.method == "POST" and "username" in request.form and "password" in request.form:
            username = request.form['username']
            password = request.form['password']
            #if self.is_authenticated(username, password):
            user = Users.query.filter_by(username=request.form["username"]).first()
            if user:
                if check_password_hash(user.password_hash, request.form["password"]):
                    login_user(user)
                    return redirect(url_for("Interface:index"))
                else:
                    flash("Username or password is incorrect!")
                    return render_template("login.html")
        else:
            return render_template("login.html")

    @login_required
    def index(self):
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
        """Toggle solenoid state and update GPIO pin
        
        """

        to_update = Solenoids.query.get_or_404(id)
        to_update.toggle_state()
        try:
            db.session.commit()
            flash(f"{to_update.name} turned {'on' if to_update.state else 'off'}")
        except:
            logging.error("Solenoid name update failed")
            flash("Name update failed")
        return redirect(url_for("Interface:index"))
    
    def is_authenticated(self, username, password):
        """Confirms if username and password are correct, and returns boolean
        
        """
        
        user_to_check = Users.query.filter_by(username=username).first()
        if user_to_check != None:
            if user_to_check.verify_password(password, user_to_check.password_hash):
                login_user(user_to_check)
                return True
        else:
            return False
        
    @login_required
    def add_user(self):
        """Collects user info and send to database

        """

        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'password_2' in request.form:
            if request.form['password'] == request.form['password_2']:
                user_to_check = Users.query.filter_by(username=request.form['username']).first()
                if user_to_check == None:
                    if self.validate(request.form['password']):
                        try: 
                            _ = request.form["is_admin"]
                            is_admin = True
                        except:
                            is_admin = False
                        self.add_to_db(request.form["username"], request.form["password"], is_admin)
                else:
                    flash("User already exists!")
        return render_template("add_user.html")
    
    def add_to_db(self, username, password, is_admin):
        """Adds new user to database

        """

        user = Users(username=username, password=password, is_admin=is_admin)
        try:
            db.session.add(user)
            db.session.commit()
            flash("User added successfully!")
        except:
            flash("User add failed")

    @login_required
    def rename(self):
        """Update solenoid names to keep easily recognisable
        
        """

        if request.method == "POST" and request.form["new_name"] != "":
            to_update = Solenoids.query.get_or_404(request.form["id"])
            to_update.name = request.form["new_name"]
            try:
                db.session.commit()
                flash("Name update successful")
            except:
                logging.error("Solenoid name update failed")
                flash("Name update failed")
        return render_template("rename.html", solenoids=Solenoids.query.all())
    
    @login_required
    def update_user(self):
        """Update username
        
        """
        
        if request.method == "POST" :
            if request.form["new_name"] != "":
                to_update = Users.query.get(session["_user_id"])
                to_update.username = request.form["new_name"]
                try:
                    db.session.commit()
                    flash("Username update successful")
                except:
                    logging.error("Username update failed")
                    flash("Username update failed")
        return render_template("update.html", user=Users.query.get(session["_user_id"]), which="user")
    
    @login_required
    def update_pass(self):
        """Updates password
        
        """
        
        if request.method == "POST":
            if request.form["new_pass"] != "" and request.form["new_pass_2"] != "":
                if request.form["new_pass"] == request.form["new_pass_2"]:
                    if self.validate(request.form["new_pass"]):
                        to_update = Users.query.filter_by(id=session["_user_id"]).first()
                        if to_update != None:
                            to_update = Users.query.get(session["_user_id"])
                            to_update.password_hash = generate_password_hash(request.form["new_pass"])
                            try:
                                db.session.commit()
                                flash("Password update successful")
                            except:
                                logging.error("Password update failed")
                                flash("Password update failed")
                    else:
                        flash("""Password is not valid!
                                Must be longer than 10 characters,
                                contain numbers, and special,
                                lower, and upper case characters.""")
                else:
                    flash("Passwords do not match!")
            else:
                flash("You must confirm your password!")
        return render_template("update.html", user=Users.query.get(session["_user_id"]), which="pass")

    def validate(self, new_pass):
        """Validates password and returns boolean
        
        """
        
        special = "!@#$%^&*?_-"
        upp, low, num, spec = False, False, False, False
        for l in new_pass:
            if l.isupper():
                upp = True
            elif l.islower():
                low = True
            elif l.isdigit():
                num = True
            elif l in special:
                spec = True
        if len(new_pass) > 10 and upp and low and num and spec:
            return True
        else:
            return False


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