from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


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

    Methods
    -------

    verify_password
        Checks given password against password hash from database
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
        """Checks given password against password hash from database
        
        """
        
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User: {self.username}"
