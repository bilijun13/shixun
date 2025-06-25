from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.utils.auth import validate_user_input
from app.utils.cors_utils import build_cors_preflight_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = validate_user_input(data)
    if errors:
        return jsonify({"errors": errors}), 400

    result = AuthService.register_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    if result['success']:
        return jsonify({"message": "User registered successfully"}), 201
    else:
        return jsonify({"error": result['message']}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({"error": "Missing username/email or password"}), 400

    user = AuthService.authenticate_user(username_or_email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = AuthService.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200