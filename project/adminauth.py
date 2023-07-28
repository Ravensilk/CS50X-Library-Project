from flask import Blueprint, redirect, request, render_template, flash, Markup
from flask_login import login_user
from .auth import find_account, check_user
from .decorators import sanitize_string, logout_required

adminauth = Blueprint('adminauth', __name__)

@adminauth.route("/admin/login")
@logout_required
def admin_login():
    return render_template("accounts/adminlogin.html")

@adminauth.route("/admin/login", methods=["POST"])
@logout_required
def admin_login_post():

    username = sanitize_string(request.form.get("username"))
    password = request.form.get("password")

    if not username:
        flash("You did not put a username!", 'danger')
        return redirect("/admin/login")
    
    if not password:
        flash("You did not put a password!", 'danger')
        return redirect('/admin/login')
    
    user = find_account(username)

    if not user:
        flash("This username is not registered. Try again.", 'danger')
        return redirect('/admin/login')
    
    if not user.is_admin:
        login_message = Markup('This is not the proper login form for non-librarians. Click <a href="/login">here</a> to login as a non-librarian.')
        flash(login_message, 'danger')
        return redirect("/admin/login")

    verify = check_user(user, password)

    if not verify:
        flash("Wrong password! Try again.", 'danger')
        return redirect('/admin/login')
    
    if not user.is_confirmed:
        flash("You need to verify your account to be able to login. Check your email.", 'danger')
        return redirect('/admin/login')
    
    login_user(user)
    flash("Successfully logged in!", 'success')
    return redirect("/admin/dashboard")