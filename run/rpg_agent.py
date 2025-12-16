# -*- coding: UTF-8 -*-
"""
@Project ：Project_LiuBu 
@File    ：rpg_agent.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/16 14:20 
"""
from typing import TypedDict, List

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages, StateGraph
from openai.types.chat.chat_completion_message import Annotation
from openai.types.chat.chat_completion_message import Annotation


# 玩家数据
class PlayerStats(TypedDict):
    hp: int
    max_hp: int
    attack: int
    inventory: List[str]
    location: str


class GameState(TypedDict):
    # messages: 存储聊天记录
    # Annotated[..., add_messages] 的意思是：
    # 当新消息进来时，不要覆盖旧的，而是"追加"到列表里
    messages: Annotation[List[AnyMessage], add_messages]

    # player: 存储角色的数值状态
    # 这部分数据会随着游戏进行不断更新（比如扣血、获得道具）
    player: PlayerStats

    # current_action: 意图识别的结果
    # 例如：{'action': 'attack', 'target': 'goblin'}
    # 这一步是为了让后面的 Python 引擎知道该运行哪个函数
    current_action: dict | None
