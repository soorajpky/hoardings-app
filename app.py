import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from config import Config
from models import db, User, Hoarding
from forms import LoginForm, HoardingForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        if u and check_password_hash(u.password, form.password.data):
            login_user(u)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    place = request.args.get('place', '')
    showroom = request.args.get('showroom', '')
    location = request.args.get('location', '')
    query = Hoarding.query
    if place:
        query = query.filter(Hoarding.place.ilike(f"%{place}%"))
    if showroom:
        query = query.filter(Hoarding.showroom_name.ilike(f"%{showroom}%"))
    if location:
        query = query.filter(Hoarding.showroom_location.ilike(f"%{location}%"))
    hoardings = query.order_by(Hoarding.renewal_date).all()
    upcoming = datetime.now().date() + timedelta(days=30)
    return render_template("dashboard.html", hoardings=hoardings, upcoming=upcoming)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_hoarding():
    form = HoardingForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            fn = secure_filename(form.image.data.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            form.image.data.save(upload_path)
            filename = fn

        h = Hoarding(
            size=form.size.data,
            renewal_date=form.renewal_date.data,
            amount=form.amount.data,
            place=form.place.data,
            owner_name=form.owner_name.data,
            contact=form.contact.data,
            address=form.address.data,
            location_url=form.location_url.data,
            showroom_name=form.showroom_name.data,
            showroom_location=form.showroom_location.data,
            image_filename=filename,
            created_by=current_user.id
        )
        db.session.add(h)
        db.session.commit()
        flash("Hoarding added!", "success")
        return redirect(url_for('dashboard'))
    return render_template("hoarding_form.html", form=form, title="Add Hoarding")

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    h = Hoarding.query.get_or_404(id)
    if not (current_user.id == h.created_by or current_user.is_admin):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    form = HoardingForm(obj=h)
    if form.validate_on_submit():
        if form.image.data and allowed_file(form.image.data.filename):
            fn = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            h.image_filename = fn

        form.populate_obj(h)
        db.session.commit()
        flash("Hoarding updated.", "success")
        return redirect(url_for('dashboard'))
    return render_template("hoarding_form.html", form=form, title="Edit Hoarding")

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    h = Hoarding.query.get_or_404(id)
    if not current_user.is_admin:
        flash("Only admin can delete hoardings.", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(h)
    db.session.commit()
    flash("Hoarding deleted.", "success")
    return redirect(url_for('dashboard'))

@app.route('/hoardings')
@login_required
def hoardings():
    place = request.args.get('place', '')
    showroom = request.args.get('showroom', '')
    query = Hoarding.query
    if place:
        query = query.filter(Hoarding.place.ilike(f"%{place}%"))
    if showroom:
        query = query.filter(Hoarding.showroom_name.ilike(f"%{showroom}%"))
    all_h = query.order_by(Hoarding.renewal_date).all()
    return render_template("hoarding_list.html", hoardings=all_h)

@app.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    return render_template("users.html", users=User.query.all())

@app.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        if User.query.filter_by(email=email).first():
            flash("User already exists.", "warning")
        else:
            new_user = User(
                email=email,
                password=generate_password_hash(password),
                is_admin=is_admin
            )
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully.", "success")
            return redirect(url_for('users'))

    return render_template("create_user.html")

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

