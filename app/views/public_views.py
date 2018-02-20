from flask import Blueprint, render_template

public_blueprint = Blueprint('public', __name__, template_folder='templates')


@public_blueprint.route('/')
def home_page():
    return render_template('pages/home_page.html')
