# -*- coding: utf-8 -*-

from flask import redirect, render_template, flash, Blueprint, request, url_for, session, jsonify, make_response
from flask_login import current_user, login_required, logout_user
from flask_paginate import Pagination, get_page_parameter
from .models import db, UserInput, User, ApiKey
from .forms import UiForm
from datetime import datetime as dt
import random
import string
from sqlalchemy import text
from datatables import ColumnDT, DataTables
from decimal import Decimal
from time import sleep
import plotly
import plotly.express as px
import plotly.graph_objs as go
from pathlib import Path
import os
import json
from statistics import mean
from babel.numbers import format_currency
import numpy as np
import requests as r
import datetime
import pytz





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

# Timezone converter
def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.strptime(dt,"%d.%m.%Y %H:%M:%S")
    dt = tz1.localize(dt)
    print(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%d.%m.%Y %H:%M:%S")

    return dt

@valuation_bp.route('/valuation', methods=['GET', 'POST'])
@login_required


def user_input():
    """Class returns input fields on the user page"""
    
    params = request.args.to_dict()
    backend_url = os.environ['AWS_URL']
    apiKey = ApiKey.query.filter(text('api_keys.user_id::integer = :id')).params(id = current_user.id).all()[0].apikey
    

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
            
            # NOTE For later purposes, remember to query for actual user no, is now set as 1 for testing purposes!
            request_object = {
                'osoite': form.ui_osoite.data,
                'kunta' : form.ui_kunta.data,
                'postinumero' : form.ui_postinumero.data,
                'asuntotyyppi' : form.ui_asuntotyyppi.data,
                'asuinala' : float(form.ui_asuinala.data),
                'rakennusvuosi' : form.ui_rakennusvuosi.data,
                'huone_lkm' : int(form.ui_huone_lkm.data),
                'kerros' : form.ui_kerros.data,
                'kerros_yht' : form.ui_kerros_yht.data,
                'kunto' : form.ui_kunto.data,
                'tontti' : form.ui_tontti.data,
                'vastike' : form.ui_vastike.data,
                'vuokrattu' : int(form.ui_vuokrattu.data),
                'hissi' : int(form.ui_hissi.data),
                'sauna' : int(form.ui_sauna.data),
                'parveke' : int(form.ui_parveke.data),
                'tonttiala' : form.ui_tonttiala.data,
                'muu_kerrosala' : form.ui_muu_kerrosala.data,
                'created_on': dt.now().strftime('%d.%m.%Y %H:%M:%S'),
                'user':int(current_user.id),
                'query_id' : query_id
                }

            

            
            request_object.update({'apiKey': apiKey})
            #request_object =  {k: str(v).encode("utf-8") for k,v in request_object.items()}
            request_object = r.get(url = backend_url, params=request_object)
            request_data = request_object.json() 

            if request_object.status_code == 406:
                form.populate_obj(UserInput)
                flash(request_data['message'], request_data['Error'])
                print(request_data['message'])
                

                    

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
        item['7'] = convert_datetime_timezone(str(item['7'].strftime("%d.%m.%Y %H:%M:%S")), "UTC", "Europe/Helsinki")
        item['9'] = null_check(item['9'])
        

    # returns what is needed by DataTable
    # Sleep function added for first draw of data (enables loading animation to be seen)

    if params['draw'] == '1':
        sleep(2)
    return jsonify(rowTable.output_result())



def create_map(lat, lng, addr, price, level):

    customdata=np.stack(([addr, price]), axis=-1)
    
    if level == 'local':
        zoom = 11
        height = 450
        hovertemplate = False
        hovermode = False
    else:
        zoom = 10
        height = 600
        hovertemplate = "<b> %{customdata[0]} </b><br><br>" + \
                        "Hinta: %{customdata[1]}" + \
                        '<extra></extra>'
        hovermode = 'closest'

    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
            lat=lat,
            lon=lng,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=17,
                color='rgb(255, 0, 0)',
                opacity=0.7
            )
            
        ))

    fig.add_trace(go.Scattermapbox(
            lat=lat,
            lon=lng,
            customdata=customdata,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=8,
                color='rgb(242, 177, 172)',
                opacity=0.7
            ),
            hovertemplate = hovertemplate            
        ))

    fig.update_layout(
        autosize=True,
        height=height,
        hovermode=hovermode,
        hoverlabel_align = 'left',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            pitch=0,
            center=dict(
            lat=mean(lat),
            lon=mean(lng)
        ),
            zoom=zoom,
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
    addr_ = []
    price_ = []

    if query_id != 'all':
        query = db.session.query(UserInput).filter(text('user_input.query_id = :query_id')).params(query_id = query_id).first()
        lat = float(query.lat)
        lng = float(query.lng)
        lat_.append(lat)
        lng_.append(lng)
        level = 'local'
    else:
        query = db.session.query(UserInput).filter(text('user_input.user::integer = :user_id')).params(user_id = current_user.id).all()
        for row in query:
            if row.lat and row.lng:
                lat = float(row.lat)
                lng = float(row.lng)
                addr = row.osoite + ', ' + row.kunta
                price = format_currency(row.hinta, 'EUR', format=u'#,##0\xa0¤', locale='fi_FI', currency_digits=False)
                lat_.append(lat)
                lng_.append(lng)
                addr_.append(addr)
                price_.append(price)
                level = 'global'



    graphJSON= create_map(lat_, lng_, addr_, price_, level)




    return graphJSON


    # return render_template('map.html', maps=open(os.path.join(valuation_bp.root_path, valuation_bp.template_folder, "datatable_map.html")).read())


   
