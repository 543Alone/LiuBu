# -*- coding: UTF-8 -*-
"""
@Project ：Project_LiuBu 
@File    ：shen_gong_bao.py.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/16 10:21 
"""
from typing import TypedDict, List

from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END

from Setting.Model import llm


class GameState(TypedDict):
    history: List[BaseMessage]  # 对话历史，作为记忆
    attitude: int  # 好感度：-100 (死敌) 到 100 (挚友)
    status: str  # 当前状态：active (对话中), combat (战斗), escaped (逃脱)


def analyze_intent(state: GameState):
    messages = state["history"]
    current_attitude = state["attitude"]

    # 获取玩家最新的一句话
    last_user_input = messages[-1].content

    print(f"\n[系统后台] 申公豹当前好感度: {current_attitude}")
    print(f"[系统后台] 正在分析玩家意图...")

    # 使用 LLM 判断玩家意图对好感度的影响
    # 为了简化，这里我们让 LLM 返回一个数字字符串
    prompt = f"""
    你是一个游戏数值策划。
    当前NPC是申公豹（商朝国师，性格：嫉妒心强、阴险、自负、只有利益没有朋友）。
    玩家对申公豹说："{last_user_input}"
    当前好感度是：{current_attitude}

    请分析这句话会让申公豹高兴还是生气。
    - 如果是奉承、贬低姜子牙，好感度增加 (5 到 20)。
    - 如果是挑衅、承认是西岐的人、或者想直接溜走，好感度减少 (-5 到 -50)。
    - 如果是无关废话，好感度不变 (0)。

    只返回一个整数（例如：10 或 -20），不要返回任何其他文字。
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        score_change = int(response.content.strip())
    except:
        score_change = 0  # 容错

    new_attitude = current_attitude + score_change

    # 简单的状态机逻辑
    new_status = "active"
    if new_attitude <= -50:
        new_status = "combat"
    elif new_attitude >= 50:
        new_status = "friend"

    print(f"[系统后台] 好感度变化: {score_change} -> 当前: {new_attitude} (状态: {new_status})")

    return {"attitude": new_attitude, "status": new_status}


# 节点 B: 角色扮演 (Actor)
# 负责生成申公豹的回复
def generate_response(state: GameState):
    status = state["status"]
    attitude = state["attitude"]
    messages = state["history"]

    # 根据状态设定不同的系统人设
    system_prompt = ""
    if status == "combat":
        system_prompt = "你现在被激怒了，准备动手。说一句狠话，然后通过描述动作发起攻击。字数50字以内。"
    elif status == "friend":
        system_prompt = "你现在觉得这人可以利用。语气变得缓和甚至有点狼狈为奸的感觉。暗示可以透露姜子牙的弱点。字数50字以内。"
    else:
        system_prompt = f"""
        你扮演申公豹。现在的背景是商周时期，你在荒野拦住了玩家。
        你当前的内心好感度是 {attitude} (范围-100到100)。
        如果好感度低，你要阴阳怪气，怀疑他是西岐的奸细。
        如果好感度高，你要表现出‘道友请留步’的虚伪热情。
        请根据上下文回复玩家。保持古风，简短有力，切忌长篇大论。
        """

    # 调用 LLM 生成对话
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)

    # 将回复存入历史
    return {"history": [response]}


workflow = StateGraph(GameState)

# 添加节点
workflow.add_node("analyze", analyze_intent)
workflow.add_node("respond", generate_response)

# 设置入口
workflow.set_entry_point("analyze")


# 添加边 (Edge) 和 条件分支
def check_status(state: GameState):
    if state["status"] == "combat":
        return "respond"  # 还是让他说最后一句狠话，然后结束
    return "respond"


workflow.add_edge("analyze", "respond")
workflow.add_edge("respond", END)  # 单轮对话结束，等待下一轮循环

# 编译图
app = workflow.compile()


def main():
    print("=" * 50)
    print("⚡️ 游戏开始：荒野岔路口 ⚡️")
    print("申公豹骑着黑点虎挡在了你的面前...")
    print("申公豹：道友请留步！我看你行色匆匆，莫非是去往西岐？")
    print("=" * 50)

    # 初始化状态
    chat_history = [
        SystemMessage(content="你是申公豹。"),
        BaseMessage(content="道友请留步！我看你行色匆匆，莫非是去往西岐？", type="ai")
    ]
    current_state = {
        "history": chat_history,
        "attitude": -10,  # 初始略带敌意
        "status": "active"
    }

    while True:
        user_input = input("\n> 少侠请回答 (输入 q 退出): ")
        if user_input.lower() == 'q':
            break

        # 玩家输入加入历史
        current_state["history"].append(HumanMessage(content=user_input))

        # 运行 LangGraph
        # stream 模式会逐步执行节点
        for output in app.stream(current_state):
            # 这里可以捕获中间状态，但为了MVP我们只关心最后结果
            for key, value in output.items():
                if key == "analyze":
                    # 更新本地状态中的数值
                    current_state["attitude"] = value["attitude"]
                    current_state["status"] = value["status"]
                if key == "respond":
                    # 更新对话历史（LangGraph会自动处理追加，但这里我们手动模拟外部存储）
                    last_response = value["history"][-1]
                    current_state["history"].append(last_response)

                    print(f"\n🐯 申公豹: {last_response.content}")

        # 检查是否结局
        if current_state["status"] == "combat":
            print("\n*** 申公豹祭出了开天珠！你进入了战斗（Demo结束） ***")
            break


if __name__ == "__main__":
    main()
