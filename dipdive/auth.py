from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_mail import Mail, Message
from flask_login import login_user, logout_user, login_required
from __init__ import db, mail


auth = Blueprint('auth', __name__) # create a Blueprint object that we name 'auth'

@auth.route('/login', methods=['GET', 'POST']) # define login page path
def login(): # define login page fucntion
    if request.method=='POST': # if the request is a GET we return the login page
        
    # if the request is POST the we check if the user exist and with te right password
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            flash('Please sign up before!')
            return redirect(url_for('auth.signup'))
        elif not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])# we define the sign up path
def signup(): # define the sign up function
    if request.method=='GET': # If the request is GET we return the sign up page and forms
        return render_template('signup.html')
    else: # if the request is POST, then we check if the email doesn't already exist and then we save data
        email = request.form.get('email')
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        age = request.form.get('age')
        city = request.form.get('city')
        
        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
        
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name,mobile=mobile,age=age, city=city, password=generate_password_hash(password, method='sha256')) 
        
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))

@auth.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
  if request.method=='GET': 
    return render_template('edit_profile.html')
  else:
    email = request.form.get('email')
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    age = request.form.get('age')
    city = request.form.get('city')
  
    User.query.filter_by(email=email).update(dict(name=name,mobile=mobile,age=age, city=city))
    print(email)
    print(name)
    db.session.commit()

     
  return render_template('edit_profile.html')


@auth.route('/logout') # define logout path
@login_required
def logout(): #define the logout function
    logout_user()
    flash('You have been Logged out!')
    return redirect(url_for('auth.login'))

@auth.route('/reset', methods=['GET','POST'])
def reset():
  if request.method == 'GET':
    return render_template('reset.html')

  if request.method == 'POST':

    email = request.form.get('email')
    user = User.verify_email(email)
    print(user)

    if user:
      send_email(user)
      flash('An email has been sent with instructions to reset your password.', 'info')

    return redirect(url_for('auth.login'))

mail = Mail()

def send_email(user):
  token = user.get_reset_token()

  msg = Message()
  msg.subject = "Login System: Password Reset Request"
  msg.sender = 'sender@gmail.com'
  msg.recipients = [user.email]
  msg.html = render_template('reset_email.html', user = user, token = token)

  mail.send(msg)


  
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_verified(token):
  user = User.verify_reset_token(token)
  print(user)
  if not user:
    flash('User not found or token has expired', 'warning')
    print('no user found')
    return redirect(url_for('auth.login'))

  password = request.form.get('password')
  if password:
    user.set_password(password, commit=True)
    flash("Password updated successfully!")
    logout_user()
    return redirect(url_for('auth.login'))

  return render_template('reset_password.html') 