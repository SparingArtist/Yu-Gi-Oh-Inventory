from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cards.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model for Admins
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Card Inventory Model
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Monster, Spell, Trap, etc.
    typing = db.Column(db.String(50), nullable=True)  # Monster type
    quantity = db.Column(db.Integer, default=1)
    image_url = db.Column(db.String(255), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page (Guest View)
@app.route('/')
def home():
    cards = Card.query.all()
    return render_template('index.html', cards=cards)

# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

# Admin Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    cards = Card.query.all()
    return render_template('dashboard.html', cards=cards)

# Add Card to Inventory
@app.route('/add_card', methods=['POST'])
@login_required
def add_card():
    name = request.form['name']
    category = request.form['category']
    typing = request.form.get('typing', '')
    quantity = int(request.form['quantity'])
    
    # Fetch card image from YGOPRODeck API
    api_url = f'https://db.ygoprodeck.com/api/v7/cardinfo.php?name={name}'
    response = requests.get(api_url)
    image_url = None
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            image_url = data['data'][0]['card_images'][0]['image_url']

    new_card = Card(name=name, category=category, typing=typing, quantity=quantity, image_url=image_url)
    db.session.add(new_card)
    db.session.commit()
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Run Server
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
