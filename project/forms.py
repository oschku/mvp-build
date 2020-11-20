# -*- coding: utf-8 -*-

"""Sign-up & log-in forms."""
from flask_wtf import FlaskForm
from wtforms import (StringField,
                    SubmitField, 
                    SelectField, 
                    IntegerField, 
                    DecimalField,
                    RadioField,
                    PasswordField)
from wtforms.validators import (DataRequired,
                                Email, 
                                EqualTo, 
                                Length, 
                                Optional, 
                                NumberRange,
                                InputRequired,
                                ValidationError,
                                Regexp)


class SignupForm(FlaskForm):
    """User Sign-up Form."""
    name = StringField(
        'Name',
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Select a stronger password.')
        ]
    )
    confirm = PasswordField(
        'Confirm Your Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    website = StringField(
        'Website',
        validators=[Optional()]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User Log-in Form."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Enter a valid email.')
        ]
    )
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


def num_range(min, max):
    message = 'Numeroiden on oltava %d ja %d välillä' % (min, max)

    def _num_range(form, field):
        l = field.data
        if l:
            if (l < min or l > max):
                raise ValidationError(message)

    return _num_range


class UiForm(FlaskForm):

    """ User input form for valuation """

    dec_filter = lambda x: x.replace(',', '.') if x else None
    
    ui_osoite = StringField('Osoite', [DataRequired()])
    ui_kunta = SelectField('Kunta', 
    choices=[('Helsinki', 'Helsinki'),
    ('Espoo','Espoo'),
    ('Vantaa', 'Vantaa')])
    ui_postinumero = StringField('Postinumero', [
        DataRequired(), Length(min=5, max=5, message = ('Postinumeron on oltava 5 merkkiä pitkä, esim. 00510')), Regexp('([0-9])\w+', message="Postinumeron täytyy sisältää vain numeroita")])
    ui_asuntotyyppi = SelectField('Asuntotyyppi', 
    choices=[('Kerrostalo', 'Kerrostalo'),
    ('Rivitalo', 'Rivitalo'),
    ('Omakotitalo', 'Omakotitalo'),
    ('Erillistalo', 'Erillistalo'),
    ('Pienkerrostalo', 'Pienkerrostalo'),
    ('Paritalo', 'Paritalo')
    ])
    ui_kunto = SelectField('Asunnon kunto', 
    choices=[('Uusi','Uusi'),
    ('Erinomainen', 'Erinomainen'),
    ('Hyvä', 'Hyvä'),
    ('Tyydyttävä', 'Tyydyttävä'),
    ('Huono', 'Huono'),
    ]) 
    ui_asuinala = DecimalField('Asuinala', [DataRequired(), num_range(min=5, max=500)])
    ui_rakennusvuosi = IntegerField('Rakennusvuosi', [DataRequired()], default = 2020)
    ui_huone_lkm = SelectField('Huoneiden lkm', 
    choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), 
    (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)
    ]) 
    ui_kerros = IntegerField('Kerros', [InputRequired(), num_range(min=0, max=35)])
    ui_kerros_yht = IntegerField('Kerroksia yhteensä', [DataRequired(), num_range(min=1, max=35)])
    ui_tontti = SelectField('Tontin omistusmuoto', 
    choices=[('Oma', 'Oma'),
    ('Vuokra', 'Vuokra'),
    ('Valinnainen vuokratontti', 'Valinnainen_vuokratontti')
    ])
    ui_vastike = IntegerField('Vastike', [DataRequired(), num_range(min=0, max=5000)])
    ui_vuokrattu = SelectField('Vuokrattu', 
    choices=[(0, 'Ei'),
    (1, 'Kyllä')]) 
    ui_hissi = SelectField('Hissi\u2800\u2800\u2800', 
    choices=[(0, 'Ei'),
    (1, 'Kyllä')]) 
    ui_sauna = SelectField('Sauna\u2800\u2800', 
    choices=[(0, 'Ei'),
    (1, 'Kyllä')]) 
    ui_parveke = SelectField('Parveke\u2800', 
    choices=[(0, 'Ei'),
    (1, 'Kyllä')]) 
    ui_tonttiala = IntegerField('Tonttiala', validators = [DataRequired(), num_range(min=0, max=50000)])
    ui_muu_kerrosala = IntegerField('Muu kerrosala', validators = [DataRequired(), num_range(min=0, max=500)])

    submit = SubmitField('Laske')