import dashscope
from dashscope import Generation
from datetime import datetime
from app.extensions import db
from app.models import AgentExecution, Agent
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Message:
    """符合dashscope要求的消息类型"""
    role: str  # 只能是 'system'/'user'/'assistant'
    content: str


class TongyiService:
    @staticmethod
    def initialize(api_key, base_url=None):
        """初始化通义API配置"""
        dashscope.api_key = api_key
        if base_url:
            dashscope.base_url = base_url

    @staticmethod
    def generate_response(
            agent: Agent,
            user_input: str,
            execution_id: Optional[int] = None,
            history_messages: Optional[List[Message]] = None,
            max_history_turns: int = 3
    ):
        """增强版多轮对话支持（类型安全版本）"""
        messages = []
        execution = None
        try:
            # 初始化消息列表（系统提示）
            messages = TongyiService.generate_context_messages(agent, user_input, execution_id, history_messages, max_history_turns)

            # 创建执行记录
            execution = TongyiService.create_execution_record(agent, user_input, execution_id)
            db.session.add(execution)
            db.session.flush()

            # 调用大模型接口
            dashscope_messages = TongyiService.convert_messages_to_dashscope_format(messages)
            response = TongyiService.call_model_api(agent, dashscope_messages)

            ai_response = response.output.text

            # 更新执行记录
            TongyiService.update_execution_record(execution, ai_response)

            db.session.commit()
            return ai_response

        except Exception as e:
            db.session.rollback()
            if 'execution' in locals():
                execution.status = 'failed'
                execution.output = str(e)
                db.session.commit()
            raise
    @staticmethod
    def generate_context_messages(
            agent: Agent,
            user_input: str,
            execution_id: Optional[int],
            history_messages: Optional[List[Message]],
            max_history_turns: int
    ) -> List[Message]:
        messages = [Message(role="system", content=agent.system_prompt)]

        if history_messages:
            messages.extend(history_messages)
        elif execution_id:
            history = TongyiService._get_conversation_history(execution_id, max_turns=max_history_turns)
            messages.extend(history)

        messages.append(Message(role="user", content=user_input))
        return messages
    @staticmethod
    def create_execution_record(agent: Agent, user_input: str, execution_id: Optional[int]) -> AgentExecution:
        return AgentExecution(
            agent_id=agent.id,
            user_id=agent.user_id,
            input=user_input,
            status='processing',
            parent_execution_id=execution_id
        )
    @staticmethod
    def convert_messages_to_dashscope_format(messages: List[Message]) -> List[dict]:
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    @staticmethod
    def call_model_api(agent: Agent, dashscope_messages: List[dict]):
        temperature = max(0.0, min(1.0, agent.temperature)) if agent.temperature is not None else 0.7
        max_tokens = agent.max_tokens if agent.max_tokens and agent.max_tokens > 0 else DEFAULT_MAX_TOKENS

        return Generation.call(
            model=agent.model,
            messages=dashscope_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    @staticmethod
    def update_execution_record(execution: AgentExecution, ai_response: str):
        execution.output = ai_response
        execution.status = 'completed'
        execution.end_time = datetime.utcnow()

    @staticmethod
    def _get_conversation_history(execution_id: int, max_turns: int = 3) -> List[Message]:
        """获取历史消息并转换为Message对象列表"""
        history = []
        current = AgentExecution.query.get(execution_id)

        while current and max_turns > 0:
            if current.parent:
                # 将数据库记录转换为Message对象
                if current.output:
                    history.insert(0, Message(role="assistant", content=current.output))
                history.insert(0, Message(role="user", content=current.input))
                max_turns -= 1
            current = current.parent

        return history

