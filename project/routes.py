# -*- coding: utf-8 -*-

"""Logged-in page routes."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required, logout_user
from flask import request, render_template, make_response, session
from datetime import datetime as dt
from flask import current_app as app
from .models import db, User, UserInput
from babel.numbers import format_currency
from sqlalchemy import text
from sqlalchemy.sql import func
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
    data = db.session.query(UserInput).filter(text('user_input.user::integer = :user_id')).params(user_id = current_user.id)
    price_data = db.session.query(UserInput).with_entities(func.avg(UserInput.hinta)).filter(text('user_input.user::integer = :user_id')).params(user_id = current_user.id).first()[0]
    if price_data:
        price_data = format_currency(price_data, 'EUR', format=u'#,##0\xa0¤', locale='fi_FI', currency_digits=False)
    else:
        price_data = "Ei hakuja"
    return render_template(
        'dashboard.html',
        content_title='Dashboard',
        template='dashboard-template',
        current_user=current_user,
        body="VALU/AI",
        data=data,
        price_data=price_data
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

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")