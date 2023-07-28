from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for, current_app
from re import escape
from werkzeug.utils import secure_filename
from io import StringIO
import os
import pandas as pd


def logout_required(func):
    @wraps(func)
    def check_logout(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already logged in!", 'danger')
            return redirect("/dashboard")
        return func(*args, **kwargs)
    return check_logout

def admin_required(func):
    @wraps(func)
    def check_admin(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access not allowed! You are not a Librarian!", 'danger')
            return redirect("/dashboard")
        return func(*args, **kwargs)
    return check_admin

def not_admin_required(func):
    @wraps(func)
    def check_admin(*args, **kwargs):
        if current_user.is_admin:
            flash("Access not allowed! This page is only for users who are not librarians!", 'danger')
            return redirect("/admin/dashboard")
        return func(*args, **kwargs)
    return check_admin

def sanitize_string(string):
    sanitized_string = str(string).strip()
    sanitized_string = sanitized_string.lower()
    return sanitized_string


def escape_string(string):
    escape_table = str.maketrans({"]":  r"\]", "\\": r"\\", "%":  r"\%", "_":  r"\_", "[":  r"\[", "{":  r"\{", "}":  r"\}", "`":  r"\`", ":":  r"\:", "=":  r"\=", "<":  r"\<", ">":  r"\>", "+":  r"\+", "'":  r"\'", "!":  r"\!", '"': r'\"', "#":  r"\#", "$":  r"\$", "&":  r"\&", "(":  r"\(", ")":  r"\)", "*":  r"\*", ",":  r"\,", "-":  r"\-", ".":  r"\.", "/":  r"\/", ";":  r"\;", "?":  r"\?", "@":  r"\@", "^":  r"\^", "|":  r"\|", "~":  r"\~"})
    escaped_text = escape(string)
    escaped_text = escaped_text.translate(escape_table)
    return escaped_text

def escape_search(string):
    escape_table = str.maketrans({"]":  r"\]", "\\": r"\\", "%":  r"\%", "_":  r"\_", "[":  r"\[", "{":  r"\{", "}":  r"\}", "`":  r"\`", ":":  r"\:", "=":  r"\=", "<":  r"\<", ">":  r"\>", "+":  r"\+", "'":  r"\'", "!":  r"\!", '"': r'\"', "#":  r"\#", "$":  r"\$", "&":  r"\&", "(":  r"\(", ")":  r"\)", "*":  r"\*", ",":  r"\,", "-":  r"\-", ".":  r"\.", "/":  r"\/", ";":  r"\;", "?":  r"\?", "@":  r"\@", "^":  r"\^", "|":  r"\|", "~":  r"\~"})
    escaped_text = string.translate(escape_table)
    return escaped_text

def check_integer(input):
    try:
        sanitized_integer = int(input)
        if sanitized_integer > 0:
            return sanitized_integer
        else:
            return None
    except ValueError:
        return None

def allowed_file(file):
    ALLOWED_EXTENSIONS = 'csv'
    if '.' not in file.filename:
        return False, "Wrong filename format."
    else:
        filename = file.filename
        file_extension = filename.rsplit('.', 1)[1].lower()
        if file_extension in ALLOWED_EXTENSIONS:
            return True, None
        else:
            return False, "Filename not accepted."
        
def validate_csv(file):
    try:
        filename = secure_filename(file.filename)
        df = pd.read_csv(file)
        df.columns = df.columns.str.lower()
        df.astype(str)

        columns = df.columns
        req_columns = ['author', 'title', 'isbn', 'genre', 'publisher', 'year']
        for column in req_columns:
            if column not in columns:
                return False, "Invalid CSV format. Make sure you have the title, author, isbn, genre, publisher and year headers."
        
        filename = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        df.to_csv(filename, index=False)
        return True, filename
    
    except Exception:
        return False, "Error uploading your CSV file."
    
        
