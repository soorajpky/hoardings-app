from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email    = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit   = SubmitField("Login")

class HoardingForm(FlaskForm):
    size              = StringField("Size", validators=[DataRequired()])
    renewal_date      = DateField("Renewal Date", validators=[DataRequired()])
    amount            = FloatField("Amount", validators=[DataRequired()])
    place             = StringField("Place", validators=[DataRequired()])
    owner_name        = StringField("Owner's Name", validators=[DataRequired()])
    contact           = StringField("Contact No.", validators=[DataRequired()])
    address           = StringField("Address", validators=[DataRequired()])
    location_url      = StringField("Google Maps URL", validators=[DataRequired()])
    showroom_name     = StringField("Showroom Name")  # used via request.form
    showroom_location = StringField("Showroom Location")  # used via request.form
    image             = FileField("Hoarding Image", validators=[
                          FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
                      ])
    submit            = SubmitField("Save")
