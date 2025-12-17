# -*- coding: UTF-8 -*-
"""
@Project ：Project_LiuBu 
@File    ：rpg_agent.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/16 14:20 
"""
import sys
import os
import json
from typing import TypedDict, List, Annotated

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, add_messages

from Setting.Model import llm


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
    messages: Annotated[List[AnyMessage], add_messages]

    # player: 存储角色的数值状态
    # 这部分数据会随着游戏进行不断更新（比如扣血、获得道具）
    player: PlayerStats

    # current_action: 意图识别的结果
    # 例如：{'action': 'attack', 'target': 'goblin'}
    # 这一步是为了让后面的 Python 引擎知道该运行哪个函数
    current_action: dict | None


def game_engine_node(state: GameState):
    """
    这个节点负责执行具体的游戏规则
    :param state:
    :return:
    """
    # 获取当前玩家数据的要执行的动作
    player = state['player']
    action = state.get('current_action')  # 比如 {'type': 'attack', 'target': 'goblin'}

    # 系统反馈信息
    system_result = ""

    if action and action.get('type') == "attack":
        damage = 10
        if 'sword' in player['inventory']: damage += 5
        system_result = f"攻击 {action.get('target')}，造成 {damage} 点伤害, 剩余 {player['hp'] - damage} 点生命"

    elif action and action.get('type') == 'check_status':
        # 查看状态
        system_result = f"当前生命值：{player['hp']}/{player['max_hp']}"
    else:
        system_result = "无效的操作"

    return {"messages": [SystemMessage(content=system_result)]}


def parser_node(state: GameState):
    # 获取玩家的最后一句话
    list_user_input = state["messages"][-1].content

    # 强制要求 LLM 只输出 JSON，不要废话
    system_prompt = """
    你是一个 RPG 游戏的指令解析器。请将玩家的输入解析为 JSON 格式的指令。
    
    可用的指令类型 (type):
    1. "attack" - 当玩家想要攻击、战斗、挥剑时。
    2. "check_status" - 当玩家想要查看状态、HP、背包时。
    3. "unknown" - 无法识别的指令。
    
    输出格式示例: {"type": "attack", "target": "敌人名称"}
    请直接输出 JSON，不要包含 Markdown 格式或其他文字。
    """

    messages = [
        SystemMessage(content=system_prompt)
        , HumanMessage(content=list_user_input)
    ]
    resource = llm.invoke(messages)

    try:
        content = resource.content.replace("```json", "").replace("```", "").strip()
        parsed_action = json.loads(content)
    except Exception as e:
        parsed_action = {"type": "unknown"}

    return {"current_action": parsed_action}


def narrator_node(state: GameState):
    # 获取上下文
    # 取出所有的聊天记录。
    # 此时，记录里最新的那条应该是 Engine 刚刚产生的 SystemMessage
    messages = state["messages"]

    # DM的Prompt
    system_prompt = """
    你是一个文字 RPG 游戏的 DM（地下城主）。
    你的任务是根据【系统判定结果】来描述刚才发生的场景。
    
    要求：
    1. 描述要生动、有沉浸感。
    2. 必须严格遵守【系统判定结果】里的数值（比如伤害值、剩余HP），不能自己编造数值。
    3. 如果系统判定攻击失败，你就描述失败的场景。
    4. 语气要符合奇幻冒险的风格。
    """
    # 构造发送给 LLM 的消息列表
    # 我们把系统提示放在最前面，然后把历史记录接在后面
    # 这样 LLM 既知道自己的身份，又知道刚才发生了什么
    prompt_messages = [SystemMessage(content=system_prompt)] + messages

    # 调用LLM
    resource = llm.invoke(prompt_messages)

    # 返回结果
    return {"messages": [resource]}


# 创建图表实例
workflow = StateGraph(GameState)

# 添加节点
workflow.add_node("parser", parser_node)
workflow.add_node("engine", game_engine_node)
workflow.add_node("narrator", narrator_node)

# 连线
workflow.add_edge(START, "parser")
workflow.add_edge("parser", "engine")
workflow.add_edge("engine", "narrator")
workflow.add_edge("narrator", END)

# 编译
app = workflow.compile()

if __name__ == '__main__':
    print("⚔️ 简单的 AI RPG 启动了！(输入 'q' 退出)")
    # 初始化一些假数据用于测试
    initial_state = {
        "player": {"hp": 100, "max_hp": 100, "attack": 10, "inventory": ["sword"], "location": "森林"},
        "messages": []
    }

    # 这是一个简单的本地聊天循环
    while True:
        user_input = input("\n你: ")
        if user_input.lower() == 'q':
            break

        # 构造输入给 LangGraph 的数据
        # 注意：我们需要把玩家的话包装成 HumanMessage
        inputs = {
            "messages": [HumanMessage(content=user_input)],
            "player": initial_state["player"]  # 实际项目中，这里应该从数据库读取最新的玩家状态
        }

        # 使用流式模式运行图表！
        # app.stream 会逐步执行节点，并允许我们实时显示输出
        print("\nAI DM: ", end="", flush=True)
        final_response = ""
        for output in app.stream(inputs):
            # 遍历每个节点的输出
            for node_name, node_output in output.items():
                if node_name == "narrator":
                    # 获取Narrator节点的消息内容
                    message_content = node_output["messages"][-1].content
                    # 实时打印每个字符
                    for char in message_content:
                        print(char, end="", flush=True)
                        final_response += char
        
        print()  # 换行

        # 获取最终状态以更新本地状态
        # 我们需要从最后一个输出中提取状态信息
        result = None
        for output in app.stream(inputs):
            result = output
        
        # 更新我们的本地状态（主要是为了下一轮对话能接上）
        # 在真实App里，LangGraph 的 Checkpointer 会自动帮你存状态，这里我们需要手动维护一下
        if result and "engine" in result:
            initial_state["player"] = result["engine"].get("player", initial_state["player"])
        if result and "narrator" in result:
            initial_state["messages"] = result["narrator"]["messages"]
