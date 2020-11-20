# -*- coding: utf-8 -*-

from flask import redirect, render_template, flash, Blueprint, request, url_for, session, jsonify
from flask_login import current_user, login_required, logout_user
from flask_paginate import Pagination, get_page_parameter
from .models import db, UserInput, User
from .forms import UiForm
from datetime import datetime as dt
import random
import string
from .bin import valuation
from sqlalchemy import text
from datatables import ColumnDT, DataTables
from decimal import Decimal


def randStr(chars = string.ascii_uppercase + string.digits, N=10):
	return ''.join(random.choice(chars) for _ in range(N))


# Blueprint Configuration
valuation_bp = Blueprint(
    'valuation_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@valuation_bp.route('/valuation', methods=['GET', 'POST'])
@login_required


def user_input():
    session.permanent = True
    page = request.args.get('page', 1, type = int)
      
    queries = UserInput.query.order_by(UserInput.created_on.desc()).filter(text('user_input.user::integer = :id')).params(id = current_user.id)
    queries = queries.paginate(page = page, per_page = 6)

    form = UiForm(obj=UserInput)
    print(session['last_login'])

    if form.validate():
        print('Validation successful')


    if form.validate() and form.is_submitted():
        query_id = randStr()

        user_form_input = UserInput(
            osoite = form.ui_osoite.data,
            kunta = form.ui_kunta.data,
            postinumero = form.ui_postinumero.data,
            asuntotyyppi = form.ui_asuntotyyppi.data,
            asuinala = form.ui_asuinala.data,
            rakennusvuosi = form.ui_rakennusvuosi.data,
            huone_lkm = form.ui_huone_lkm.data,
            kerros = form.ui_kerros.data,
            kerros_yht = form.ui_kerros_yht.data,
            kunto = form.ui_kunto.data,
            tontti = form.ui_tontti.data,
            vastike = form.ui_vastike.data,
            vuokrattu = form.ui_vuokrattu.data,
            hissi = form.ui_hissi.data,
            sauna = form.ui_sauna.data,
            parveke = form.ui_parveke.data,
            tonttiala = form.ui_tonttiala.data,
            muu_kerrosala = form.ui_muu_kerrosala.data,
            created_on=dt.now(),
            user=int(current_user.id),
            query_id = query_id,
            hinta = None)

        db.session.add(user_form_input)
        db.session.commit()

        try:
            hinta = valuation.calculate(UserInput, query_id)[0]
            hinta = float(hinta)
            hinta = round(hinta, -3)

        
            
            db.session.execute(
                text("UPDATE user_input SET hinta=:param2 WHERE query_id=:param1"),
                params = {"param2":hinta, "param1":query_id}
            )
            db.session.commit()
        
        
        except ValueError as V:
            if V.args[1] == 'street':
                form.populate_obj(UserInput)
                flash('Osoite on virheellinen','street_err')
                print(V.args[1])
            elif V.args[1] == 'country':
                form.populate_obj(UserInput)
                flash('Osoite on virheellinen','input_err')
                print(V.args[1])
            elif V.args[1] == 'city':
                form.populate_obj(UserInput)
                flash( f'Kunnasta {form.ui_kunta.data} ei löytynyt osoitetta {form.ui_osoite.data}. Tarkista kunta','city_err')
                print(V.args[1])
                print(UserInput.osoite)
            elif V.args[1] == 'bad_score':
                form.populate_obj(UserInput)
                flash( f'Osoitteella {form.ui_osoite.data} epäselvä osumatulos. Kokeile toista osoitetta','street_err')
                print(V.args[1])
                print(UserInput.osoite)
            elif V.args[1] == 'multiple_streets':
                form.populate_obj(UserInput)
                flash( f'Osoitteella {form.ui_osoite.data} löytyi useita hakutuloksia. Tarkenna hakua','street_err')
                print(V.args[1])
                print(UserInput.osoite)
            elif V.args[1] == 'no_streets':
                form.populate_obj(UserInput)
                flash( f'Osoite on virheellinen','street_err')
                print(V.args[1])
                print(UserInput.osoite)
                  

        return redirect('/valuation')
    

    return render_template('inputs.html', form = form,
    query_history = UserInput.query.order_by(UserInput.created_on.desc()).all(),
    queries=queries)



@valuation_bp.route("/tables")
@login_required
def tables():
    """List users with DataTables <= 1.10.x."""
    return render_template('tables.html', project='tables')






@valuation_bp.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    session.permanent = True

    """Return server side data."""
    # defining columns
    columns = [
        ColumnDT(UserInput.osoite),
        ColumnDT(UserInput.kunta),
        ColumnDT(UserInput.asuntotyyppi),
        ColumnDT(UserInput.asuinala),
        ColumnDT(UserInput.rakennusvuosi),
        ColumnDT(UserInput.kunto),
        ColumnDT(UserInput.created_on),
        ColumnDT(UserInput.rakennusvuosi),
        ColumnDT(UserInput.rakennusvuosi),
        ColumnDT(UserInput.hinta),        
    ]

    # Query the users data by filtering with the user id
    #query = UserInput.query.filter(text('user_input.user::integer = :id')).params(id = current_user.id)
    query = db.session.query().select_from(UserInput).filter(text('user_input.user::integer = :id')).params(id = current_user.id)

    # GET parameters
    params = request.args.to_dict()

    # Lambda to take care of missing data in price column:
    null_check = lambda x : int(Decimal(x)) if x else 'Hakuvirhe'

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    for item in rowTable.output_result()['data']:
        item['7'] = str(item['6'].strftime("%d.%m.%Y %H:%M"))
        item['6'] = int((item['6'] - dt(1970, 1, 1)).total_seconds()) #UNIX Timestamp
        item['9'] = null_check(item['9'])
        

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())




   
