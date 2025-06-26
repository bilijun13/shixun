from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, \
    create_refresh_token, set_refresh_cookies
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

    # 在生成令牌时包含用户名信息
    access_token = create_access_token(identity=str(user.id), additional_claims={'username': user.username})
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    })
    return response, 200


import os
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dotenv import load_dotenv, set_key

# 加载环境变量
load_dotenv()

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from dotenv import load_dotenv, set_key
import os
import json


@auth_bp.route('/center', methods=['GET', 'POST'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = AuthService.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == 'GET':
        return jsonify({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }), 200

    elif request.method == 'POST':
        try:
            # 解析JSON请求体
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON format"}), 400

            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')

            # 更新OpenAI API密钥
            if 'openai_api_key' in data and data['openai_api_key']:
                openai_api_key = data['openai_api_key']
                set_key(env_path, 'OPENAI_API_KEY', openai_api_key)

            # 更新通义千问API密钥
            if 'tongyi_api_key' in data and data['tongyi_api_key']:
                tongyi_api_key = data['tongyi_api_key']
                set_key(env_path, 'TONGYI_API_KEY', tongyi_api_key)

            # 重新加载环境变量
            load_dotenv(env_path)

            return jsonify({"message": "API keys updated successfully"}), 200

        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"}), 400
        except Exception as e:
            current_app.logger.error(f"Error in /auth/center: {str(e)}")
            return jsonify({"error": "Failed to process request"}), 422

@auth_bp.route('/refresh', methods=['POST', 'OPTIONS'])
def refresh_token():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    # 从请求头中获取刷新令牌（需前端在请求头中携带）
    @jwt_required(refresh=True)
    def _refresh():
        try:
            current_user = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user)

            return jsonify({
                "access_token": new_access_token,
                "msg": "Token refreshed"
            }), 200

        except Exception as e:
            return jsonify({"msg": "Refresh failed", "error": str(e)}), 401

    return _refresh()


def _build_cors_preflight_response():
    response = jsonify({"msg": "Preflight OK"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response
