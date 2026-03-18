#!/usr/bin/env python3
"""
BettaFish - Query Agent (独立运行)

功能:
1. 长期运行，监听飞书群消息
2. 发现 Coordinator 分配的任务后执行
3. 搜索分析完成后，发结果到飞书群

启动方式:
sessions_spawn({
    "label": "bf-query",
    "task": "运行 /workspace/projects/workspace/skills/openclaw-bettafish/agent_query.py",
    "mode": "session",
    "thread": true
})
"""

import json
import time
import os
import sys
from datetime import datetime

# ============ 配置 ============
CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_xxx")
TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")
AGENT_NAME = "QueryAgent"
POLL_INTERVAL = 3  # 秒

# ============ 工具函数 ============
def send_msg(text):
    """发送消息到飞书群"""
    prefix = f"[{AGENT_NAME}]"
    print(f"\n{prefix} {text}\n")
    # 实际调用 feishu_im_user_message

def search(query):
    """搜索（模拟）"""
    # TODO: 接入 Tavily API
    return [
        {"title": f"关于 {query} 的结果1", "source": "news"},
        {"title": f"关于 {query} 的结果2", "source": "blog"},
    ]

def analyze(query, results):
    """分析（模拟 LLM）"""
    return f"""
基于 {len(results)} 条搜索结果的分析:

1. 主要观点:
   - 话题热度较高
   - 存在多元观点

2. 情感倾向:
   - 正面: 60%
   - 负面: 25%
   - 中性: 15%

3. 关键信息:
   {results[0]['title']}
   {results[1]['title']}

总结: 整体舆情偏向正面，需关注少数负面声音。
"""

# ============ 任务处理 ============
def process_task(session_id, query):
    """处理分析任务"""
    send_msg(f"🚀 开始处理 Session:{session_id} 查询:{query}")
    
    # Round 1: 首次搜索
    send_msg("🔍 首次搜索...")
    results = search(query)
    
    send_msg(f"【首次总结】找到 {len(results)} 条信息")
    
    # Round 2: 反思搜索
    send_msg("🤔 反思搜索...")
    reflect_results = search(f"{query} 争议 负面")
    
    # 生成最终分析
    analysis = analyze(query, results + reflect_results)
    
    # 发送结果
    send_msg(f"""✅ 分析完成 Session:{session_id}

{analysis}

@{AGENT_NAME} 任务完成
""")

# ============ 消息监听 ============
def check_new_tasks():
    """检查是否有新任务分配给自己"""
    # 实际: 调用 feishu_im_user_get_messages 获取群消息
    # 解析消息，查找 @QueryAgent 的任务分配
    
    # 模拟返回
    return []

def main_loop():
    """主循环 - 持续监听任务"""
    send_msg("🤖 QueryAgent 已上线，等待任务分配")
    
    while True:
        try:
            # 1. 获取群消息
            # messages = feishu_im_user_get_messages(
            #     chat_id=CHAT_ID,
            #     relative_time="last_1_minutes"
            # )
            
            # 2. 查找分配给自己的任务
            # for msg in messages:
            #     if f"@{AGENT_NAME}" in msg.content:
            #         # 解析 session_id 和 query
            #         process_task(session_id, query)
            
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"[{AGENT_NAME}] 错误: {e}")
            time.sleep(POLL_INTERVAL)

# ============ 测试入口 ============
if __name__ == "__main__":
    if len(sys.argv) > 2:
        # 命令行测试: python agent_query.py <session_id> <query>
        process_task(sys.argv[1], sys.argv[2])
    else:
        # 正常运行模式
        main_loop()
