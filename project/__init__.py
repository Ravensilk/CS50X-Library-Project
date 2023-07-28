from flask import Flask, flash, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from itsdangerous import URLSafeTimedSerializer, URLSafeSerializer
from dotenv import load_dotenv
from flask_mail import Mail
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
from werkzeug.exceptions import HTTPException, NotFound


db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()

 # Start Serializer 
idserializer = URLSafeSerializer(os.getenv('app_secret_key'))
serializer = URLSafeTimedSerializer(os.getenv('app_secret_key'))
serializeremailsalt = os.getenv('SECURITY_EMAIL_SALT')
serializeridsalt = os.getenv('SECURITY_ID_SALT')
serializerchangepasssalt = os.getenv('SECURITY_CHANGEPASS_SALT')

def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.secret_key = os.getenv('app_secret_key')
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://" + os.getenv('DB_USER') + ":" + os.getenv('DB_PASSWORD') + "@" + os.getenv('DB_HOST') + "/cs50structured"
    UPLOAD_FOLDER = 'project/static/uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    db.init_app(app)

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.refresh_view = 'auth.login'
    login_manager.login_message_category = 'danger'
    login_manager.needs_refresh_message_category = 'danger'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(id)
    
    # Register Blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .adminauth import adminauth as adminauth_blueprint
    app.register_blueprint(adminauth_blueprint)

    from .adminmain import adminmain as adminmain_blueprint
    app.register_blueprint(adminmain_blueprint)

    # Import models
    from .models import Users

    # Start Mail instance
    mail.init_app(app)

    # Initiate CSRF 
    csrf.init_app(app)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Invalid CSRF code, reload the page, login (if you we're logged in, your session expired) and try again.", 'danger')
        return redirect("/")

    @app.errorhandler(HTTPException)
    def page_not_found(e):
        return render_template("accounts/error.html")
    
    @app.errorhandler(NotFound)
    def page_not_found(e):
        return render_template("accounts/error.html")
    
    # Create tables
    with app.app_context():
        db.create_all()

    return app