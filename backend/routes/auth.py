from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def sanitize(text):
    if not text:
        return ''
    return str(text).strip()[:200]

# Signup
@auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()

    name = sanitize(data.get('name'))
    email = sanitize(data.get('email', '')).lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    if len(name) < 2:
        return jsonify({'message': 'Name must be at least 2 characters'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Please enter a valid email'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201


# Login
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    email = sanitize(data.get('email', '')).lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and Password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }
    }), 200