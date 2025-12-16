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
from langchain_google_genai import ChatGoogleGenerativeAI

# 加载.env文件中的环境变量
load_dotenv()
# print(os.getenv("GOOGLE_API_KEY"))

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # 推荐用 flash，速度快，适合游戏交互
    # model="gemini-1.5-pro",  # 如果觉得逻辑不够聪明，可以换成 pro
    temperature=0.7,
    max_retries=2,
    api_key=os.getenv("GOOGLE_API_KEY"),  # 从环境变量中获取API密钥
)
