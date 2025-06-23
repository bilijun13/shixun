from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.agent_service import AgentService
from datetime import datetime

api_bp = Blueprint('api', __name__)


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