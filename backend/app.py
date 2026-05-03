from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'Vivek@2026SecretKey'

# Initialize extensions
db.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
JWTManager(app)

# Register routes
from routes.auth import auth_bp
from routes.projects import projects_bp
from routes.tasks import tasks_bp

app.register_blueprint(auth_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(tasks_bp)

# Create all tables
with app.app_context():
    db.create_all()

# Serve frontend pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/project')
def project():
    return render_template('project.html')

if __name__ == '__main__':
    app.run(debug=True)