# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：node.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:39 
"""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from State import GameState
from agent import agent_node
from summarize import summarize_node
from user_tool import tools

tool_node = ToolNode(tools)

workflow = StateGraph(GameState)

# 添加总结节点
workflow.add_node("summarize", summarize_node)


# 修改原来的条件边
# 原来是: tools -> agent -> END
# 现在是: tools -> agent -> (判断长度) -> summarize -> END

# 我们需要定义一个新的条件边逻辑，接在 agent 后面
def should_continue_or_summarize(state: GameState):
    messages = state["messages"]
    last_message = messages[-1]

    # 1. 优先判断：是否要用工具？
    if last_message.tool_calls:
        return "tools"

    # 2. 其次判断：是否太长需要总结？
    if len(messages) > 6:
        return "summarize"

    # 3. 都不需要，直接结束
    return END


# 重构连接关系
workflow = StateGraph(GameState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("summarize", summarize_node)

workflow.add_edge(START, "agent")

# Agent 决定去向
workflow.add_conditional_edges(
    "agent",
    should_continue_or_summarize,
    {
        "tools": "tools",
        "summarize": "summarize",
        END: END
    }
)

workflow.add_edge("tools", "agent")
workflow.add_edge("summarize", END)

# 初始化一个内存存档器
checkpointer = MemorySaver()

# 告诉图表：请用这个存档器来记东西
app = workflow.compile(checkpointer=checkpointer)
