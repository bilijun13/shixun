import json
import os
import sys
import uuid

import requests

from app.services.agent_service import AgentService
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

api_bp = Blueprint('api', __name__)
conversations = {}

# 加载.env文件中的环境变量
load_dotenv()

# 通义千问API配置
TONGYI_API_KEY = os.getenv("TONGYI_API_KEY")
TONGYI_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 检查API密钥是否存在
if not TONGYI_API_KEY:
    print("警告: 未找到通义千问API密钥，请设置TONGYI_API_KEY环境变量")


@api_bp.route('/start_chat', methods=['POST'])
def start_chat():
    session_id = str(uuid.uuid4())
    conversations[session_id] = []
    return jsonify({"session_id": session_id})


@api_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('session_id')
        user_input = data.get('input')

        if not all([session_id, user_input]):
            return jsonify({"error": "Missing required parameters"}), 400

        # 构建符合最新API规范的消息
        messages = [
            {"role": "system", "content": "你是一个专业的人工智能助手，用中文简洁回答"},
            {"role": "user", "content": user_input}
        ]

        payload = {
            "model": "qwen-turbo",
            "input": {
                "messages": messages
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.7,
                "top_p": 0.8
            }
        }

        # 修正后的请求头（移除无效字段）
        headers = {
            "Authorization": f"Bearer {TONGYI_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # 打印调试信息
        print(f"Final request payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        response = requests.post(
            TONGYI_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )

        # 增强错误处理
        if response.status_code != 200:
            error_detail = response.text
            print(f"API Error Details: {error_detail}")
            return jsonify({
                "error": "AI service error",
                "status_code": response.status_code,
                "detail": error_detail[:200]  # 截取部分错误信息
            }), 503

        result = response.json()
        print(f"Full API response: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # 安全提取回复
        assistant_response = result.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content",
                                                                                                     "无法生成回复")

        return jsonify({
            "response": assistant_response,
            "session_id": session_id
        })

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)[:200]
        }), 500

@api_bp.route('/execute/<int:agent_id>', methods=['POST'])
@jwt_required()
def execute_agent(agent_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    # 参数校验
    if not data or 'input' not in data:
        return jsonify({"error": "Missing input parameter"}), 400

    try:
        # 获取上下文ID（用于多轮对话）
        parent_execution_id = data.get('parent_execution_id')

        # 调用服务层
        ai_response, execution = AgentService.execute_agent(
            user_id=user_id,
            agent_id=agent_id,
            user_input=data['input'],
            parent_execution_id=parent_execution_id  # 传递上下文
        )

        return jsonify({
            "execution_id": execution.id,
            "output": ai_response,
            "status": execution.status,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404  # 资源未找到
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@api_bp.route('/execution/<int:execution_id>', methods=['GET'])
@jwt_required()
def get_execution(execution_id):
    user_id = get_jwt_identity()

    try:
        execution = AgentService.get_execution(user_id, execution_id)
        if not execution:
            raise ValueError("Execution not found")

        # 获取完整的对话历史链
        conversation_chain = AgentService.get_conversation_chain(execution_id)

        return jsonify({
            "current": execution.to_dict(),
            "history": [e.to_dict() for e in conversation_chain]
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500