from flask import Blueprint, request, render_template, redirect, flash, url_for, session, Markup
from . import db, serializer, idserializer, serializeremailsalt, serializeridsalt, mail, serializerchangepasssalt
from datetime import datetime
from .models import Users
from .decorators import logout_required, escape_string, sanitize_string
from flask_login import login_user, login_required, logout_user
from email_validator import validate_email, EmailNotValidError
from flask_mail import Message

import bcrypt

auth = Blueprint('auth', __name__)

def create_account(uname, pword, mail):

    try:
        hashed_pword = bcrypt.hashpw(pword.encode('utf-8'), bcrypt.gensalt())

        new_user = Users(username = uname, hash = hashed_pword, email = mail)

        db.session.add(new_user)
        db.session.commit()
        return True
    
    except Exception:
        db.session.rollback()
        return False
        
def find_account(uname):

    check_user = Users.query.filter(Users.username == uname).first()
    return check_user

def find_email(uemail):

    check_email = Users.query.filter(Users.email == uemail).first()
    return check_email

def check_user(user, hashp):

    if bcrypt.checkpw(hashp.encode('utf-8'), user.hash.encode('utf-8')):
        return True
    else:
        return False 

def create_token(email):
    return serializer.dumps(email, serializeremailsalt)

def verify_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt=serializeremailsalt, max_age=expiration)
        return email
    
    except Exception:
        return False 
    
def create_changepass_token(email):
    return serializer.dumps(email, serializerchangepasssalt)

def verify_changepass_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt=serializerchangepasssalt, max_age=expiration)
        return email
    
    except Exception:
        return False

def create_id(id):
    return idserializer.dumps(id, serializeridsalt)

def get_serid(token):
    try: 
        id = idserializer.loads(token, salt=serializeridsalt)
        try:
            id = int(id)
            return id
        except Exception:
            return False
    
    except Exception:
        return False
    
def send_email(email, subject, template):
    try:
        msg = Message(html = template, recipients = [email], subject = subject, sender=("Admin", "jkcfinalprojectsmtp@gmail.com"))
        mail.send(msg)
        return True
    
    except Exception:
        return False



@auth.route("/login")
@logout_required
def login():
    return render_template("accounts/login.html")

@auth.route("/login", methods=["POST"])
@logout_required
def login_post():

    username = sanitize_string(request.form.get("username"))
    password = request.form.get("password")

    if not username:
        flash("You did not put a username!", 'danger')
        return redirect('/login')
    
    if not password:
        flash("You did not put a password!", 'danger')
        return redirect('/login')
    
    user = find_account(username)

    if not user:
        flash("This username is not registered. Try again.", 'danger')
        return redirect('/login')
    
    if user.is_admin:
        login_message = Markup('This is not the proper login form for Librarians. Click <a href="/admin/login">here</a> to login as a Librarian.')
        flash(login_message, 'danger')
        return redirect('/login')

    verify = check_user(user, password)

    if not verify:
        flash("Wrong password! Try again.", 'danger')
        return redirect('/login')
    
    if not user.is_confirmed:
        flash("You need to verify your account to be able to login. Check your email.", 'danger')
        return redirect('/login')
    
    login_user(user)
    flash("Successfully logged in!", 'success')
    return redirect("/dashboard")
        
@auth.route("/register")
@logout_required
def register():
    return render_template("accounts/register.html")

@auth.route("/register", methods=["POST"])
@logout_required
def register_post():

    username = sanitize_string(request.form.get("username"))
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    email = sanitize_string(request.form.get("email"))

    if not username:
        flash("You did not provide a username!", 'danger')
        return redirect("/register")
    if not password:
        flash("You did not provide a password!", 'danger')
        return redirect("/register")
    if not confirmation:
        flash("You did not re-enter your password!", 'danger')
        return redirect("/register")
    if not email:
        flash("You did not provide an email!", 'danger')
        return redirect("/register")
    if not password == confirmation:
        flash("The passwords you entered were not the same.", 'danger')
        return redirect("/register")
    
    check = find_account(username)

    if check:
        flash("This account exists already! Choose a new username.", 'danger')
        return redirect("/register")
    
    try:
        emailinfo = validate_email(email, check_deliverability=True)
        emailinfo = emailinfo.normalized

    except EmailNotValidError as e: 
        flash(str(e), 'danger')
        return redirect("/register")
    
    email_check = find_email(emailinfo)
    if email_check:
        flash("This email has been used for another account already. Pick a new one.", 'danger')
        return redirect("/register")

    create = create_account(username, password, emailinfo)

    if create:
        newuser = Users.query.filter(Users.email == emailinfo).first()
        emailid = create_id(newuser.id)
        emailtoken = create_token(newuser.email)
        confirmlink = url_for('auth.verify', userid=emailid, token=emailtoken, _external = True)
        subject = 'Confirm your Email for Library Management App of (Schoolname)'
        html = render_template('accounts/confirm.html', confirm_link = confirmlink)
        sendmsg = send_email(newuser.email, subject, html)

        if sendmsg:
            session.clear()
            flash("Your account was successfully created. Verify your account by checking your email for the confirmation link to login.", 'success')
            return redirect("/login")
        
        else:
            flash("Your account was created but we failed to send you an activation link. Go to the IT Department to verify your account.", 'danger')
            return redirect("/login")
    
    else:
        flash("Something went wrong! Try again.", 'danger')
        return redirect("/register")

@auth.route("/verify", methods=["GET"])
def verify():
        
        userid = get_serid(request.args.get('userid'))
        useremail = verify_token(request.args.get('token'))

        if not userid:
            flash("This account does not exist. Register now!", 'danger')
            return redirect("/register")
        
        if not useremail:
            flash("This account does not exist. Register now!", 'danger')
            return redirect("/register")

        user = Users.query.get(userid)

        if user.is_confirmed:
            flash("Your account is already confirmed!", 'danger')
            return redirect("/login")

        else:

            if user.email == useremail:
                try:     
                    user.is_confirmed = True
                    user.confirmed_on = datetime.now()
                    db.session.commit()
                
                except Exception:
                    db.session.rollback()
                    flash("Something went wrong! Try again.", 'danger')
                    return redirect("/register")
                
                flash("Your account was verified successfully!", 'success')
                return redirect("/login")
            
            else:
                flash("Your confirmation link is either invalid or expired.", 'danger')
                return redirect("/login")


@auth.route("/forgottenpassword")
def request_changepass():
    return render_template("accounts/newforgottenpass.html")

@auth.route("/forgottenpassword", methods=["POST"])
def send_resetlink():

    email = request.form.get('email')

    if not email:
        flash("You did not submit an email! Try again.", 'danger')
        return redirect("/forgottenpassword")
    
    try:
        emailinfo = validate_email(email, check_deliverability=True)
        emailinfo = emailinfo.normalized

    except EmailNotValidError as e: 
        flash(str(e), 'danger')
        return redirect("/forgottenpassword")
    
    user = Users.query.filter(Users.email == emailinfo).first()

    if user is None:
        flash("There is no registered account under this email. Try again.", 'danger')
        return redirect("/forgottenpassword")
    
    else:

        if user.is_admin:
            flash("Librarian accounts' password can only changed by an administrator. Head to the ID Department.", 'danger')
            return redirect("/forgottenpassword")

        emailid = create_id(user.id)
        emailtoken = create_changepass_token(user.email)
        resetlink = url_for('auth.changepass', userid=emailid, token=emailtoken, _external = True)
        subject = 'Forgotten Password for JKCU Library'
        html = render_template('accounts/forgottenpassemail.html', reset_link = resetlink)
        sendmsg = send_email(user.email, subject, html)

        if sendmsg:
            session.clear()
            flash("Your request was processed, please check your email for the link to reset your password.", 'success')
            flash(str(resetlink), 'success')
            return redirect("/login")
        
        else:
            flash("Your request was processed but we were unable to send you an email due to a problem. Go to the IT Department to change your password instead.", 'danger')
            return redirect("/login")


@auth.route("/changepassword", methods=["GET"])
def changepass():

    if request.method == "GET":

        userid = get_serid(request.args.get('userid'))
        useremail = verify_changepass_token(request.args.get('token'))

        if not userid:
            flash("This account does not exist. Register now!", 'danger')
            return redirect("/register")
        
        if not useremail:
            flash("There is not account associated with this email address. Register now!", 'danger')
            return redirect("/register")

        user = Users.query.get(userid)

        if user is None:
            flash("This account does not exist. Register now!", 'danger')
            return redirect("/register")

        else:

            if user.is_admin:
                flash("Librarian accounts' password can only changed by an administrator. Head to the ID Department.", 'danger')
                return redirect("/login")

            if user.email == useremail:  
                newidtoken = create_id(user.id)
                newemailtoken = create_changepass_token(user.email)
                return render_template("accounts/newchangepass.html", token = newemailtoken, id = newidtoken)
            
            else:
                flash("Your confirmation link is either invalid or expired.", 'danger')
                return redirect("/login")

@auth.route("/changepassword", methods=["POST"])
def process_change_pass():

    if request.method == "POST":
        
        verifiedid = get_serid(request.form.get('idtoken'))
        verifiedemail = request.form.get('email')
        verifiedtoken = verify_changepass_token(request.form.get('changepasstoken'))
        newpassword = request.form.get('newpassword')
        newconfirmation = request.form.get('newconfirmation')

        try:
            emailinfo = validate_email(verifiedemail, check_deliverability=True)
            emailinfo = emailinfo.normalized

        except EmailNotValidError as e: 
            flash(str(e), 'danger')
            return redirect(request.referrer)
        
        if not verifiedid or not verifiedtoken or not newpassword or not newconfirmation:
            flash("You used an invalid token. If you were sent the email more than an hour ago, that means your token is expired. Request a new one.", 'danger')
            return redirect(request.referrer)
        
        user = Users.query.get(verifiedid)

        if user is None:
            flash("This account does not exist. Register now!", 'danger')
            return redirect(request.referrer)
        
        else:
            
            if user.is_admin:
                flash("Librarian accounts' password can only changed by an administrator. Head to the ID Department.", 'danger')
                return redirect(request.referrer)

            if emailinfo != verifiedtoken:
                flash("You provided a different email from the one this request was sent from. Try again.", 'danger')
                return redirect(request.referrer)
            
            if verifiedtoken != user.email:
                flash("The email linked to this account is not the same with what you entered. Try again.", 'danger')
                return redirect("/register")
            
            if newpassword != newconfirmation:
                flash("The passwords you entered were not the same. Try again!", 'danger')
                return redirect(request.referrer)
            
            elif newpassword == newconfirmation:

                try:
                    hashedpw = bcrypt.hashpw(newpassword.encode('utf-8'), bcrypt.gensalt())
                    user.hash = hashedpw
                    db.session.commit()

                    flash("Your password was successfully updated. Login below to try your new password.", 'success')
                    return redirect("/login")
                
                except Exception:
                    db.session.rollback()
                    
                    flash("There was an error during the change of your password, no changes were saved. Try again later.", 'danger')
                    return redirect("/login")
        

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
       