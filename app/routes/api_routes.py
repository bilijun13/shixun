from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.agent_service import AgentService
import time

api_bp = Blueprint('api', __name__)


@api_bp.route('/execute/<int:agent_id>', methods=['POST'])
@jwt_required()
def execute_agent(agent_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if 'input' not in data:
        return jsonify({"error": "Missing input"}), 400

    try:
        # 调用真实服务
        ai_response, execution = AgentService.execute_agent(
            user_id=user_id,
            agent_id=agent_id,
            user_input=data['input']
        )

        return jsonify({
            "execution_id": execution.id,
            "output": ai_response,  # 真实AI响应
            "status": execution.status
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/execution/<int:execution_id>', methods=['GET'])
@jwt_required()
def get_execution(execution_id):
    user_id = get_jwt_identity()
    execution = AgentService.get_execution(user_id, execution_id)

    if not execution:
        return jsonify({"error": "Execution not found or access denied"}), 404

    return jsonify(execution.to_dict()), 200