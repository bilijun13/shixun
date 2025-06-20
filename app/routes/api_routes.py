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

    # 创建执行记录
    execution = AgentService.create_execution(
        user_id=user_id,
        agent_id=agent_id,
        input_text=data['input']
    )

    if not execution:
        return jsonify({"error": "Agent not found or access denied"}), 404

    # 模拟执行过程（实际应用中这里会调用真正的AI模型）
    AgentService.update_execution_status(execution.id, 'running')

    # 模拟处理时间
    time.sleep(2)

    # 模拟生成输出
    output = f"Processed input: {data['input']}. This is a simulated response from agent {agent_id}."

    # 更新执行结果
    execution = AgentService.complete_execution(
        execution_id=execution.id,
        output=output
    )

    return jsonify({
        "execution_id": execution.id,
        "status": execution.status,
        "output": execution.output
    }), 200


@api_bp.route('/execution/<int:execution_id>', methods=['GET'])
@jwt_required()
def get_execution(execution_id):
    user_id = get_jwt_identity()
    execution = AgentService.get_execution(user_id, execution_id)

    if not execution:
        return jsonify({"error": "Execution not found or access denied"}), 404

    return jsonify(execution.to_dict()), 200