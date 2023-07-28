from . import db
from .models import Books
from sqlalchemy import insert
import requests
from csv import DictReader
import requests
import os

def add_books(filepath, bookdb):
        try:
                current_books = bookdb
                booklist = []
                with open(filepath, "r") as file:
                        reader = DictReader(file)
                        isbns = []
                        for book in reader:
                                

                                if book['isbn'] in current_books:
                                        continue
                                else:
                                        isbn = f"ISBN:{book['isbn']}"
                                        booklist.append({'title': book['title'], 'author': book['author'], 'isbn': book['isbn'], 'publisher': book['publisher'], 'year': book['year'], 'genre': book['genre'], 'request': isbn})
                                        isbns.append(isbn)

                        books = ",".join(isbns)

                if booklist:
                        r = requests.get(f"https://openlibrary.org/api/books?bibkeys={books}&format=json&jscmd=details")
                        if r.status_code == 200:
                                response = r.json()
                                for book in booklist:
                                        try:
                                                description = str(response[book['request']]['details']['description']['value'])
                                        except Exception:
                                                description = "This book does not have a synopsis available in OpenLibrary." 
                                        book['description'] = description

                        db.session.execute(insert(Books), booklist)
                        db.session.commit()
                        os.remove(filepath)
                        return True, "Your CSV file has been proccessed successfully and added into our database!"
                else:
                        return False, "No new books were found from your file."
        
        except Exception:
                return False, "There was an error uploading your file."
        




                
