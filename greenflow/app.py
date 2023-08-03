import logging
import mysql.connector
import RPi.GPIO as GPIO
from solenoid import Solenoid
#from models import Users
from flask import Flask, render_template, request, redirect, url_for, session
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

    username
        username of user
    password
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
        return "<Name %r" % self.user


class Interface(FlaskView):
    @classmethod
    def _initilization(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.solenoids = []
        for i in range(0, 4):
            self.solenoids.append(Solenoid(i, i + 2, f"Hose {i + 1}"))
            self.solenoids[i].turn_off()
            
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

    @login_required
    def index(self):
        session["_user_id"]
        return render_template("index.html", solenoids=self.solenoids)
        
    @login_required
    def water(self):
        return render_template("water.html")
    
    @login_required
    def schedule(self):
        return render_template("schedule.html", solenoids=self.solenoids)
    
    @login_required
    def settings(self):
        return render_template("settings.html")
    
    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for("Interface:login"))
    
    @login_required
    @app.route("/Interface:toggle_solenoid/<int:id>")
    def toggle_solenoid(self, id):
        self.solenoids[int(id)].toggle_state()
        return redirect(url_for("Interface:index"))
    
    def is_authenticated(self, username, password):
        user_to_check = Users.query.filter_by(username=username).first()
        if user_to_check != None:
            if check_password_hash(user_to_check.password_hash, password):
                login_user(user_to_check)
                return True
        else:
            return False
        
    def add_user_to_db(self, username, password):
        user_to_check = Users.query.filter_by(username="Jull").first()
        if user_to_check != None:
            user = Users(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()


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