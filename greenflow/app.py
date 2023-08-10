#!/usr/bin/env python

import sys
import logging
import mysql.connector
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed, UserNeed, identity_loaded, Identity, AnonymousIdentity, identity_changed
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "akl;wejr,q2bjk35jh2wv35tugyaiu"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://greenflowuser:fasc1st-$hoot-c4rbine-WARINESS@localhost/greenflow"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Users and Solenoids databases
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Admin access
principals = Principal(app)
admin_permission = Permission(RoleNeed("admin"))

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    if hasattr(current_user, "is_admin"):
        if current_user.is_admin:
            identity.provides.add(RoleNeed("admin"))

@app.errorhandler(403)
def page_forbidden(e):
    """Redirects to index and gives error when page not accessible by current user
    
    """
    
    session['redirected_from'] = request.url
    flash("You do not have permission to view that page!")
    return redirect(url_for('index'))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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

    def verify_password(self, password):
        """Checks given password against password hash from database
        
        """
        return check_password_hash(self.password_hash, password)

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



@app.route("/")
@login_required
def index():
    return render_template("index.html", solenoids=Solenoids.query.all())

@app.route("/water")
@login_required
def water():
    return render_template("water.html")

@app.route("/schedule/")
@login_required
def schedule():
    return render_template("schedule.html", solenoids=Solenoids.query.all())

@app.route("/settings/")
@login_required
def settings():
    return render_template("settings.html", solenoids=Solenoids.query.all(), user=current_user)

@app.route("/login/", methods=["GET", "POST"])
def login():
    """Performs checks and logs user in
    
    Also adds admin/admin user if no users found in database
    """
    
    user_to_add = Users.query.all()
    if not user_to_add:
        add_to_db("admin", "admin", True)
    if not current_user.is_authenticated:
        if request.method == "POST" and "username" in request.form and "password" in request.form:
            user = Users.query.filter_by(username=request.form["username"]).first()
            if user and is_authenticated(user, request.form["password"]):
                login_user(user)
                identity_changed.send(app, identity=Identity(user.id))
                return redirect(url_for("index"))
            else:
                flash("Username or password is incorrect!")
                return render_template("login.html")
        return render_template("login.html")
    else:
        return redirect(url_for("index"))

@app.route("/logout/")
@login_required
def logout():
    """Logs out user, and removes authentication
    
    """
    if current_user.is_authenticated:
        logout_user()
        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)
        identity_changed.send(app, identity=AnonymousIdentity())
    return redirect(url_for("login"))

@app.route("/toggle_solenoid/<int:id>")
@login_required
def toggle_solenoid(id):
    """Toggle solenoid state and update GPIO pin
    
    """

    to_update = Solenoids.query.get_or_404(id)
    to_update.toggle_state()
    try:
        db.session.commit()
        flash(f"{to_update.name} turned {'on' if to_update.state else 'off'}")
    except:
        logging.error("Solenoid toggle failed")
        flash(f"Hose failed to turn {'on' if to_update.state else 'off'}")
        to_update.toggle_state()        # Is this necessary?
    return redirect(url_for("index"))

@app.route("/add_user/", methods=["GET", "POST"])
@login_required
@admin_permission.require(http_exception=403)
def add_user():
    """Collects user info and send to database

    """

    if request.method == "POST" and "username" in request.form and "password" in request.form and "password_2" in request.form:
        if request.form["password"] == request.form["password_2"]:
            user_to_check = Users.query.filter_by(username=request.form["username"]).first()
            if user_to_check == None:
                if validate(request.form["password"]):
                    try: 
                        _ = request.form["is_admin"]
                        is_admin = True
                    except:
                        is_admin = False
                    add_to_db(request.form["username"], request.form["password"], is_admin)
            else:
                flash("User already exists!")
    return render_template("add_user.html")

@app.route("/del_user/", methods=["GET", "POST"])
@login_required
@admin_permission.require(http_exception=403)
def del_user():
    """Collects user info and deletes from database

    """

    if request.method == "POST" and "username" in request.form:
        to_delete = Users.query.get(request.form["username"])
        try:
            db.session.delete(to_delete)
            db.session.commit()
            flash("User deleted successfully")
        except:
            flash("User delete failed")
    return render_template("del_user.html", users=Users.query.all())

@app.route("/rename/", methods=["GET", "POST"])
@login_required
def rename():
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

@app.route("/update_user/", methods=["GET", "POST"])
@login_required
def update_user():
    """Update username
    
    """
    
    if request.method == "POST":
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

@app.route("/update_pass/", methods=["GET", "POST"])
@login_required
def update_pass():
    """Updates password
    
    """
    
    if request.method == "POST":
        if request.form["new_pass"] != "" and request.form["new_pass_2"] != "":
            if request.form["new_pass"] == request.form["new_pass_2"]:
                if validate(request.form["new_pass"]):
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

def is_authenticated(user, password):
    """Confirms if username and password are correct, and returns boolean
    
    """
    
    if user.verify_password(password):
        return True
    else:
        return False

def add_to_db(username, password, is_admin):
    """Adds new user to database

    """

    user = Users(username=username, password=password, is_admin=is_admin)
    try:
        db.session.add(user)
        db.session.commit()
        flash("User added successfully!")
    except:
        flash("User add failed")

def validate(new_pass):
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

'''
Interface._initilization()
Interface.register(app, route_base="/")
'''
logging.basicConfig(level=logging.DEBUG, filename="app.log", format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")


def main():
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