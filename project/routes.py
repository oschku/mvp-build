# -*- coding: utf-8 -*-

"""Logged-in page routes."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required, logout_user
from flask import request, render_template, make_response, session
from datetime import datetime as dt
from flask import current_app as app
from .models import db, User
from babel.numbers import format_currency

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)




@main_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    """Logged-in User Dashboard."""
    session.permanent = True
    return render_template(
        'test.html',
        title='Valuation engine',
        content_title='Valuation engine',
        template='dashboard-template',
        current_user=current_user,
        body="VALU/AI"
    )


@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_bp.login'))



@app.template_filter()
def eur(value):
    if value:
        value = int(value)
    else:
        value = 0
    return format_currency(value, 'EUR', locale='fi_FI')

app.jinja_env.filters['eur'] = eur