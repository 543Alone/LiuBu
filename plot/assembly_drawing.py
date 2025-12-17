# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：assembly_drawing.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:38 
"""
from langgraph.graph import END

from State import GameState


def should_continue(state: GameState):
    """
    条件判断边 (Conditional Edge)。
    判断 AI 是想说话，还是想用工具？
    """
    last_message = state["messages"][-1]
    # 如果 AI 的回复里包含 tool_calls，说明它想用工具，转去 tools 节点
    if last_message.tool_calls:
        return "tools"
    # 否则，直接结束，把话吐给玩家
    return END
