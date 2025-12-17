# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：main.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 10:00 
"""
from langchain_core.messages import HumanMessage

from node import app


def main():
    print("⚔️  AI RPG 启动！(输入 'q' 退出)")

    # 这里的 thread_id 就像是“存档槽位”
    # 只要 thread_id 不变，AI 就会一直记得你
    config = {"configurable": {"thread_id": "player_1"}}

    while True:
        user_input = input("\n👤 你: ")
        if user_input.lower() in ['q', 'quit']: break

        # 现在我们只需要发送“增量”消息（新消息）
        # MemorySaver 会自动把旧消息从数据库里调出来拼接上去
        inputs = {"messages": [HumanMessage(content=user_input)]}

        # 使用 stream 模式，一边生成一边输出
        # config 必须传进去，不然不知道存哪个档
        try:
            for event in app.stream(inputs, config=config):
                for key, value in event.items():
                    if key == "agent":  # 如果是 Agent 说话
                        last_msg = value["messages"][-1]
                        print(f"\n🤖 DM: {last_msg.content}")
                    elif key == "tools":  # 如果是工具运行
                        # 这里可以打印工具的结果，或者保持神秘不打印
                        pass
        except Exception as e:
            print(f"❌ 报错了: {e}")