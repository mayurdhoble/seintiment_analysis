from flask import Flask, request, render_template, redirect, url_for, jsonify, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import joblib
from joblib import load
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Define base directory for the application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths for model, vectorizer, and database
MODEL_PATH = os.path.join(BASE_DIR, "clf.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
DATABASE_PATH = os.path.join(BASE_DIR, "users.db")

# Load the pre-trained model and vectorizer
model = load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, name, email, password_hash, created_at, is_active=True):
        self._id = id
        self._name = name
        self._email = email
        self._password_hash = password_hash
        self._created_at = created_at
        self._is_active = is_active

    # Properties with getters and setters
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def email(self):
        return self._email

    @property
    def password_hash(self):
        return self._password_hash
    
    @password_hash.setter
    def password_hash(self, value):
        self._password_hash = value

    @property
    def created_at(self):
        return self._created_at

    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self._id)

# Database functions
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cur.fetchone()
    conn.close()
    
    if user_data:
        return User(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            created_at=user_data['created_at'],
            is_active=user_data['is_active']
        )
    return None

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        review = request.form['review']
        # Preprocess the text
        text_data = [review.lower()]  # Apply any additional preprocessing if needed
        
        # Transform the input text using the vectorizer
        text_data_transformed = vectorizer.transform(text_data)
        
        # Make prediction
        prediction = model.predict(text_data_transformed)
        result = 'Positive' if prediction[0] == 1 else 'Negative'
        
        # Return JSON response
        return jsonify({
            'prediction': result,
            'status': 'success'
        })

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        if not all([name, email, password, confirm_password]):
            flash('Please fill all fields', 'error')
            return redirect(url_for('signup'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
            
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cur.fetchone():
            conn.close()
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
            
        try:
            password_hash = generate_password_hash(password)
            cur.execute('''
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            ''', (name, email, password_hash))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            conn.close()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = cur.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                created_at=user_data['created_at'],
                is_active=True
            )
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        conn = get_db()
        cur = conn.cursor()
        
        try:
            if name and name != current_user.name:
                cur.execute('UPDATE users SET name = ? WHERE id = ?',
                          (name, current_user.id))
                current_user.name = name
            
            if current_password and new_password:
                if current_user.check_password(current_password):
                    new_hash = generate_password_hash(new_password)
                    cur.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                              (new_hash, current_user.id))
                    current_user.password_hash = new_hash
                    flash('Password updated successfully', 'success')
                else:
                    flash('Current password is incorrect', 'error')
            
            conn.commit()
            if name and name != current_user.name:
                flash('Profile updated successfully', 'success')
        except Exception as e:
            conn.rollback()
            flash('An error occurred', 'error')
        finally:
            conn.close()
            
    return render_template('profile.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not all([name, email, subject, message]):
            flash('Please fill all fields', 'error')
            return redirect(url_for('contact'))
            
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO contacts (name, email, subject, message)
                VALUES (?, ?, ?, ?)
            ''', (name, email, subject, message))
            conn.commit()
            conn.close()
            
            flash('Message sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('contact'))
            
    return render_template('contact.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

# Create database tables if they don't exist
def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    # Create users table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Create contacts table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize database
    init_db()
    app.run(debug=True)