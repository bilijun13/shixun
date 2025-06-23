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
            history_messages: Optional[List[dict]] = None,
            max_history_turns: int = 3  # 新增参数控制历史轮数
    ):
        """
        增强版多轮对话支持
        """
        try:
            # 消息组装逻辑优化
            messages = [{"role": "system", "content": agent.system_prompt}]

            # 添加历史消息（优先级：直接传入 > 数据库查询）
            if history_messages:
                messages.extend(history_messages)
            elif execution_id:
                messages.extend(
                    TongyiService._get_conversation_history(
                        execution_id,
                        max_turns=max_history_turns
                    )
                )

            # 添加当前用户输入
            messages.append({"role": "user", "content": user_input})

            # 创建执行记录
            execution = AgentExecution(
                agent_id=agent.id,
                user_id=agent.user_id,
                input=user_input,
                status='processing',
                parent_execution_id=execution_id
            )
            db.session.add(execution)
            db.session.flush()  # 先获取execution.id但不提交

            # API调用
            response = Generation.call(
                model=agent.model,
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens or 1500
            )

            # 处理响应
            execution.output = response.output.text
            execution.status = 'completed'
            execution.end_time = datetime.utcnow()
            db.session.commit()

            return response.output.text, execution

        except Exception as e:
            db.session.rollback()
            if 'execution' in locals():
                execution.status = 'failed'
                execution.output = str(e)
                db.session.commit()
            raise

    @staticmethod
    def _get_conversation_history(execution_id: int, max_turns: int = 3) -> List[dict]:
        """优化历史消息获取逻辑"""
        history = []
        current = AgentExecution.query.get(execution_id)

        # 确保获取完整的对话轮次（user+assistant为一轮）
        while current and max_turns > 0:
            if current.parent:  # 确保有父记录
                # 添加AI回复（如果存在）
                if current.output:
                    history.insert(0, {
                        "role": "assistant",
                        "content": current.output
                    })
                # 添加上一轮用户输入
                history.insert(0, {
                    "role": "user",
                    "content": current.input
                })
                max_turns -= 1
            current = current.parent

        return history