# -*- coding: UTF-8 -*-
"""
@Project ：LiuBu 
@File    ：user_tool.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/17 09:34 
"""
from Ai_tools import combat_tool
from Player_tools import inventory_tool
from Setting.Model import llm

# 把工具打包
tools = [combat_tool, inventory_tool]
# 这一步很关键：告诉 LLM 它有哪些技能
llm_with_tools = llm.bind_tools(tools)
