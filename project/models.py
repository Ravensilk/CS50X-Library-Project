from . import db
from datetime import datetime, date
from sqlalchemy import text
from flask_login import UserMixin

class Users(UserMixin, db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
        username = db.Column(db.String(100), unique=True, nullable=False)
        email = db.Column(db.String(255), nullable=False)
        hash = db.Column(db.Text, nullable=False)
        registered = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))
        last_login_date = db.Column(db.Date, nullable=True)
        cart_requests = db.Column(db.Integer, nullable=False, default = 0)
        favorite_requests = db.Column(db.Integer, nullable=False, default = 0)
        is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
        confirmed_on = db.Column(db.DateTime, nullable=True)
        locked = db.Column(db.Boolean, nullable=False, default=False)
        is_admin = db.Column(db.Boolean, nullable=False, default=False)

        books = db.relationship("Books", back_populates="user")
        transactions = db.relationship("ForApproval", back_populates="user")
        history = db.relationship("History", back_populates="user")
        items = db.relationship("Cart", back_populates="user")
        favorites = db.relationship("Favorites", back_populates="user")
        lostbooks = db.relationship("LostBooks", back_populates="user")
        requests = db.relationship("Requests", back_populates="user")

class Books(db.Model):
        __tablename__ = "books"
        id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
        title = db.Column(db.String(255), nullable=False)
        description = db.Column(db.Text, nullable=False)
        author = db.Column(db.String(255), nullable=False)
        publisher = db.Column(db.String(255), nullable=False)
        isbn = db.Column(db.String(100), unique=True, nullable=False)
        genre = db.Column(db.String(100), nullable=False)
        year = db.Column(db.String(5), nullable=False)
        borrowed_by = db.Column(db.String(100), db.ForeignKey("users.username"), nullable=True)
        borrowed_on = db.Column(db.DateTime, nullable=True)
        last_borrowed_by = db.Column(db.String(100), nullable=True)
        last_returned_on = db.Column(db.DateTime, nullable=True)

        user = db.relationship("Users", back_populates="books")
        transactions = db.relationship("ForApproval", back_populates="books")
        history = db.relationship("History", back_populates="books")
        items = db.relationship("Cart", back_populates="books")
        favorites = db.relationship("Favorites", back_populates="books")
        lostbookdetails = db.relationship("LostBooks", back_populates="books")

class ForApproval(db.Model):
        __tablename__ = "for_approval"
        id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
        book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
        book_isbn = db.Column(db.String(100), nullable=False)
        borrower = db.Column(db.String(100), db.ForeignKey("users.username"), nullable=False)
        requested_on = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))

        books = db.relationship("Books", back_populates="transactions")
        user = db.relationship("Users", back_populates="transactions")


class History(db.Model):
        __tablename__ = "history"
        id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
        book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
        borrower = db.Column(db.String(100), db.ForeignKey("users.username"), nullable=False)
        updated_on = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))
        transaction = db.Column(db.String(20), nullable=False)

        books = db.relationship("Books", back_populates="history")
        user = db.relationship("Users", back_populates="history")

class Cart(db.Model):
        __tablename__ = "cart"
        id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
        user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
        book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
        book_isbn = db.Column(db.String(100), nullable=False)
        added_on = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))

        user = db.relationship("Users", back_populates="items")
        books = db.relationship("Books", back_populates="items")

class Favorites(db.Model):
        __tablename__ = "favorites"
        id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
        user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
        book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
        favorited_on = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))

        user = db.relationship("Users", back_populates="favorites")
        books = db.relationship("Books", back_populates="favorites")

class LostBooks(db.Model):
        __tablename__ = "lost_books"
        id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
        lost_by = db.Column(db.String(100), db.ForeignKey("users.username"), nullable=False)
        book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
        borrowed_on = db.Column(db.DateTime, nullable=False)

        user = db.relationship("Users", back_populates="lostbooks")
        books = db.relationship("Books", back_populates="lostbookdetails")

class Requests(db.Model):
        __tablename__ = "requests"
        id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
        user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
        title = db.Column(db.String(255), nullable=False)
        author = db.Column(db.String(255), nullable=False)
        isbn = db.Column(db.String(100), unique=True, nullable=True, default = None)
        year = db.Column(db.String(5), nullable=True, default = None)
        status = db.Column(db.String(20), nullable=True)
        feedback = db.Column(db.String(255), nullable=True)
        requested_on = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))
        updated_on = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=text("CURRENT_TIMESTAMP"))

        user = db.relationship("Users", back_populates="requests")

