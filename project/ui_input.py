# -*- coding: utf-8 -*-

from flask import redirect, render_template, flash, Blueprint, request, url_for, session, jsonify, make_response
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
from time import sleep
import plotly
import plotly.express as px
import plotly.graph_objs as go
from pathlib import Path
import os
import pandas as pd
import json
from statistics import mean




# Read mapbox access token
wdir = Path(__file__).parent.absolute()
px.set_mapbox_access_token(open(os.path.join(wdir, "data", "mb.mapbox_token")).read())
mapbox_access_token = open(os.path.join(wdir, "data", "mb.mapbox_token")).read()

# Key generator for query id's
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

    params = request.args.to_dict()

    if 'action' not in params:
        session.permanent = True
        page = request.args.get('page', 1, type = int)
        
        queries = UserInput.query.order_by(UserInput.created_on.desc()).filter(text('user_input.user::integer = :id')).params(id = current_user.id)
        queries = queries.paginate(page = page, per_page = 6)

        form = UiForm(obj=UserInput)
        print(session['last_login'])


        # USER INPUT FORM AND VALUATION CALCULATION
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
                hinta = None,
                lat = None,
                lng = None)

            db.session.add(user_form_input)
            db.session.commit()

            try:
                hinta = valuation.calculate(UserInput, query_id)[0]
                hinta = float(hinta)
                hinta = round(hinta, -3)
                lat,lng = valuation.geodata.geocode(form.ui_osoite.data, form.ui_kunta.data)

            
                
                db.session.execute(
                    text("UPDATE user_input SET hinta=:param2 WHERE query_id=:param1"),
                    params = {"param2":hinta, "param1":query_id}
                )
                db.session.execute(
                    text("UPDATE user_input SET lng=:param2 WHERE query_id=:param1"),
                    params = {"param2":lng, "param1":query_id}
                )
                db.session.execute(
                    text("UPDATE user_input SET lat=:param2 WHERE query_id=:param1"),
                    params = {"param2":lat, "param1":query_id}
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
    

    # GET request to repopulate form data
    if 'action' in params:
        query_id = params['query_id']
        query_pop = db.session.query(UserInput).filter(text('user_input.query_id = :query_id')).params(query_id = query_id).first()        
        
        data_dict = query_pop.__dict__
        data_dict.pop('_sa_instance_state')

        # Lambda to take care of missing data in price column:
        null_check = lambda x : int(Decimal(x)) if x else 'Hakuvirhe'
        null_check_coord = lambda x : float(Decimal(x)) if x else None

        data_dict['created_on'] = str(data_dict['created_on'].strftime("%d.%m.%Y %H:%M"))
        data_dict['hinta'] = null_check(data_dict['hinta'])
        data_dict['lat'] = null_check_coord(data_dict['lat'])
        data_dict['lng'] = null_check_coord(data_dict['lng'])        

        response = make_response(json.dumps(data_dict))
        response.content_type = 'application/json'

        return response
   

    return render_template('inputs.html', form = form, content_title = "Valuation Engine")


   


@valuation_bp.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    session.permanent = True

    """Return server side data."""
    # defining columns
    # NOTE: DO NOT CHANGE THE ORDER!!!!
    columns = [
        ColumnDT(UserInput.osoite),
        ColumnDT(UserInput.kunta),
        ColumnDT(UserInput.postinumero),
        ColumnDT(UserInput.asuntotyyppi),
        ColumnDT(UserInput.asuinala),
        ColumnDT(UserInput.rakennusvuosi),
        ColumnDT(UserInput.kunto),
        ColumnDT(UserInput.created_on),
        ColumnDT(UserInput.rakennusvuosi),
        ColumnDT(UserInput.hinta),
        ColumnDT(UserInput.sauna),
        ColumnDT(UserInput.parveke),
        ColumnDT(UserInput.hissi),
        ColumnDT(UserInput.vuokrattu),
        ColumnDT(UserInput.vastike),
        ColumnDT(UserInput.tonttiala),
        ColumnDT(UserInput.muu_kerrosala),
        ColumnDT(UserInput.huone_lkm),
        ColumnDT(UserInput.kerros),
        ColumnDT(UserInput.kerros_yht), 
        ColumnDT(UserInput.tontti),
        ColumnDT(UserInput.query_id)       
    ]

    # Query the users data by filtering with the user id
    query = db.session.query().select_from(UserInput).filter(text('user_input.user::integer = :id')).params(id = current_user.id)


    # GET parameters
    params = request.args.to_dict()

    # Lambda function to shift params order by magnitude of 1:
    new_order = lambda x:  int(x) - 1 if x else None   
    update_sort = {'order[0][column]': str(new_order(params['order[0][column]']))}

    # Lambda to take care of missing data in price column:
    null_check = lambda x : int(Decimal(x)) if x else 'Hakuvirhe'

    # Update column order if order has been requested:
    if new_order(params['order[0][column]']) >= 0:
        params.update(update_sort)

    
    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    for item in rowTable.output_result()['data']:
        item['8'] = int((item['7'] - dt(1970, 1, 1)).total_seconds()) #UNIX Timestamp
        item['7'] = str(item['7'].strftime("%d.%m.%Y %H:%M"))
        item['9'] = null_check(item['9'])
        

    # returns what is needed by DataTable
    # Sleep function added for first draw of data (enables loading animation to be seen)

    if params['draw'] == '1':
        sleep(2)
    return jsonify(rowTable.output_result())



def create_map(lat, lng):

    
    

    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
            lat=lat,
            lon=lng,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=17,
                color='rgb(255, 0, 0)',
                opacity=0.7
            ),
            text = 'kohde',
            hoverinfo='text'
        ))

    fig.add_trace(go.Scattermapbox(
            lat=lat,
            lon=lng,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=8,
                color='rgb(242, 177, 172)',
                opacity=0.7
            ),
            hoverinfo='none'
        ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            pitch=0,
            center=dict(
            lat=mean(lat),
            lon=mean(lng)
        ),
            zoom=11,
            style='mapbox://styles/axwdigital/ckhx9p6b002ra19nsd4ry1cz9'
        ),
        margin = dict(l=20, r=20, t=20, b=20)
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON






@valuation_bp.route('/map', methods=['GET', 'POST'])
@login_required

def map():
    
    # Plotly maps integration



    # Use sample data in mapbox
    # TODO Update the df to contain only the coordinates that are in question for a given child row in the 
    # datatables element

    params = request.args.to_dict()

    # template_path = os.path.join(valuation_bp.root_path, valuation_bp.template_folder)

    # df = px.data.carshare()
    # fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon", color="peak_hour", size="car_hours",
    #               color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    # fig.write_html(os.path.join(template_path, 'datatable_map.html'))


    query_id = params['query_id']
    lat_ = []
    lng_ = []

    if query_id != 'all':
        query = db.session.query(UserInput).filter(text('user_input.query_id = :query_id')).params(query_id = query_id).first()
        lat = float(query.lat)
        lng = float(query.lng)
        lat_.append(lat)
        lng_.append(lng)
    else:
        query = db.session.query(UserInput).all()
        for row in query:
            lat = float(row.lat)
            lng = float(row.lng)
            lat_.append(lat)
            lng_.append(lng)

    graphJSON= create_map(lat_, lng_)




    return graphJSON


    # return render_template('map.html', maps=open(os.path.join(valuation_bp.root_path, valuation_bp.template_folder, "datatable_map.html")).read())


   
