# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：agent.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:36 
"""
from langchain_core.messages import SystemMessage

from State import GameState
from user_tool import llm_with_tools


def agent_node(state: GameState):
    messages = state["messages"]
    summary = state.get("summary", "")

    # 如果有摘要，把它变成 SystemMessage 放在最前面
    # 这样 AI 就知道：“哦，我之前的经历是这样的...”
    if summary:
        system_msg = SystemMessage(content=f"【前情提要】: {summary}")
        # 这里的逻辑是：SystemPrompt(人设) + Summary(记忆) + RecentMessages(最近对话)
        messages = [SystemMessage(content="你是一个DM...")] + [system_msg] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
