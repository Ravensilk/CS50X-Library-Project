from flask import Blueprint, request, render_template, redirect, flash, jsonify, make_response, Markup, session
from . import db
from .models import Books, Cart, ForApproval, History, Users, Favorites, Requests
from .details import add_books
from flask_login import login_required, current_user, login_fresh, logout_user
from .decorators import sanitize_string, escape_string, escape_search, check_integer, not_admin_required
from datetime import date, datetime
from operator import itemgetter
from flask_wtf.csrf import validate_csrf, CSRFProtect, ValidationError
from . import csrf
from sqlalchemy.sql.expression import desc
import bcrypt

main = Blueprint('main', __name__)

def search_book(book_id):
    book = Books.query.get(book_id)
    if book:
        return book
    else:
        return None
    
@main.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True

@main.errorhandler(404)
def page_not_found(e):
    return 'WOW WRONG'

@main.route("/", methods=['POST', "GET"])
def index():
    if request.method == "POST":
        bookname = escape_search(sanitize_string(request.form.get("bookname")))
        
        if bookname: 
            books = Books.query.filter(Books.title.ilike(f"%{bookname}%")).all()
            if len(books) > 0:
                bookname = bookname.replace('\\', '')
                return render_template("accounts/newsearch.html", books = books, bookname = bookname, number = str(len(books)))
            else:
                flash("No book was found on the database! Try again.", 'danger')
                return redirect("/")
        else:
            flash("No book name provided! Try again.", 'danger')
            return redirect("/")
    
    else:
        return render_template("accounts/index.html")

@main.route("/dashboard")
@login_required
@not_admin_required
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
                return render_template("main/dashboard.html", uname = current_user.username, route = route)
        
    else:
        current_user.last_login_date = date.today()
        db.session.commit()

    books_borrowed = len(current_user.books)
    books_approval = len(current_user.transactions)
    books_cart = len(current_user.items)
    books_favorite = len(current_user.favorites)

    return render_template("main/dashboard.html", uname = current_user.username, route = route, borrowed = str(books_borrowed), approval = str(books_approval), cart = str(books_cart), favorites = str(books_favorite)) 

@main.route("/profile")
@login_required
@not_admin_required
def profile():
    route = 'profile'
    books = current_user.books
    forapproval = []
    approval = current_user.transactions
    for book in approval:
        bookdata = book.books
        print(bookdata)
        booktitle = bookdata.title
        bookauthor = bookdata.author
        forapproval.append({'title': booktitle, 'author': bookauthor, 'submitted_on': book.requested_on})

    return render_template("main/profile.html", books = books, approval = forapproval, uname = current_user.username, route = route)

@main.route("/borrow")
@login_required
@not_admin_required
def borrow():
    route = 'borrow'
    return render_template("main/borrow.html", uname = current_user.username, route = route)

@main.route("/borrow", methods=["POST"])
@login_required
@not_admin_required
def borrow_post():

    route = 'borrow'

    bookname = escape_search(sanitize_string(request.form.get("bookname")))
    bookauthor = escape_search(sanitize_string(request.form.get("bookauthor")))
    bookyear = request.form.get("bookyear")
    bookgenre = escape_search(sanitize_string(request.form.get("bookgenre")))

    in_cart = [book.book_id for book in current_user.items]
    borrowed = [book.id for book in current_user.books]
    currentapproval = [book.book_id for book in current_user.transactions]
    favorites = [book.book_id for book in current_user.favorites]

    if not bookname and not bookauthor and not bookyear and not bookgenre:
        flash("Please fill-out the form with any of the details you know about the book.", 'danger')
        return redirect("/borrow")
    
    query = Books.query

    if bookname: 
        query = query.filter(Books.title.ilike(f"%{bookname}%"))

    if bookauthor: 
        query = query.filter(Books.author.ilike(f"%{bookauthor}%"))

    if bookyear: 

        nextyear = date.today().year + 1

        try:
            bookyear = check_integer(bookyear)
            nextyear = check_integer(nextyear)

            if nextyear is None:
                flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
                return redirect("/borrow") 
            
            if bookyear is None:
                flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
                return redirect("/borrow") 
            
            if bookyear <= nextyear:
                query = query.filter(Books.year == bookyear)
            else:
                flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
                return redirect("/borrow") 

        except:
            flash(f"Enter a valid year! (Max year is {str(nextyear)})", 'danger')
            return redirect("/borrow") 

    if bookgenre:
        query = query.filter(Books.genre.ilike(f"%{bookgenre}%"))

    books = query.distinct().order_by(Books.title).order_by(Books.year).all()

    if books:
        return render_template("main/newborrow.html", route = route, books=books, in_cart = in_cart, favorites = favorites, borrowed = borrowed, currentapproval = currentapproval, uname = current_user.username)
    
    else:
        flash("The database did not return any book using the filters that you gave.", 'danger')
        return redirect("/borrow")
    
@main.route("/borrowcart")
@login_required
@not_admin_required
def borrow_submit():

    books = [book for book in current_user.items]
    booklist = []
    for book in books:
        data = Books.query.get(book.book_id)
        booklist.append({'id': book.book_id, 'isbn': book.book_isbn, 'title': data.title, 'author': data.author})

    if booklist is None:
        return render_template("main/submitborrow.html", uname = current_user.username)

    else:
        booklist = sorted(booklist, key=itemgetter('title'))
        return render_template("main/submitborrow.html", books=booklist, uname = current_user.username)

@main.route("/borrowcart", methods=["POST"])   
@login_required
@not_admin_required
def borrow_submit_post():
    books_collected = len(current_user.books)
    books_forapprove = len(current_user.transactions)
    books_approval = request.form.getlist('books[]')
    operation = request.form.get("operation")

    if not books_approval:
        flash("You did not choose any book for approval. Make sure to tick the checkbox!", 'danger')
        return redirect("/borrowcart")
    
    elif books_approval and operation == "list":

        if (books_collected + books_forapprove) >= 10:
            if books_collected >= 10:
                flash(f"You currently have 10 books in possession. Students can only borrow a maximum of 10 books.", 'danger')
                return redirect("/borrowcart")
            else:
                flash(f"Students can only borrow a maximum of 10 books. You have {books_collected} borrowed and {books_forapprove} for approval.", 'danger')
                return redirect("/borrowcart")

        for book in books_approval:

            try:
                bookid = check_integer(book)
                if not bookid:
                    flash("The book does not exist", 'danger')
                    return redirect("/borrowcart")
                
                bookie = Books.query.get(bookid)
                if not bookie:
                    flash("The book does not exist", 'danger')
                    return redirect("/borrowcart")
                
                submitted = ForApproval.query.filter(ForApproval.book_id == bookie.id).filter(ForApproval.borrower == current_user.username).first()
                if submitted:
                    flash(f"You have already submitted {bookie.title} for approval. Remove it from your cart.", 'danger')
                    return redirect("/borrowcart")
                
                if not bookie.borrowed_by:
                    new_forapproval = ForApproval(book_id = bookie.id, book_isbn = bookie.isbn, borrower = current_user.username)
                    remove_cart = Cart.query.filter(Cart.book_id == bookie.id).filter(Cart.user_id == current_user.id).first()
                    db.session.delete(remove_cart)
                    db.session.add(new_forapproval)
                    db.session.commit()
                    flash(f"{bookie.title} has been submitted for approval!", 'success')

                else:
                    flash(f"The book {bookie.title} is already borrowed by someone else, sorry!", 'danger')
                    return redirect("/borrowcart")

            except Exception as e:
                flash(str(e), 'danger')
                return redirect("/borrowcart")
    
        return redirect("/borrowcart")
    
    elif books_approval and operation == "single":

        if (books_collected + books_forapprove) >= 10:
            if books_collected >= 10:
                flash(f"You currently have 10 books in possession. Students can only borrow a maximum of 10 books.", 'danger')
                return redirect("/borrow")
            else:
                flash(f"Students can only borrow a maximum of 10 books. You have {books_collected} borrowed and {books_forapprove} for approval.", 'danger')
                return redirect("/borrow")

        try:
            bookid = check_integer(books_approval[0])
            if not bookid:
                flash("The book does not exist", 'danger')
                return redirect("/borrow")
            
            bookie = Books.query.get(bookid)
            if not bookie:
                flash("The book does not exist", 'danger')
                return redirect("/borrow")
            
            submitted = ForApproval.query.filter(ForApproval.book_id == bookie.id).filter(ForApproval.borrower == current_user.username).first()
            if submitted:
                flash(f"You have already submitted {bookie.title} for approval. Remove it from your cart.", 'danger')
                return redirect("/borrow")
            
            if not bookie.borrowed_by:
                new_forapproval = ForApproval(book_id = bookie.id, book_isbn = bookie.isbn, borrower = current_user.username)
                db.session.add(new_forapproval)
                db.session.commit()
                flash(f"{bookie.title} has been submitted for approval!", 'success')
                return redirect("/borrow")

            else:
                flash(f"The book {bookie.title} is already borrowed by someone else, sorry!", 'danger')
                return redirect("/borrow")

        except Exception as e:
            flash(str(e), 'danger')
            return redirect("/borrow")

@main.route("/removecart", methods=["POST"])
@login_required
@not_admin_required
def remove_cart():
    books_remove = request.form.getlist('books[]')
    books_cart = [book.book_id for book in current_user.items]
    if not books_remove:
        flash("You did not choose any book for removal. Make sure to tick the checkbox!", 'danger')
        return redirect("/borrowcart")
    
    else:
        
        for book in books_remove:
            if int(book) in books_cart:
                try:
                    bookid = check_integer(book)
                    if not bookid: 
                        flash("You entered a wrong book ID.", 'danger')
                        return redirect("/borrowcart")
                    
                    bookie = Books.query.get(bookid)
                    if not bookie:
                        flash("The book does not exist", 'danger')
                        return redirect("/borrowcart")

                    remove_cart = Cart.query.filter(Cart.book_id == bookie.id).filter(Cart.user_id == current_user.id).first()
                    db.session.delete(remove_cart)
                    db.session.commit()
                    flash(f"{bookie.title} has been removed from your cart.", 'warning')

                except Exception:
                    flash("An error happened during removal. Try again later.", 'danger')
                    return redirect("/borrowcart")
            else:
                flash("This book is not in your cart.", 'danger')
                return redirect("/borrowcart")
            
        return redirect("/borrowcart")  

@main.route("/clearcart", methods=["POST"])
@login_required
@not_admin_required
def clear_cart():
    operation = escape_string(sanitize_string(request.form.get("operation")))

    if operation == "clear":
        books_clear = [book.book_id for book in current_user.items]
        
        if len(books_clear) > 0:

            deleted_books = 0

            for book in books_clear:
                check = Books.query.get(book)
                if check.borrowed_by:
                    deleted_books = deleted_books + 1
                    deletefromcart = Cart.query.filter(Cart.book_id == book).filter(Cart.user_id == current_user.id).first()
                    flash(f"{check.title} was removed from your cart as it is borrowed by someone else.", 'warning')
                    db.session.delete(deletefromcart)  
            
            if deleted_books > 0:
                try:
                    db.session.commit()
                    return redirect("/borrowcart")
                
                except:
                    db.session.rollback()
                    flash("Something went wrong while clearing your cart. Try again later.", 'danger')
                    return redirect("/borrowcart")
            else:
                flash("No books were removed because none of there were borrowed. Submit them for approval!", 'success')
                return redirect("/borrowcart")

        else:
            flash("You do not have books inside your cart. Consider adding more!", 'danger')
            return redirect("/borrowcart")
    
    else:
        flash("Invalid access.", 'danger')
        return redirect("/borrowcart")

@main.route("/cart", methods=["POST"])
@csrf.exempt
def cart():
    csrf_token = request.headers.get('X-CSRFToken')
    
    if current_user.is_authenticated:   

        if csrf_token is None:
            response = make_response(jsonify({"message": "Invalid CSRF Token"}), 400)
            response.headers['Content-Type'] = "application/json"
            return response

        else:
            try:
                validate_csrf(csrf_token)
            except ValidationError:
                response = make_response(jsonify({"message": "Invalid CSRF Token"}), 400)
                response.headers['Content-Type'] = "application/json"
                return response
            
        if current_user.is_admin:
            response = make_response(jsonify({"message": "Librarians are not allowed to add to cart."}), 400)
            response.headers['Content-Type'] = "application/json"
            return response

        ## Check limit 
        if current_user.cart_requests >= 100:
            response = make_response(jsonify({"message": "You can only add to cart 100 times per day to avoid abuse."}), 400)
            response.headers['Content-Type'] = "application/json"
            return response

        book_ids = [book.book_id for book in current_user.items]

        data = request.json
        bookid = sanitize_string(data.get('bookid'))

        try:
            bookid = check_integer(bookid)

            if bookid is None:
                response = make_response(jsonify({"message": "Invalid Book ID."}), 400)
                response.headers['Content-Type'] = "application/json"
                return response

            book = Books.query.get(bookid)
            if book:
                if bookid not in book_ids:
                    if not book.borrowed_by:    
                        try:
                            requests = current_user.cart_requests + 1
                            new_item = Cart(book_id = bookid, book_isbn = book.isbn, user_id = current_user.id)
                            current_user.cart_requests = requests
                            db.session.add(new_item)
                            db.session.commit()
                            response = make_response(jsonify({"message": "Book added to your cart."}), 200)
                            response.headers['Content-Type'] = "application/json"
                            return response
                        except Exception:
                            response = make_response(jsonify({"message": "Something went wrong."}), 400)
                            response.headers['Content-Type'] = "application/json"
                            return response
                    else:
                        response = make_response(jsonify({"message": "This book is already borrowed by somebody else."}), 400)
                        response.headers['Content-Type'] = "application/json"
                        return response
                else:
                    response = make_response(jsonify({"message": "You already have this book in your cart."}), 400)
                    response.headers['Content-Type'] = "application/json"
                    return response
            else: 
                response = make_response(jsonify({"message": "This book does not exist."}), 400)
                response.headers['Content-Type'] = "application/json"
                return response 
        except Exception:
            response = make_response(jsonify({"message": "Invalid book ID."}), 400)
            response.headers['Content-Type'] = "application/json"
            return response    
          
    else:
        response = make_response(jsonify({"message": "You need to login to add to cart."}), 400)
        response.headers['Content-Type'] = "application/json"
        return response
    
@main.route("/addtofavorite", methods=["POST"])
@csrf.exempt
def addtofavorite():
    csrf_token = request.headers.get('X-CSRFToken')
    
    if current_user.is_authenticated:   

        if csrf_token is None:
            response = make_response(jsonify({"message": "Invalid CSRF Token"}), 400)
            response.headers['Content-Type'] = "application/json"
            return response

        else:
            try:
                validate_csrf(csrf_token)
            except ValidationError:
                response = make_response(jsonify({"message": "Invalid CSRF Token"}), 400)
                response.headers['Content-Type'] = "application/json"
                return response

        if current_user.is_admin:
            response = make_response(jsonify({"message": "Librarians are not allowed to add to cart."}), 400)
            response.headers['Content-Type'] = "application/json"
            return response

        ## Check limit 
        if current_user.favorite_requests >= 500:
            response = make_response(jsonify({"message": "You can only add a book to your favorites 500 times per day to avoid abuse."}), 400)
            response.headers['Content-Type'] = "application/json"
            return response

        favorite_ids = [book.book_id for book in current_user.favorites]

        data = request.json
        bookid = sanitize_string(data.get('bookid'))

        try:
            bookid = check_integer(bookid)

            if bookid is None:
                response = make_response(jsonify({"message": "Invalid Book ID."}), 400)
                response.headers['Content-Type'] = "application/json"
                return response

            book = Books.query.get(bookid)
            if book:
                if bookid not in favorite_ids: 
                    try:
                        requests = current_user.favorite_requests + 1
                        new_favorite = Favorites(user_id = current_user.id, book_id = bookid)
                        current_user.favorite_requests = requests
                        db.session.add(new_favorite)
                        db.session.commit()
                        response = make_response(jsonify({"message": "Book added to your favorites."}), 200)
                        response.headers['Content-Type'] = "application/json"
                        return response
                    except Exception:
                        response = make_response(jsonify({"message": "Something went wrong."}), 400)
                        response.headers['Content-Type'] = "application/json"
                        return response
                else:
                    try:
                        requests = current_user.favorite_requests + 1
                        current_favorite = Favorites.query.filter(Favorites.user_id == current_user.id).filter(Favorites.book_id == bookid).first()
                        current_user.favorite_requests = requests
                        db.session.delete(current_favorite)
                        db.session.commit()
                        response = make_response(jsonify({"message": "Book removed from your favorites."}), 200)
                        response.headers['Content-Type'] = "application/json"
                        return response
                    except Exception:
                        response = make_response(jsonify({"message": "Something went wrong."}), 400)
                        response.headers['Content-Type'] = "application/json"
                        return response
            else: 
                response = make_response(jsonify({"message": "This book does not exist."}), 400)
                response.headers['Content-Type'] = "application/json"
                return response 
        except Exception:
            response = make_response(jsonify({"message": "Invalid book ID."}), 400)
            response.headers['Content-Type'] = "application/json"
            return response    
          
    else:
        response = make_response(jsonify({"message": "You need to login to add to your favorites."}), 400)
        response.headers['Content-Type'] = "application/json"
        return response   
    
@main.route('/myfavorites')
@login_required
@not_admin_required
def favorites():
    route = 'favorites'

    in_cart = [book.book_id for book in current_user.items]
    borrowed = [book.id for book in current_user.books]
    currentapproval = [book.book_id for book in current_user.transactions]
    favorites = [book.book_id for book in current_user.favorites]

    favoritebooks = current_user.favorites
    data = []

    for book in favoritebooks:
        favoritedetails = book.books
        data.append({'id': favoritedetails.id, 'title': favoritedetails.title, 'author': favoritedetails.author, 'description': favoritedetails.description, 'borrowed_by': favoritedetails.borrowed_by, 'isbn': favoritedetails.isbn})
    return render_template("main/newfavorites.html", uname = current_user.username, route = route, data = data, in_cart = in_cart, favorites = favorites, borrowed = borrowed, currentapproval = currentapproval)

@main.route("/history")
@login_required
@not_admin_required
def history():
    route = 'history'
    historyentries = History.query.filter(History.borrower == current_user.username).order_by(desc(History.updated_on)).all()
    data = []
    for book in historyentries:
        bookdetails = book.books
        data.append({'title': bookdetails.title, 'borrower': book.borrower, 'updated_on': book.updated_on, 'transaction': book.transaction})

    return render_template("main/history.html", uname = current_user.username, route = route, data = data)

@main.route("/request")
@login_required
@not_admin_required
def req():
    route = 'request'
    return render_template("main/newrequest.html", uname = current_user.username, route = route)

@main.route("/request", methods=["POST"])
@login_required
@not_admin_required
def req_post():
    route = 'request'

    bookname = escape_search(sanitize_string(request.form.get("bookname")))
    bookauthor = escape_search(sanitize_string(request.form.get("bookauthor")))
    bookisbn = escape_search(sanitize_string(request.form.get("bookisbn")))
    bookyear = escape_search(sanitize_string(request.form.get("bookyear")))

    if not bookname and not bookauthor and not bookisbn and not bookyear:
        flash("You need to give any detail regarding the book or article you are requesting for.", 'danger')
        return redirect("/request")
    
    if not bookname:
        flash("You need to provide a proper title in order to submit your request.", 'danger')
        return redirect("/request")
    
    if not bookauthor:
        flash("You need to provide a proper author in order to submit your request.", 'danger')
        return redirect("/request")
    
    if bookisbn:
        checkisbn = check_integer(bookisbn)
        if checkisbn is None:
            flash("You submitted an invalid ISBN code. Try again.", 'danger')
            return redirect("/request")
        else:
            bookisbn = checkisbn

    if bookyear:
        checkyear = check_integer(bookyear)
        if checkyear is None:
            flash("You submitted an invalid year. Try again.", 'danger')
            return redirect("/request")
        
    if not bookisbn:
        bookisbn = None

    if not bookyear:
        bookyear = None
        
    newrequest = Requests(user_id = current_user.id, title = bookname, author = bookauthor, isbn = bookisbn, year = bookyear, status = "Pending")

    try:
        db.session.add(newrequest)
        db.session.commit()
        flash("Your request was submitted and forwarded to the libriarian.", 'success')
        return redirect("/request")
    
    except:
        db.session.rollback()
        flash("An error happened while your adding your request, try again later.", 'danger')
        return redirect("/request")

@main.route("/myrequests")
@login_required
@not_admin_required
def decided_requests():
    route = 'myrequests'
    requests = Requests.query.filter(Requests.user_id == current_user.id).order_by(desc(Requests.updated_on)).limit(100).all()

    return render_template("main/processedrequests.html", requests = requests, uname = current_user.username, route = route)

@main.route("/updatepassword")
@login_required
@not_admin_required
def request_update_pass():
    route = "updatepass"
    return render_template("main/newupdatepass.html", route = route, uname = current_user.username)

@main.route("/updatepassword", methods=["POST"])
@login_required
@not_admin_required
def update_pass():
    route = "updatepass"

    oldpassword = request.form.get("oldpassword")
    newpassword = request.form.get("newpassword")
    newpasswordconfirmation = request.form.get("newpasswordconfirmation")

    if not oldpassword:
        flash("You need to provide your old password. Try again.", 'danger')
        return redirect("/updatepassword")

    if not newpassword:
        flash("You did not provide a new password. Try again.", 'danger')
        return redirect("/updatepassword")

    if not newpasswordconfirmation:
        flash("You did not re-enter your new password. Try again.", 'danger')
        return redirect("/updatepassword")
    
    if newpassword != newpasswordconfirmation:
        flash("The new password and confirmation password that you entered are not the same. Try again.", 'danger')
        return redirect("/updatepassword")
    
    user = Users.query.filter(Users.id == current_user.id).first()

    if bcrypt.checkpw(oldpassword.encode('utf-8'), user.hash.encode('utf-8')):

        user.hash = bcrypt.hashpw(newpassword.encode('utf-8'), bcrypt.gensalt())

        try:
            db.session.commit()
            logout_user()
            flash("Your password was successfully updated. Please login again.", 'success')
            return redirect("/login")
        
        except:
            db.session.rollback()
            flash("A problem happened while updating your password. No changes were saved. Try again later.", 'danger')
            return redirect("/updatepassword")
        
    else:
        flash("The old password that you entered and the current password of this account are not the same. Try again.", 'danger')
        return redirect("/updatepassword")

