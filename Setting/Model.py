# -*- coding: UTF-8 -*-
"""
@Project ：Project_LiuBu 
@File    ：Model.py
@IDE     ：PyCharm 
@Author  ：Write Bug
@Date    ：2025/12/16 13:59 
"""
import os

from dotenv import load_dotenv
from langchain_xai import ChatXAI

# 加载.env文件中的环境变量
load_dotenv()
# print(os.getenv("XAI_API_KEY"))

llm = ChatXAI(
    model="grok-4-1-fast-reasoning-latest",
    temperature=0.7,
    max_retries=2,
    api_key=os.getenv("XAI_API_KEY"),  # 从环境变量中获取API密钥
)