from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Hoarding(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    size              = db.Column(db.String(50))
    renewal_date      = db.Column(db.Date)
    amount            = db.Column(db.Float)
    place             = db.Column(db.String(100))
    owner_name        = db.Column(db.String(100))
    contact           = db.Column(db.String(20))
    address           = db.Column(db.String(200))
    location_url      = db.Column(db.String(300))
    showroom_name     = db.Column(db.String(100))
    showroom_location = db.Column(db.String(100))
    image_filename    = db.Column(db.String(300))
    created_by        = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='hoardings')

