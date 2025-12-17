# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：Ai_tools.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:32 
"""


# 这就是 AI 的“技能包”。只有当它觉得需要用的时候才会用。

def combat_tool(action_type: str, target: str) -> str:
    """
    只有在发生战斗、攻击、或者造成伤害时才调用此工具。
    返回计算后的伤害结果。
    """
    # 这里依然是严谨的 Python 逻辑
    if action_type == "attack":
        damage = 15  # 这里可以是复杂的伤害公式
        return f"【系统判定】攻击命中 {target}！造成 {damage} 点物理伤害。"
    return "【系统判定】无效的战斗动作。"
