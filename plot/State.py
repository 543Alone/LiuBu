# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：State.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:30 
"""
from typing import TypedDict, Annotated, List

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class GameState(TypedDict):
    # 只需要存消息历史，不需要存那些复杂的 current_action 了
    messages: Annotated[List[AnyMessage], add_messages]
    # 用来存长期的剧情摘要
    summary: str
