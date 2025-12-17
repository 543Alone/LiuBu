# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：summarize.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:51 
"""
from langchain_core.messages import HumanMessage, RemoveMessage

from Setting.Model import llm
from State import GameState


def summarize_node(state: GameState):
    summary = state.get("summary", "")

    # 如果有旧的摘要，把它作为背景告诉 AI
    if summary:
        summary_message = f"这是之前的剧情摘要：{summary}"
    else:
        summary_message = "这是新的冒险开始。"

    messages = state["messages"]

    # 这里我们把“旧摘要” + “最近的对话” 发给 AI，让它生成新的摘要
    prompt = f"""
    {summary_message}

    请将上面的剧情摘要和后续的对话历史，合并成一段新的、简洁的冒险日志。
    只要描述关键剧情（谁去了哪，干了什么，结果如何），不要记录具体的对话细节。
    """

    # 调用 LLM 生成新摘要
    response = llm.invoke(messages + [HumanMessage(content=prompt)])
    new_summary = response.content

    # --- 关键操作：清理内存 ---
    # 我们保留最后 2 条消息（保证对话连贯性），把之前的全删了
    # RemoveMessage 是 LangGraph 用来删除消息的特殊指令
    delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]

    return {
        "summary": new_summary,
        "messages": delete_messages  # 这会把 State 里的旧消息物理删除
    }
