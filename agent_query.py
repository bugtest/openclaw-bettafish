#!/usr/bin/env python3
"""
BettaFish MVP - Query Agent
用法: 被 Coordinator 通过 sessions_spawn 启动
任务: 搜索分析 -> 发结果到飞书群
"""

import os
import sys

# 从任务描述中获取查询
TASK = sys.argv[1] if len(sys.argv) > 1 else "分析舆情"
CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_xxx")
TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")

print(f"[QueryAgent] 开始: {TASK}")

# 1. 搜索（模拟）
print("搜索中...")
results = [
    "结果1: 小米SU7发布引发热议",
    "结果2: 用户评价总体积极",
    "结果3: 存在一些负面声音"
]

# 2. 分析（模拟 LLM）
analysis = f"""
分析: {TASK}

发现:
1. {results[0]}
2. {results[1]}
3. {results[2]}

结论: 整体舆情正面，需关注负面反馈
"""

# 3. 发送结果到飞书群
print(f"\n发送结果到群 {CHAT_ID}:")
print(analysis)

# 实际调用:
# feishu_im_user_message(action="send", receive_id_type="chat_id", 
#                        receive_id=CHAT_ID, msg_type="text", 
#                        content=json.dumps({"text": analysis}))

print("[QueryAgent] 完成")
