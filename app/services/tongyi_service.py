import dashscope
from dashscope import Generation
from datetime import datetime
from app.extensions import db
from app.models import AgentExecution


class TongyiService:
    @staticmethod
    def initialize(api_key):
        """初始化通义API"""
        dashscope.api_key = api_key

    @staticmethod
    def generate_response(agent, user_input, execution_id=None):
        """
        调用通义大模型生成响应
        :param agent: Agent对象
        :param user_input: 用户输入
        :param execution_id: 可选的执行ID（用于更新现有记录）
        :return: (response_text, execution)
        """
        full_prompt = f"{agent.system_prompt}\n\n用户输入: {user_input}"

        try:
            # 创建或获取执行记录
            if execution_id:
                execution = AgentExecution.query.get(execution_id)
                if not execution:
                    raise ValueError("Execution not found")
            else:
                execution = AgentExecution(
                    agent_id=agent.id,
                    user_id=agent.user_id,
                    input=user_input,
                    status='processing'
                )
                db.session.add(execution)
                db.session.commit()

            # 调用通义API
            response = Generation.call(
                model=agent.model,
                prompt=full_prompt,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens
            )

            # 更新执行记录
            execution.output = response.output.text
            execution.status = 'completed'
            execution.end_time = datetime.utcnow()
            db.session.commit()

            return response.output.text, execution

        except Exception as e:
            if execution:
                execution.status = 'failed'
                execution.output = str(e)
                execution.end_time = datetime.utcnow()
                db.session.commit()
            raise e