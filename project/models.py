# -*- coding: utf-8 -*-

"""Database models."""
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
	"""User account model."""

	__tablename__ = 'flasklogin-users'
	id = db.Column(
		db.Integer,
		primary_key=True
	)
	name = db.Column(
		db.String(100),
		nullable=False,
		unique=False
	)
	email = db.Column(
		db.String(40),
		unique=True,
		nullable=False
	)
	password = db.Column(
		db.String(200),
		primary_key=False,
		unique=False,
		nullable=False
	)
	website = db.Column(
		db.String(60),
		index=False,
		unique=False,
		nullable=True
	)
	created_on = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
	last_login = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )

	def set_password(self, password):
		"""Create hashed password."""
		self.password = generate_password_hash(password, method='sha256')

	def check_password(self, password):
		"""Check hashed password."""
		return check_password_hash(self.password, password)

	def __repr__(self):
		return '<User {}>'.format(self.name)


class UserInput(db.Model):
	__tablename__ = 'user_input'
	id = db.Column(db.Integer, primary_key = True)
	osoite = db.Column(db.String(50), nullable = False)
	kunta = db.Column(db.String(50), nullable = False)
	postinumero = db.Column(db.String(5), nullable = False)
	asuntotyyppi = db.Column(db.String(20), nullable = False)
	asuinala = db.Column(db.Float, nullable = False)
	rakennusvuosi = db.Column(db.Integer, nullable = False)
	huone_lkm = db.Column(db.Integer, nullable=False)
	kerros = db.Column(db.Integer, nullable=False)
	kerros_yht = db.Column(db.Integer, nullable=False)
	kunto = db.Column(db.String, nullable=False)
	tontti = db.Column(db.String, nullable = False)
	vastike = db.Column(db.Float, nullable = False)
	vuokrattu = db.Column(db.Integer, nullable=False)
	hissi = db.Column(db.Integer, nullable=False)
	sauna = db.Column(db.Integer, nullable=False)
	parveke = db.Column(db.Integer, nullable=False)
	tonttiala = db.Column(db.Float, nullable = True)
	muu_kerrosala = db.Column(db.Float, nullable = True)
	created_on = db.Column(db.DateTime, index=False, unique=False, nullable=True)
	user = db.Column(db.String, nullable = False)
	query_id = db.Column(db.String(10), nullable=False)
	hinta = db.Column(db.Numeric, nullable=True)
	


	@property
	def serialized(self):
		return {'id': self.id}
