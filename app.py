# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import cv2
import numpy as np
import base64
from emotion_detector import detect_emotion

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Replace with a secure random key

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Music recommendations
music_recommendations = {
    "happy": "https://www.youtube.com/watch?v=ZbZSe6N_BXs",
    "sad": "https://www.youtube.com/watch?v=zQO7J483Dng&list=RDzQO7J483Dng&start_radio=1&pp=ygURc2FkIHNvbmdzIGVuZ2xpc2igBwE%3D",
    "angry": "https://www.youtube.com/watch?v=FDIgln1YSdA&list=RDFDIgln1YSdA&start_radio=1&pp=ygUKYW5ncnkgc29uZ6AHAQ%3D%3D",
    "neutral": "https://www.youtube.com/watch?v=Y2uDpiHRz2Q&list=RDY2uDpiHRz2Q&start_radio=1",
    "unknown": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

# Routes
@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode('utf-8')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password, user.password.encode('utf-8')):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode('utf-8')
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
        else:
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful! Please log in.")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # your logic to check user and send email
        flash("If the email is registered, a reset link has been sent.")
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route("/detect", methods=["POST"])
@login_required
def detect():
    image_data = request.json["image"]
    nparr = np.frombuffer(base64.b64decode(image_data.split(",")[1]), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    emotion = detect_emotion(image)
    music_url = music_recommendations.get(emotion, music_recommendations["unknown"])
    return jsonify({"emotion": emotion, "music_url": music_url})

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)