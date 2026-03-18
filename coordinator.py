#!/usr/bin/env python3
"""
BettaFish MVP - Coordinator
用法: 在 OpenClaw 中直接运行此代码
"""

import os
import json
import time

CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_xxx")
QUERY = "小米SU7舆情分析"  # 修改这里

# 1. 发送任务到飞书群
print(f"启动分析: {QUERY}")

# 2. Spawn Query Agent
print("正在启动 Query Agent...")
# 实际使用时调用:
# sessions_spawn({
#     "label": "query-agent",
#     "task": f"分析 '{QUERY}' 的网络舆情，使用 Tavily 搜索，输出 markdown 报告",
#     "mode": "run"
# })

# 3. 等待结果（模拟）
for i in range(3):
    print(f"等待 Agent 完成... ({i+1}/3)")
    time.sleep(1)

# 4. 汇总
print("\n分析完成！")
print(f"查询: {QUERY}")
print("结果已发送到飞书群")
