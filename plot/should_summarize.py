# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：should_summarize.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:52 
"""
from State import GameState
from langgraph.graph import END


def should_summarize(state: GameState):
    """
    判断当前消息是不是太多了？
    """
    messages = state["messages"]

    # 比如：如果对话超过 6 条，就触发总结
    # (实际项目中这个数字可以设大点，比如 20)
    if len(messages) > 6:
        return "summarize"
    return END
