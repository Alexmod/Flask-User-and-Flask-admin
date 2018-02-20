from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView
import os.path as op


# Instantiate Flask extensions
db = SQLAlchemy()
csrf_protect = CSRFProtect()
mail = Mail()
migrate = Migrate()
babel = Babel()


def create_app(extra_config_settings={}):
    # Create a Flask applicaction.

    # Instantiate Flask
    app = Flask(__name__)

    # Load App Config settings
    # Load common settings from 'app/settings.py' file
    app.config.from_object('app.settings')
    # Load local settings from 'app/local_settings.py'
    app.config.from_object('app.local_settings')
    # Load extra config settings from 'extra_config_settings' param
    app.config.update(extra_config_settings)

    # Setup Flask-Extensions -- do this _after_ app config has been loaded

    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup Flask-Migrate
    migrate.init_app(app, db)

    # Setup Flask-Mail
    mail.init_app(app)

    # Setup WTForms CSRFProtect
    csrf_protect.init_app(app)

    # Register blueprints
    from app.views.public_views import public_blueprint
    app.register_blueprint(public_blueprint)
    from app.views.members_views import members_blueprint
    app.register_blueprint(members_blueprint)
    # from app.views.admin_views import admin_blueprint
    # app.register_blueprint(admin_blueprint)

    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    from wtforms.fields import HiddenField

    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # Setup an error-logger to send emails to app.config.ADMINS
    init_email_error_handler(app)

    # Setup Flask-User to handle user account related forms
    from .models.user_models import User, MyRegisterForm
    from .views.members_views import user_profile_page
    db_adapter = SQLAlchemyAdapter(db, User)  # Setup the SQLAlchemy DB Adapter
    UserManager(
        db_adapter, app,  # Init Flask-User and bind to app
        register_form=MyRegisterForm,  # Custom register form UserProfile fields
        user_profile_view_function=user_profile_page,
    )

    babel.init_app(app)  # Initialize Flask-Babel

    Bootstrap(app)  # Initialize flask_bootstrap

    # Admin part
    class AdminUserView(ModelView):
        can_create = False
        column_display_pk = True
        column_exclude_list = ('password')
        form_overrides = dict(password=HiddenField)

    class AdmUsersRolesView(ModelView):
        column_display_pk = True

    class AdmRolesView(ModelView):
        column_display_pk = True

    from .models.models import AdmUsers, AdmUsersRoles, AdmRoles
    admin = Admin(app, template_mode='bootstrap3')
    admin.add_view(AdminUserView(AdmUsers, db.session, name='Users'))
    admin.add_view(AdmRolesView(AdmUsersRoles, db.session,
                                name='Roles-User'))
    admin.add_view(AdmUsersRolesView(AdmRoles, db.session, name='Role'))
    path = op.join(op.dirname(__file__), 'static')
    admin.add_view(FileAdmin(path, '/static/', name='Files'))
    admin.add_link(MenuLink(name='Profile', endpoint='user.profile'))
    admin.add_link(MenuLink(name='Logout', endpoint='user.logout'))

    return app


def init_email_error_handler(app):
    # Initialize a logger to send emails on error-level messages.
    # Unhandled exceptions will now send an email message to app.config.ADMINS.
    if app.debug:
        return  # Do not send error emails while developing

    # Retrieve email settings from app.config
    host = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )

    # Log errors using: app.logger.error('Some error message')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
