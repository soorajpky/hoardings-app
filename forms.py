from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField, SelectField
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
    
    showroom_name     = SelectField("Showroom Name", choices=[
        ("Rajakumari Gold and Diamonds", "Rajakumari Gold and Diamonds"),
        ("Rajakumari Silks and Designs", "Rajakumari Silks and Designs"),
        ("Rajakumari Hypermarket", "Rajakumari Hypermarket")
    ], validators=[DataRequired()])

    showroom_location = SelectField("Showroom Location", choices=[
        ("Trivandrum", "Trivandrum"),
        ("Kaliyikavila", "Kaliyikavila"),
        ("Attingal", "Attingal"),
        ("Kallambalam", "Kallambalam"),
        ("Pothencode", "Pothencode"),
        ("Kattakada", "Kattakada"),
        ("Paripally", "Paripally"),
        ("Kottiyam", "Kottiyam"),
        ("Trissur", "Trissur")
    ], validators=[DataRequired()])

    image             = FileField("Hoarding Image", validators=[FileAllowed(['jpg','png','jpeg','gif'])])
    submit            = SubmitField("Save")
