from flask import Flask, request, render_template, redirect, url_for, flash, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, SignUp, Profile, ApartmentBuilding, Apartment
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key' # set a secret key for flash messages

# Create a connection to the Postgres database
engine = create_engine("postgresql://postgres:arrange@localhost:5432/example")

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Define regular expression patterns for validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
ZIP_REGEX = re.compile(r'^\d{5}$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        # Get signup data from request body
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate required fields
        if not username or not email or not password:
            flash('Missing required fields', 'error')
            return redirect(url_for('signup'))

        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format', 'error')
            return redirect(url_for('signup'))

        # Check if username already exists in the database
        if session.query(SignUp).filter(SignUp.username == username).first():
            flash('Username already exists. Please choose another username.', 'error')
            return redirect(url_for('signup'))

        # Check if email already exists in the database
        if session.query(SignUp).filter(SignUp.email == email).first():
            flash('Email already exists. Please use another email.', 'error')
            return redirect(url_for('signup'))

        # Create SignUp instance and add to session
        signup = SignUp(username=username, email=email, password=password)
        session.add(signup)
        session.commit()

        flash('Signup successful', 'success')
        return render_template('login.html')
    else:
        # If the request method is GET, render the signup.html template
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get login data from request body
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate required fields
        if not email or not password:
            flash('Missing required fields', 'error')
            return redirect(url_for('login'))

        # Check if a matching SignUp instance exists in the database
        signup = session.query(SignUp).filter(SignUp.email == email, SignUp.password == password).first()

        # If no matching SignUp instance is found, redirect to the login page with an error message
        if not signup:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))

        # If a matching SignUp instance is found, redirect to the profile page
        return redirect(url_for('home'))

    # If the request method is GET, render the login.html template
    return render_template('login.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        # Get profile data from request form
        signup_id = request.form.get('signup_id')
        image_data = request.files['image_data'].read()

        # Validate required fields
        if not signup_id or not image_data:
            flash('Missing required fields', 'error')
            return redirect(url_for('profile'))

        # Create Profile instance and add to session
        profile = Profile(signup_id=signup_id, image=image_data)
        session.add(profile)
        session.commit()

        flash('Profile added', 'success')
        return redirect(url_for('profile'))
    else:
        return render_template('profile.html')

@app.route('/building', methods=['POST'])
def building():
    # Get building data from request body
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zip')

    # Validate required fields
    if not name or not address or not city or not state or not zip_code:
        flash('Missing required fields', 'error')
        return redirect(url_for('building_form'))

    # Validate zip code format
    if not re.match(ZIP_REGEX, zip_code):
        flash('Invalid zip code format', 'error')
        return redirect(url_for('building_form'))

    # Create ApartmentBuilding instance and add to session
    building = ApartmentBuilding(name=name, address=address, city=city, state=state, zip=zip_code)
    session.add(building)
    session.commit()

    flash('Building added', 'success')
    return redirect(url_for('home'))


@app.route('/apartment', methods=['POST'])
def apartment():
    # Get apartment data from
    data = request.get_json()
    building_id = data.get('building_id')
    number = data.get('number')
    rent = data.get('rent')
    bedrooms = data.get('bedrooms')
    bathrooms = data.get('bathrooms')

    # Validate required fields
    if not building_id or not number or not rent or not bedrooms or not bathrooms:
        flash('Missing required fields', 'error')
        return redirect(url_for('apartment_form'))

    # Create Apartment instance and add to session
    apartment = Apartment(building_id=building_id, number=number, rent=rent, bedrooms=bedrooms, bathrooms=bathrooms)
    session.add(apartment)
    session.commit()

    flash('Apartment added', 'success')
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    # Redirect to home page
    return render_template('index.html')

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True)