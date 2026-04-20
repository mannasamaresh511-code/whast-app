import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(300), default="Hey there! I am using this app.")
    profile_pic = db.Column(db.String(100), default="default.png")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(500), nullable=False)

# Initialize DB
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')

        if action == 'signup':
            if User.query.filter_by(username=username).first():
                flash("Username already exists!")
            else:
                hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
                new_user = User(username=username, password=hashed_pw)
                db.session.add(new_user)
                db.session.commit()
                flash("Signup successful! Please login.")
        
        elif action == 'login':
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials.")

    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    current_user = db.session.get(User, session['user_id'])
    
    # Search functionality
    search_query = request.args.get('search')
    users = []
    if search_query:
        users = User.query.filter(User.username.contains(search_query)).all()

    # Messaging logic
    active_chat = request.args.get('chat_with')
    messages = []
    if active_chat:
        chat_user = User.query.filter_by(username=active_chat).first()
        if chat_user:
            messages = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == chat_user.id)) |
                ((Message.sender_id == chat_user.id) & (Message.receiver_id == current_user.id))
            ).all()

    if request.method == 'POST':
        content = request.form.get('content')
        receiver_name = request.form.get('receiver')
        receiver = User.query.filter_by(username=receiver_name).first()
        if receiver and content:
            new_msg = Message(sender_id=current_user.id, receiver_id=receiver.id, content=content)
            db.session.add(new_msg)
            db.session.commit()
            return redirect(url_for('dashboard', chat_with=receiver_name))

    return render_template('dashboard.html', current_user=current_user, users=users, active_chat=active_chat, messages=messages)

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    if 'user_id' not in session: return redirect(url_for('index'))
    current_user = db.session.get(User, session['user_id'])
    user_profile = User.query.filter_by(username=username).first_or_404()

    if request.method == 'POST' and current_user.id == user_profile.id:
        user_profile.bio = request.form.get('bio')
        pic = request.files.get('profile_pic')
        if pic:
            filename = secure_filename(pic.filename)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user_profile.profile_pic = filename
        db.session.commit()
        return redirect(url_for('profile', username=username))

    return render_template('profile.html', user=user_profile, is_owner=(current_user.id == user_profile.id))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)