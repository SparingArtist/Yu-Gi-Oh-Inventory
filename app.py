from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__, template_folder="templates")

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cards.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the database
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
    desc = db.Column(db.Text, nullable=True)
    attack = db.Column(db.Integer, nullable=True)
    defense = db.Column(db.Integer, nullable=True)
    level = db.Column(db.Integer, nullable=True)
    race = db.Column(db.String(50), nullable=True)
    attribute = db.Column(db.String(50), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to load cards from Excel file
def load_cards_from_excel():
    file_path = "updated_cards.xlsx"
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            name = row["Name"]
            
            # Check if card already exists in database
            existing_card = Card.query.filter_by(name=name).first()
            if existing_card:
                continue  # Skip if already in database

            new_card = Card(
                name=name,
                category=row.get("Category", "Unknown"),
                typing=row.get("Typing", "N/A"),
                quantity=row.get("Quantity", 1),
                image_url=row.get("Image URL", None),
                desc=row.get("Description", ""),
                attack=row.get("Attack"),
                defense=row.get("Defense"),
                level=row.get("Level"),
                race=row.get("Race"),
                attribute=row.get("Attribute")
            )
            db.session.add(new_card)

        db.session.commit()
        print("✅ Cards loaded from updated_cards.xlsx")
    else:
        print("⚠ Excel file not found. No cards loaded.")

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

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Run Server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables exist
        load_cards_from_excel()  # Load cards from Excel on startup
    app.run(debug=True)
