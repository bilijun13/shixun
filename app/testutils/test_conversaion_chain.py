from app import TongyiService
from app.models import Agent


def test_conversation_chain():
    """验证对话链是否正常工作"""
    agent = Agent.query.first()

    # 第一轮
    resp1, exec1 = TongyiService.generate_response(agent, "第一句话")
    assert exec1.parent_execution_id is None

    # 第二轮
    resp2, exec2 = TongyiService.generate_response(agent, "第二句话", exec1.id)
    assert exec2.parent_execution_id == exec1.id

    # 检查数据库
    from sqlalchemy import inspect
    inspector = inspect(exec2)
    print("实际存储的parent_execution_id:",
          inspector.attrs.parent_execution_id.value)