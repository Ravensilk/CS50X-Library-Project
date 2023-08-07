# Library Management System - CS50 Final Project
#### Video Demo:  https://youtu.be/yiA3fghi0lY
#### Description:

This project is for the CS50x course in EDx. It is a library management system which uses Python, HTML, CSS and Javascript. It runs on a MYSQL database and is handled by SQL Alchemy for the database management.

I envisioned this project to help solve some problems of schools who are still sticking to the card catalog system, which makes the library less efficient and makes it hard for librarians to really keep track of all the books and other articles found in their library.

This system was made intuitive and easy to use and understand. It uses different modules and packages from the python library to handle different processes. Registration, login and session control is handled by **flask-login**, secret key generation is handled by **itsdangerous**, password hashing is handled by **bcrypt**, database management is handled by **SQL Alchemy**, the whole system is served on **Flask**, forms and CSRF protection is handled by **Flask-WTF**, email sending is handled by **flask_mail** and several other modules were also used.

### __init__.py
This is where all the initialization of all the different library such as Flask-Login, SQL Alchemy, Flask-WTF, Itsdangerous and other libraries that have used are being done. It also contains the different env codes that the system will use for different settings.

### main.py
This file contains all the methods and functions that logged in users can use to navigate the website. It is a blueprint which is rendered at the __init__.py file.

### auth.py
This file contains all of the methods and functions that users who would want to login or register will use in order to access the website. It has the login, register, change password and verify account functions.

### adminmain.py
This file contains all the methods and functions that logged in administrators can use to navigate the website. It is a blueprint which is rendered at the __init__.py file.

### adminauth.py
This file contains all of the methods and functions that administrator who would want to login or register will use in order to access the website. It has the login function, which verifies if the person logging in is an administrator.

### decorators.py
This file contains all of the methods and functions used for sanitizing and checking values or files submitted to the programs and that functions ran in main.py, auth.py, adminmain.py, adminauth.py and models.py.

### models.py
This file contains all of the models that is being used by SQL Alchemy in order to do the queries and database management. It has the users, books, lostbooks, requests and different tables that are made once the system is run.

### details.py
This file contains that functions that is used for adding different books into the database when an administrator uploads books through the website.

## /templates

### /accounts
This folder contains all of the files that are used by the auth.py and main.py on rendering the different pages for users who are not logged it.

### /admin
This folder contains all of the files that are used by the adminmain.py and adminauth.py on rendering the different pages for administrators who are trying to login and navigate the website.

### /main
This folder contains all of the files that are used by the adminmain.py and adminauth.py on rendering the different pages for users who are trying to login and navigate the website.

## /static

### /css
This folder contains all the files that are used by jinja to generate styling (through CSS) for the different pages of the website.

### /images
This folder contains all the images being used by the website.

### /js
This folder contains all the javascript files used by jinja to handle all the animations and functionalities used in the website. This includes the mobile nagivation, the add to cart buttons and several other functions.

### /uploads
This folder contains all the temporary files used when an administrator uploads a book file into the system in order to update the database.
