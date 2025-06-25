import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from app import create_app
from config import Config

app = create_app(Config)
allowed_origins = [
    "http://localhost:5173",
    os.getenv("PRODUCTION_FRONTEND_URL", "")
]
# 配置CORS，支持凭证和特定来源
CORS(app,
     origins=["http://localhost:5173"],
     supports_credentials=True,  # 必须为 True
     expose_headers=["Content-Type","Authorization"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS","PUT", "DELETE"]
     )

app.url_map.strict_slashes = False

# 处理 /Auth/login 路由
@app.route('/Auth/login', methods=['POST'])
def login():
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)