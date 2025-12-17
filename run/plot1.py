# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：plot1.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:25 
"""
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from Setting.Model import llm
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage


# --- 1. 定义工具 (把之前的 Engine 变成工具) ---
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


def inventory_tool() -> str:
    """
    当玩家想查看背包、物品或状态时调用。
    """
    return "【系统状态】当前 HP: 80/100, 背包: [生锈的剑, 回血草药]"


# 把工具打包
tools = [combat_tool, inventory_tool]
# 这一步很关键：告诉 LLM 它有哪些技能
llm_with_tools = llm.bind_tools(tools)


# --- 2. 定义状态 (State) ---
class GameState(TypedDict):
    # 只需要存消息历史，不需要存那些复杂的 current_action 了
    messages: Annotated[List[AnyMessage], add_messages]
    summary: str

# --- 3. 定义核心节点 ---

def agent_node(state: GameState):
    """
    这是唯一的决策中心。
    它会自己决定是：
    1. 直接回复玩家（比如纯剧情描述）
    2. 还是调用工具（比如算伤害）
    """
    messages = state["messages"]
    # 增加一个 System Prompt 来设定人设
    if not isinstance(messages[0], SystemMessage):
        system_msg = SystemMessage(content="""
        你是一个文字 RPG 的 DM（地下城主）。
        1. 对于玩家的普通行为（观察、对话、移动），请你发挥想象力，生动描述剧情。
        2. 当玩家涉及【战斗】或【查询数据】时，请务必调用对应的工具来获取结果。
        3. 拿到工具结果后，请根据结果继续描述战斗场面。
        """)
        messages = [system_msg] + messages

    # AI 思考并行动
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


from langgraph.prebuilt import ToolNode

# LangGraph 自带的一个节点，专门用来运行工具
tool_node = ToolNode(tools)


# --- 4. 组装图表 (最关键的一步) ---

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


workflow = StateGraph(GameState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

# 这里是“分岔路口”
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",  # 如果去 tools，跑完工具
        END: END  # 如果去 END，等待玩家下次输入
    }
)

# 工具跑完后，必须把结果还给 agent，让 agent 把它润色成小说
workflow.add_edge("tools", "agent")

app = workflow.compile()
