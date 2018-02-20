from flask import Blueprint, redirect, render_template, request, url_for
from flask_user import current_user, login_required
from app import db, babel
from app.models.user_models import UserProfileForm
from flask import current_app as app
import gettext

members_blueprint = Blueprint('members', __name__, template_folder='templates')


@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in
                    babel.list_translations()]
    return request.accept_languages.best_match(translations)


def set_lang(lang):
    i18n_dir = app.config['BABEL_TRANSLATION_DIRECTORIES']
    gettext.install('lang', i18n_dir)
    trans_file = i18n_dir + lang + '/LC_MESSAGES/flask_user'
    tr = gettext.translation(trans_file, 'locale',  languages=[lang])
    tr.install(True)
    app.jinja_env.install_gettext_translations(tr)


@members_blueprint.before_app_request
def before_request():
    lang = get_locale()
    lang = lang if lang else app.config['BABEL_DEFAULT_LOCALE']
    set_lang(lang)

    if request.path.startswith('/admin'):
        if current_user.is_authenticated:
            if not current_user.has_role("admin"):
                return redirect(url_for('user.logout'))
        else:
            return redirect(url_for('user.login'))


@members_blueprint.route('/members/')
@login_required
def member_page():
    return render_template('pages/user_page.html')


@members_blueprint.route('/members/profile/', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    # form = UserProfileForm(request.form, current_user)
    form = UserProfileForm()

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('public.home_page'))

    # Process GET or invalid POST
    return render_template('pages/user_profile_page.html',
                           form=form)
