from flask import Blueprint, render_template, request, redirect, flash, Markup, session
from .models import Books, ForApproval, Users, History, LostBooks, Requests
from .decorators import allowed_file, validate_csv, check_integer, escape_search, sanitize_string, admin_required
from flask_login import current_user, login_required
from . import db
from .details import add_books
from datetime import datetime, date
from sqlalchemy.sql.expression import desc

adminmain = Blueprint('adminmain', __name__)

@adminmain.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True

@adminmain.route("/admin/dashboard")
@login_required
def dashboard():
    route = 'dashboard'
    last_login = current_user.last_login_date
    date_today = date.today()
    
    if not last_login is None:

        if date_today > last_login: 
            try:
                current_user.last_login_date = date_today
                current_user.cart_requests = 0
                current_user.favorite_requests = 0
                db.session.commit()
            
            except Exception:
                db.session.rollback()
                date_error_msg = "There was an error logging your your login date."
                flash(date_error_msg, 'danger')
                return render_template("admin/dashboard.html", uname = current_user.username, route = route)
        
    else:
        current_user.last_login_date = date.today()
        db.session.commit()

    books_borrowed = len(Books.query.filter(Books.borrowed_by != "").all())
    books_approval = len(ForApproval.query.all())
    books_lost = len(LostBooks.query.all())

    return render_template("admin/dashboard.html", uname = current_user.username, route = route, borrowed = str(books_borrowed), approval = str(books_approval), lost = str(books_lost)) 

@adminmain.route("/admin/upload")
@login_required
@admin_required
def upload():
    route = 'upload'
    return render_template("admin/newupload.html", uname = current_user.username, route = route)

@adminmain.route("/admin/upload", methods=["POST"])
@login_required
@admin_required
def upload_post():
    if 'csvfile' not in request.files:
        flash("Something went wrong during file upload. Try again", 'danger')
        return redirect("/admin/upload")
    
    file = request.files['csvfile']
    if file.filename == "":
        flash("You did not upload anything! Try again", 'danger')
        return redirect("/admin/upload")

    if not file:
        flash("Something went wrong during file upload. Try again", 'danger')
        return redirect("/admin/upload")
    
    check_status, check_error = allowed_file(file)
    if not check_status:
        check_status_msg = Markup(f"There was an error with your upload. <br> <strong>Error</strong>: {check_error}")
        flash(check_status_msg, 'danger')
        return redirect("/admin/upload")

    validate_status, validate_details = validate_csv(file)
    if not validate_status:
        validate_status_msg = Markup(f"There was an error with your upload. <br> <strong>Error</strong>: {validate_details}")
        flash(validate_status_msg, 'danger')
        return redirect("/admin/upload")
    
    else:
        current_books = Books.query.with_entities(Books.isbn).filter(Books.isbn != "").all()
        books_isbn = []
        for book in current_books:
            books_isbn.append(book[0])

        addbook_status, addbook_details = add_books(validate_details, books_isbn)
        
        if not addbook_status:
            addbook_status_msg = Markup(f"There was an error with your upload. <br> <strong>Error</strong>: {addbook_details}")
            flash(addbook_status_msg, 'danger')
            return redirect("/admin/upload")
        else:
            flash(addbook_details, 'success')
            return redirect("/admin/upload")
    
@adminmain.route("/admin/bookapproval")
@login_required
@admin_required
def book_approval():
    route = "approval"
    requests = ForApproval.query.all()

    books = [book for book in requests]
    booklist = []
    for book in books:
        data = Books.query.get(book.book_id)
        booklist.append({'id': data.id, 'isbn': data.isbn, 'title': data.title, 'author': data.author, 'borrower': book.borrower, 'request_id': book.id, 'date_requested': book.requested_on})

    return render_template("admin/newbookapproval.html", uname = current_user.username, route = route, booklist = booklist)

@adminmain.route("/admin/bookapproval", methods=["POST"])
@login_required
@admin_required
def book_approval_post():
    route = "approval"
    requestid = request.form.get("requestid")
    safe_id = check_integer(requestid)

    if safe_id is None:
        flash("Invalid request ID submitted. Try again", 'danger')
        return redirect("/admin/bookapproval")
    
    else:
        bookrequest = ForApproval.query.get(safe_id)
        book = Books.query.get(bookrequest.book_id)
        book_title = book.title
        borrower = Users.query.filter(Users.username == bookrequest.borrower).first()
        borrowed_books = borrower.books

        if len(borrowed_books) >= 10:
            flash(f"Student with ID {bookrequest.borrower} still has 10 books in possession. Please deny this request.", 'danger')
            return redirect("/admin/bookapproval")

        if not book.borrowed_by:
            book_borrower = bookrequest.borrower
            new_history = History(book_id = bookrequest.book_id, borrower = bookrequest.borrower, transaction = "Approved")
            book.borrowed_by = bookrequest.borrower
            book.borrowed_on = datetime.now()
            book.last_borrowed_by = bookrequest.borrower
            flash(f"Student with ID {book_borrower}'s request to borrow {book_title} was approved. Remind the student that he / she should return the book by the end of the school year or he / she will pay penalty.", 'success')
            db.session.add(new_history)
            db.session.delete(bookrequest)

            deny_request = ForApproval.query.filter(ForApproval.book_id == bookrequest.book_id).filter(ForApproval.borrower != bookrequest.borrower).all()
            if len(deny_request) > 0:
                for deniedrequest in deny_request:
                    flash(f"Request from student with ID {deniedrequest.borrower} to borrow the book {book_title} was denied since student with ID {book_borrower}'s request was approved.", 'danger')
                    deny_history = History(book_id = deniedrequest.book_id, borrower = deniedrequest.borrower, transaction="Denied")
                    db.session.add(deny_history)
                    db.session.delete(deniedrequest)

            try: 
                db.session.commit()
                return redirect("/admin/bookapproval")

            except Exception:
                db.session.rollback()
                flash("Something went wrong during the approval process, try again later!", 'danger')
                return redirect("/admin/bookapproval")
        
        else:
            flash("This book is already borrowed by someone else. Please deny.", 'danger')
            return redirect("/admin/bookapproval")


@adminmain.route("/admin/bookdenial", methods=["POST"])
@login_required
@admin_required
def book_denial_post():
    route = "denial"
    requestid = request.form.get("requestid")
    safe_id = check_integer(requestid)

    if safe_id is None:
        flash("Invalid request ID submitted. Try again", 'danger')
        return redirect("/admin/bookapproval")
    
    else:
        bookrequest = ForApproval.query.get(safe_id)
        book = Books.query.get(bookrequest.book_id)
        book_title = book.title
        book_borrower = bookrequest.borrower
        new_history = History(book_id = bookrequest.book_id, borrower = bookrequest.borrower, transaction = "Denied")

        try: 
            db.session.add(new_history)
            db.session.delete(bookrequest)
            db.session.commit()
            flash(f"Student with ID {book_borrower}'s request to borrow {book_title} was denied.", 'danger')
            return redirect("/admin/bookapproval")

        except Exception as e:
            db.session.rollback()
            flash("Something went wrong during the approval process, try again later!", 'danger')
            return redirect("/admin/bookapproval")
        

@adminmain.route("/admin/booklist", methods=["GET", "POST"])
@login_required
@admin_required
def booklist():
    route = 'booklist'
    if request.method == "POST":
        operation = request.form.get('operation')
        if operation == 'viewall':
            books = Books.query.all()
            return render_template("admin/booklist.html", uname = current_user.username, route = route, data = books)
        elif operation == 'search':
            bookname = escape_search(sanitize_string(request.form.get("bookname")))
            bookauthor = escape_search(sanitize_string(request.form.get("bookauthor")))
            bookgenre = escape_search(sanitize_string(request.form.get("bookgenre")))
            bookpublisher = escape_search(sanitize_string(request.form.get("bookpublisher")))
            bookyear = request.form.get("bookyear")
            studentid = request.form.get("studentid")

            if not bookname and not bookauthor and not bookgenre and not bookpublisher and not bookyear and not studentid:
                flash("Please fill-out the form with any detail you know about the book or article you are searching for.", 'danger')
                return redirect("/admin/booklist")
            # Bookyear Block
            else: 
                query = Books.query

                if bookname:
                    query = query.filter(Books.title.ilike(f"%{bookname}%"))

                if bookauthor:
                    query = query.filter(Books.author.ilike(f"%{bookauthor}%"))

                if bookgenre:
                    query = query.filter(Books.genre.ilike(f"%{bookgenre}%"))

                if bookpublisher:
                    query = query.filter(Books.publisher.ilike(f"%{bookpublisher}%"))

                if bookyear:
                
                    nextyear = date.today().year + 1

                    try:
                        bookyear = check_integer(bookyear)
                        nextyear = check_integer(nextyear)

                        if nextyear is None:
                            flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
                            return redirect("/admin/booklist") 
                        
                        if bookyear is None:
                            flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
                            return redirect("/admin/booklist") 
                        
                        if bookyear <= nextyear:
                            query = query.filter(Books.year == bookyear)
                        else:
                            flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
                            return redirect("/admin/booklist") 

                    except:
                        flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
                        return redirect("/admin/booklist") 

                if studentid:

                    try:
                        studentid = check_integer(studentid)

                        if studentid is None:
                            flash("Invalid student ID provided. Try again.", 'danger')
                            return redirect("/admin/booklist")
                        
                        findstudent = Users.query.filter(Users.username == studentid).first()

                        if not findstudent:
                            flash("Cannot find the student ID you provided in the database.", 'danger')
                            return redirect("/admin/booklist")
                        
                        query = query.filter(Books.borrowed_by == studentid)

                    except:
                        flash("Something went wrong, please try again later!", 'danger')
                        return redirect("/admin/booklist")
                    
                books = query.distinct().order_by(Books.title).order_by(Books.year).all()

                if books:
                    return render_template("admin/booklist.html", data = books, uname = current_user.username)
                
                else:
                    flash("The database did not return any book using the filters that you gave.", 'danger')
                    return redirect("/admin/booklist")
            
        else:
            return "Invalid Operation"
    else:
        return render_template("/admin/newbooksearch.html", uname = current_user.username, route = route)
    
@adminmain.route("/admin/returnbook", methods=["GET", "POST"])
@login_required
@admin_required
def book_return():
    route = 'return'
    if request.method == "POST":
        operation = escape_search(sanitize_string(request.form.get("operation")))

        if operation == "search":
            bookname = escape_search(sanitize_string(request.form.get('bookname')))
            studentid = sanitize_string(request.form.get('studentid'))
            bookisbn = sanitize_string(request.form.get('bookisbn'))

            if not bookname and not studentid and not bookisbn:
                flash("Please fill-out the form with any detail you know about the book or the student's ID.", 'danger')
                return redirect("/admin/returnbook")
            
            else:
                query = Books.query

                if bookname:
                    query = query.filter(Books.title.ilike(f"%{bookname}%"))

                if studentid:

                    try:
                        studentid = check_integer(studentid)

                        if studentid is None:
                            flash("Invalid student ID provided. Try again.", 'danger')
                            return redirect("/admin/returnbook")
                        
                        findstudent = Users.query.filter(Users.username == studentid).first()

                        if not findstudent:
                            flash("Cannot find the student ID you provided in the database.", 'danger')
                            return redirect("/admin/returnbook")
                        
                        query = query.filter(Books.borrowed_by == studentid)

                    except:
                        flash("Something went wrong, please try again later!", 'danger')
                        return redirect("/admin/returnbook")
                    
                if bookisbn:

                    try:
                        bookisbn = check_integer(bookisbn)

                        if bookisbn is None:
                            flash("Invalid ISBN code provided. Try again.", 'danger')
                            return redirect("/admin/returnbook")
                        
                        query = query.filter(Books.isbn == bookisbn)

                    except:
                        flash("Something went wrong, please try again later!", 'danger')
                        return redirect("/admin/returnbook")
                
                books = query.filter(Books.borrowed_by != "").distinct().order_by(Books.title).order_by(Books.year).all()

                if books:
                    return render_template("admin/returnresult.html", data = books, uname = current_user.username)
                    
                else:
                    flash("The database did not return any book using the filters that you gave.", 'danger')
                    return redirect("/admin/returnbook")
                
        elif operation == "return":

            bookid = sanitize_string(request.form.get('bookid'))

            if bookid:

                    try:
                        bookid = check_integer(bookid)

                        if bookid is None:
                            flash("Invalid book ID provided. Try again.", 'danger')
                            return redirect("/admin/returnbook")
                        
                        returnbook = Books.query.filter(Books.id == bookid).first()

                        if not returnbook:
                            flash("Cannot find the book you provided in the database.", 'danger')
                            return redirect("/admin/returnbook")
                        
                        else:
                            last_borrower = returnbook.borrowed_by
                            returnbook.borrowed_by = None
                            returnbook.last_borrowed_by = last_borrower
                            returnbook.borrowed_on = None
                            returnbook.last_return_on = datetime.now()
                            new_history = History(book_id = returnbook.id, borrower = last_borrower, transaction = "Returned")
                            
                            db.session.add(new_history)
                            db.session.commit()  

                            flash(f"The book {returnbook.title} has been successfully returned by student ID number {last_borrower} and has been reflected on the database.", 'success')
                            return redirect("/admin/returnbook")
                        
                    except:
                        flash("Something went wrong, please try again later!", 'danger')
                        return redirect("/admin/returnbook")
            
            elif bookid is None:
                flash("Invalid book ID provided. Try again.", 'danger')
                return redirect("/admin/returnbook")
            
        elif operation == "lost":

            bookid = sanitize_string(request.form.get('bookid'))

            if bookid:

                    try:
                        bookid = check_integer(bookid)

                        if bookid is None:
                            flash("Invalid book ID provided. Try again.", 'danger')
                            return redirect("/admin/returnbook")
                        
                        lostbook = Books.query.filter(Books.id == bookid).first()

                        if not lostbook:
                            flash("Cannot find the book you provided in the database.", 'danger')
                            return redirect("/admin/returnbook")
                        
                        else:
                            last_borrower = lostbook.borrowed_by
                            lostbook.last_borrowed_by = last_borrower
                            new_history = History(book_id = lostbook.id, borrower = last_borrower, transaction = "Lost")
                            new_lost = LostBooks(book_id = lostbook.id, lost_by = last_borrower, borrowed_on = lostbook.borrowed_on)
                            db.session.add(new_lost)
                            db.session.add(new_history)
                            db.session.commit()  

                            flash(f"The book {lostbook.title} has been updated to be lost by student ID number {last_borrower} and has been reflected on the database.", 'warning')
                            return redirect("/admin/returnbook")
                        
                    except:
                        flash("Something went wrong, please try again later!", 'danger')
                        return redirect("/admin/returnbook")
            
            elif bookid is None:
                flash("Invalid book ID provided. Try again.", 'danger')
                return redirect("/admin/returnbook")

    else:
        return render_template("admin/newreturnsearch.html", uname = current_user.username, route = route)
    
@adminmain.route("/admin/lostbooks", methods=["GET", "POST"])
@login_required
@admin_required
def lostbooks():
    route = 'lostbooks'
    search = False
    bookdetails = []

    if request.method == "POST":
        operation = sanitize_string(escape_search(request.form.get("operation")))
        if operation == 'all':
            lostbooks = LostBooks.query.order_by(desc(LostBooks.borrowed_on)).all()
            search = True
    else:
        lostbooks = LostBooks.query.order_by(desc(LostBooks.borrowed_on)).limit(500).all()
        
    if lostbooks:
        for book in lostbooks:
            bookdata = book.books
            bookdetails.append({'title': bookdata.title, 'isbn': bookdata.isbn, 'author': bookdata.author, 'lost_by': book.lost_by, 'borrowed_on': book.borrowed_on})

    return render_template("admin/lostbooks.html", uname = current_user.username, route = route, lostbooks = bookdetails, search = search)
                                                    
@adminmain.route("/admin/requests")
@login_required
@admin_required
def requests():
    route = 'requests'
    requests = Requests.query.filter(Requests.status == "Pending").all()

    return render_template("admin/requests.html", uname = current_user.username, requests = requests, route = route)

@adminmain.route("/admin/requests", methods=["POST"])
@login_required
@admin_required
def request_feedback():
    route = 'requests'
    requestid = request.form.get("requestid")
    operation = escape_search(sanitize_string(request.form.get("operation")))

    if not requestid or not operation:
        flash("Invalid request, try again.", 'danger')
        return redirect("/admin/requests")
    
    checkid = check_integer(requestid)

    if checkid is None:
        flash("The ID passed with the request is invalid.", 'danger')
        return redirect("/admin/requests")
    
    findrequest = Requests.query.get(checkid)

    if findrequest is None:
        flash("The ID passed with the request is invalid.", 'danger')
        return redirect("/admin/requests")
    
    return render_template("admin/feedbackrequest.html", uname = current_user.username, route = route, operation = operation, requestobject = findrequest)
    
@adminmain.route("/admin/processrequest", methods=["POST"])
@login_required
@admin_required
def process_request():
    requestid = request.form.get("requestid")
    operation = escape_search(sanitize_string(request.form.get("operation")))
    feedback = escape_search(request.form.get("feedback"))

    if not requestid or not operation or not feedback:
        flash("Your process failed because you failed to enter a feedback.", 'danger')
        return redirect("/admin/requests")
    
    if operation == "approve":
        request_status = "Approved"

    elif operation == "deny":
        request_status = "Denied"

    else:
        flash("Invalid operation, please try again.", 'danger')
        return redirect("/admin/requests")
    
    checkid = check_integer(requestid)

    if checkid is None:
        flash("The ID passed with the request is invalid.", 'danger')
        return redirect("/admin/requests")
    
    updaterequest = Requests.query.get(checkid)

    updaterequest.status = request_status
    updaterequest.feedback = feedback
    updaterequest.updated_on = datetime.now()

    try:
        db.session.commit()
        flash("The request was successfully processed.", 'success')
        return redirect("/admin/requests")
    
    except:
        db.session.rollback()
        flash("There was an error during the update of the request, try again later.",' danger')
        return redirect("/admin/requests")

@adminmain.route("/admin/decidedrequests")
@login_required
@admin_required
def decided_requests():
    route = 'processedrequests'
    requests = Requests.query.filter(Requests.status != "Pending").order_by(desc(Requests.updated_on)).limit(100).all()

    return render_template("admin/processedrequests.html", requests = requests, uname = current_user.username, route = route)






    
