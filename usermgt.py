# -*- coding: utf-8 -*-

""" This script can be used to manually update a user to the database
    TODO:   - Add a user delete command
            - Make argparse commands, so that cli can be used directly (e.g. from dockerized version)
            - Future user management should be done via a signup form etc..
"""

import argparse
from project import create_app, SQLAlchemy
app = create_app()
db = SQLAlchemy(app)

from project.models import db, User
from datetime import datetime as dt

# parser = argparse.ArgumentParser()
# parser.add_argument('-u', '--username', type=Str, required=True)
# parser.add_argument('-e', '--email', type=Str, required=True)
# parser.add_argument('-p', '--password', type=Str, required=True)




def user_exists(email, User):
    '''Queries the database and checks whether the given user exists'''

    existing_user = User.query.filter_by(email = email).all()

    if existing_user:
        return True
    else:
        return False




def add_user(name, email, password, User, db):
    """Create a user manually and update to existing database."""
    
    with app.app_context():

        if not user_exists(email, User):    

            new_user = User(
                name=name,
                email=email,
                created_on=dt.now()
                )
            new_user.set_password(password)
            db.session.add(new_user)  # Adds new User record to database
            db.session.commit()  # Commits all changes
            print(f"User {name} successfully created!")
        
        else:
            print(f"The email {email} already has a registered user!")

name = 'Oskari Honkasalo'
email = 'oskari.honkasalo@remax.fi'
password = 'Fay_2020!'

add_user(name, email, password, User, db)