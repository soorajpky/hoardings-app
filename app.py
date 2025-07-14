import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from collections import Counter

from config import Config
from models import db, User, Hoarding
from forms import LoginForm, HoardingForm

# ✅ Detect if running locally (for static path logic)
IS_LOCAL = os.environ.get('FLASK_ENV') == 'development'

# ✅ Correct static path for local vs Nginx reverse proxy (server)
app = Flask(__name__,
            static_url_path='/static' if IS_LOCAL else '/hoardings/static',
            static_folder='static')

app.config.from_object(Config)
db.init_app(app)

# ✅ Login manager
login_manager = LoginManager(app)
login_manager.login_view = 'hoarding_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Allowed image file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ✅ Redirect root to login
@app.route('/')
def home_redirect():
    return redirect(url_for('hoarding_login'))

# ✅ Login route
@app.route('/hoarding/login', methods=['GET', 'POST'])
def hoarding_login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        if u and check_password_hash(u.password, form.password.data):
            login_user(u)
            return redirect(url_for('hoarding_dashboard'))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

# ✅ Logout
@app.route('/hoarding/logout')
@login_required
def hoarding_logout():
    logout_user()
    return redirect(url_for('hoarding_login'))

# ✅ Dashboard
@app.route('/hoarding/dashboard')
@login_required
def hoarding_dashboard():
    place_filter = request.args.get('place', '')
    showroom_filter = request.args.get('showroom', '')

    query = Hoarding.query
    if place_filter:
        query = query.filter(Hoarding.place == place_filter)
    if showroom_filter:
        query = query.filter(Hoarding.showroom_name == showroom_filter)

    hoardings = query.order_by(Hoarding.renewal_date).all()
    places = sorted(set(h.place for h in Hoarding.query.all()))
    showrooms = sorted(set(h.showroom_name for h in Hoarding.query.all()))
    chart_data = Counter(h.showroom_name for h in Hoarding.query.all())

    labels = list(chart_data.keys())
    values = list(chart_data.values())

    upcoming = datetime.now().date() + timedelta(days=30)
    total_hoardings = Hoarding.query.count()
    upcoming_renewals = Hoarding.query.filter(Hoarding.renewal_date <= upcoming).count()

    return render_template("dashboard.html",
                           hoardings=hoardings,
                           upcoming=upcoming,
                           places=places,
                           showrooms=showrooms,
                           selected_place=place_filter,
                           selected_showroom=showroom_filter,
                           labels=labels,
                           values=values,
                           total_hoardings=total_hoardings,
                           upcoming_renewals=upcoming_renewals)

# ✅ Add hoarding
@app.route('/hoarding/add', methods=['GET', 'POST'])
@login_required
def hoarding_add():
    form = HoardingForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            fn = secure_filename(form.image.data.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            form.image.data.save(save_path)
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
        return redirect(url_for('hoarding_dashboard'))
    return render_template("hoarding_form.html", form=form)

# ✅ Edit hoarding
@app.route('/hoarding/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def hoarding_edit(id):
    h = Hoarding.query.get_or_404(id)
    if not (current_user.id == h.created_by or current_user.is_admin):
        flash("Access denied.", "danger")
        return redirect(url_for('hoarding_dashboard'))

    form = HoardingForm(obj=h)
    if form.validate_on_submit():
        if form.image.data and allowed_file(form.image.data.filename):
            fn = secure_filename(form.image.data.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            form.image.data.save(save_path)
            h.image_filename = fn

        form.populate_obj(h)
        db.session.commit()
        flash("Hoarding updated.", "success")
        return redirect(url_for('hoarding_dashboard'))

    return render_template("hoarding_form.html", form=form, title="Edit Hoarding")

# ✅ Delete hoarding
@app.route('/hoarding/delete/<int:id>')
@login_required
def hoarding_delete(id):
    h = Hoarding.query.get_or_404(id)
    if not current_user.is_admin:
        flash("Only admin can delete hoardings.", "danger")
        return redirect(url_for('hoarding_dashboard'))

    db.session.delete(h)
    db.session.commit()
    flash("Hoarding deleted.", "success")
    return redirect(url_for('hoarding_dashboard'))

# ✅ Create user
@app.route('/hoarding/create-user', methods=['GET', 'POST'])
@login_required
def hoarding_create_user():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('hoarding_dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        if User.query.filter_by(email=email).first():
            flash("User already exists!", "warning")
        else:
            new_user = User(email=email,
                            password=generate_password_hash(password),
                            is_admin=is_admin)
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully!", "success")
            return redirect(url_for('hoarding_dashboard'))

    return render_template("create_user.html")

# ✅ Run
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=8080, debug=True)



