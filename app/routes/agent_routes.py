from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import TongyiService
from app.models import Agent, AgentExecution
from app.services.agent_service import AgentService
from app.utils.cors_utils import build_cors_preflight_response

agent_bp = Blueprint('agents', __name__)
CORS(agent_bp,
     origins=["http://localhost:5173"],
     supports_credentials=True,
     expose_headers=["Content-Type", "Authorization"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
     )

# 示例：处理连续对话的路由
@agent_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    agent_id = data['agent_id']
    user_input = data['input']
    session_id = data.get('session_id')  # 关键：客户端需传递会话ID

    agent = Agent.query.get(agent_id)

    # 获取或创建执行记录链
    if session_id:
        parent_exec = AgentExecution.query.get(session_id)
        if not parent_exec:
            return jsonify({"error": "Invalid session_id"}), 400
    else:
        parent_exec = None

    # 调用服务
    response, execution = TongyiService.generate_response(
        agent=agent,
        user_input=user_input,
        execution_id=parent_exec.id if parent_exec else None  # 关键参数
    )

    return jsonify({
        "response": response,
        "session_id": execution.id  # 返回新session_id供下次使用
    })

@agent_bp.route('/', methods=['POST'])
@jwt_required()
def create_agent():
    user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ['name', 'system_prompt']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    agent = AgentService.create_agent(
        user_id=user_id,
        name=data['name'],
        system_prompt=data['system_prompt'],
        description=data.get('description', ''),
        model=data.get('model', 'qwen-turbo'),
        temperature=data.get('temperature', 0.7),
        max_tokens=data.get('max_tokens', 1000),
        is_public=data.get('is_public', False)
    )

    return jsonify(agent.to_dict()), 201

@agent_bp.route('', methods=['GET'])
@agent_bp.route('/', methods=['GET'])
@jwt_required()
def list_agents():
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()
    user_id = get_jwt_identity()
    public = request.args.get('public', '').lower() == 'true'

    agents = AgentService.list_agents(user_id, public)
    return jsonify([agent.to_dict() for agent in agents]), 200


@agent_bp.route('/<int:agent_id>', methods=['GET'])
@jwt_required()
def get_agent(agent_id):
    user_id = get_jwt_identity()
    agent = AgentService.get_agent(user_id, agent_id)

    if not agent:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify(agent.to_dict()), 200


@agent_bp.route('/<int:agent_id>', methods=['PUT'])
@jwt_required()
def update_agent(agent_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    agent = AgentService.update_agent(
        user_id=user_id,
        agent_id=agent_id,
        update_data=data
    )

    if not agent:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify(agent.to_dict()), 200


@agent_bp.route('/<int:agent_id>', methods=['DELETE'])
@jwt_required()
def delete_agent(agent_id):
    user_id = get_jwt_identity()
    success = AgentService.delete_agent(user_id, agent_id)

    if not success:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify({"message": "Agent deleted successfully"}), 200


@agent_bp.route('/<int:agent_id>/executions', methods=['GET'])
@jwt_required()
def list_agent_executions(agent_id):
    user_id = get_jwt_identity()
    executions = AgentService.list_agent_executions(user_id, agent_id)

    if executions is None:
        return jsonify({"error": "Agent not found or access denied"}), 404

    return jsonify([execution.to_dict() for execution in executions]), 200


@agent_bp.route('/<int:agent_id>/execute', methods=['POST'])
@jwt_required()
def execute_agent(agent_id):
    """执行Agent对话"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'input' not in data:
        return jsonify({"error": "Missing input"}), 400

    parent_execution_id = data.get('parent_execution_id')

    try:
        response_text, execution = AgentService.execute_agent(
            user_id=user_id,
            agent_id=agent_id,
            user_input=data['input'],
            parent_execution_id=parent_execution_id
        )

        return jsonify({
            "success": True,
            "output": response_text,
            "execution_id": execution.id,  # 确保返回 execution.id
            "status": execution.status
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



@agent_bp.route('/models', methods=['GET'])
@jwt_required()
def list_available_models():
    """获取可用的通义模型列表"""
    return jsonify({
        "models": [
            {"id": "qwen-turbo", "name": "通义千问Turbo"},
            {"id": "qwen-plus", "name": "通义千问Plus"},
            {"id": "qwen-max", "name": "通义千问Max"},
            {"id": "qwen-1.8b", "name": "通义千问1.8B"}
        ]
    }), 200