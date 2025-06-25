from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies
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
    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }), 200


@auth_bp.route('/center', methods=['GET'])
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


@auth_bp.route('/refresh', methods=['POST', 'OPTIONS'])
def refresh_token():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()  # 确保返回预检响应

    # 只对 POST 请求进行 JWT 验证
    @jwt_required(refresh=True)
    def _refresh():
        try:
            current_user = get_jwt_identity()
            new_token = create_access_token(identity=current_user)

            response = jsonify({
                "access_token": new_token,
                "msg": "Token refreshed"
            })

            # 如果使用 Cookie 方案
            set_access_cookies(response, new_token)
            return response, 200

        except Exception as e:
            print(str(e))
            return jsonify({"msg": "Refresh failed", "error": str(e)}), 401

    return _refresh()  # 调用内部函数进行实际处理


def _build_cors_preflight_response():
    response = jsonify({"msg": "Preflight OK"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response
