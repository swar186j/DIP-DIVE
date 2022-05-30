import os
from time import time
from flask_login import UserMixin
import jwt
from __init__ import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(10))
    age= db.Column(db.String(3))
    city= db.Column(db.String(20))

    def __init__(self, email: str, password: str, name: str, mobile: int, age: int, city:str):
        """Create a new User object using the email address and hashing the
        plaintext password using Werkzeug.Security.
        """
        self.email = email
        self.password = password
        self.name = name
        self.mobile= mobile
        self.age= age
        self.city= city
        

    def __repr__(self):
        return 'User {}'.format(self.name)

    def set_password(self, password, commit=False):
        self.password = generate_password_hash(password)

        if commit:
            db.session.commit()

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self, expires=500):
        return jwt.encode({'reset_password': self.name, 'exp': time() + expires},
                           key=os.getenv('SECRET_KEY','random_key'), algorithm="HS256")

    @staticmethod
    def verify_reset_token(token):
        try:
            name = jwt.decode(token, key=os.getenv('SECRET_KEY','random_key'),algorithms=["HS256"])['reset_password']
            print(name)
        except Exception as e:
            print(e)
            return
        return User.query.filter_by(name=name).first()

    @staticmethod
    def create_user(name, password, email):

        user_exists = User.query.filter_by(name=name).first()
        if user_exists:
            return False

        user = User()

        user.name = name
        user.password = user.set_password(password)
        user.email = email

        db.session.add(user)
        db.session.commit()

        return True

    @staticmethod
    def update_user(email, name, mobile, age, city):

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            return False

        user = User()

        user.name = name
        user.mobile= mobile
        user.age=age
        user.city= city
        
        user.email = email

        db.session.update(user)
        db.session.commit()

        return True

    @staticmethod
    def login_user(name, password):

        user = User.query.filter_by(name=name).first()

        if user:
            if user.verify_password(password):
                return True

        return False

    @staticmethod
    def verify_email(email):

        user = User.query.filter_by(email=email).first()

        return user























