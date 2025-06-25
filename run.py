from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

from app import create_app
from config import Config

app = create_app(Config)

# 全局CORS配置 - 统一处理所有路由
CORS(app,
     resources={
         r"/*": {
             "origins": "http://localhost:5173",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 600
         }
     })


# 处理 /Auth/login 路由
@app.route('/Auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', "http://localhost:5173")
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response

    # 处理实际登录请求
    data = request.json
    # 这里添加实际的登录验证逻辑
    # 示例返回
    return jsonify({"token": "example-token", "message": "Login successful"}), 200



# 处理重定向后的新路径
@app.route('/new-agents-path', methods=['GET', 'POST', 'PUT', 'DELETE'])
def new_agents_path():
    if request.method == 'GET':
        return jsonify({"message": "This is the new agents endpoint"}), 200

    # 其他方法处理...
    return jsonify({"message": "Method not allowed"}), 405


# 统一添加 OPTIONS 方法处理
@app.route('/api/agents', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def agents():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    if request.method == 'GET':
        return jsonify({"message": "Fetching agents", "data": []}), 200
    elif request.method == 'POST':
        data = request.get_json()
        return jsonify({"message": "Agent created", "data": data}), 201
    else:
        return jsonify({"message": "Method not allowed"}), 405


# 预检请求响应构建
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5000)