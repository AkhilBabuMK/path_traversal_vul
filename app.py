
from flask import Flask, request, render_template, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-for-demo'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_DIR'] = os.path.join(os.getcwd(), 'uploads')  # Use relative path in current working directory
os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)  # Create uploads directory if it doesn't exist

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)  # Plaintext for demo; use hashing in production

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "Username already exists", 400
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_DIR'], filename)
            file.save(file_path)
            return "File uploaded successfully"
    return render_template('upload.html')

@app.route('/download')
def download():
    filename = request.args.get('file')
    if not filename:
        return "File name is required", 400
    file_path = os.path.join(app.config['UPLOAD_DIR'], filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path)

if __name__ == '__main__':
    # Create secret.txt in the parent directory of UPLOAD_DIR if it doesn't exist
    secret_file_path = os.path.join(os.getcwd(), 'secret.txt')
    if not os.path.exists(secret_file_path):
        with open(secret_file_path, 'w') as f:
            f.write("Top Secret Information\nDatabase Credentials: admin:supersecretpassword\nAPI Key: XYZ123456789")
    app.run(debug=True, host='0.0.0.0', port=5000)
