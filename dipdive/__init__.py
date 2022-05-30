from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__) # creates the Flask instance, __name__ is the name of the current Python module
    
    db_name='signup.db'
    
    app.config['SECRET_KEY'] = '1234' # it is used by Flask and extensions to keep data safe
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ db_name #it is the path where the SQLite database file will be saved
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # deactivate Flask-SQLAlchemy track modifications
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
    app.config['MAIL_PASSWORD'] = "your_password"
    app.config["CACHE_TYPE"] = "null"
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config["SESSION_PERMANENT"] = False
        
    
    db.init_app(app) # Initialiaze sqlite database
       #db=SQLAlchemy(app)
    # The login manager contains the code that lets your application and Flask-Login work together
    #login_manager = LoginManager() # Create a Login Manager instance
    login_manager.login_view = 'auth.login' # define the redirection path when login required and we attempt to access without being logged in
    login_manager.init_app(app) # configure it for login
    jwt.init_app(app)
    mail.init_app(app)
    
    from models import User

    @login_manager.user_loader
    def load_user(user_id): #reload user object from the user ID stored in the session
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    # blueprint for auth routes in our app
    # blueprint allow you to orgnize your flask app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
