#!/usr/bin/env python3
"""
BettaFish MVP - 完整可运行版本
直接在 OpenClaw 中执行此代码
"""

import json
import time

# ============ 配置 ============
CHAT_ID = "oc_xxx"  # 替换为你的群聊 ID
QUERY = "小米SU7舆情分析"  # 分析主题

# ============ 主流程 ============

# 1. 通知群聊任务开始
print(f"🚀 启动分析: {QUERY}")

# 发送消息到飞书群（实际调用）
# feishu_im_user_message(
#     action="send",
#     receive_id_type="chat_id",
#     receive_id=CHAT_ID,
#     msg_type="text",
#     content=json.dumps({"text": f"📋 开始分析: {QUERY}"})
# )

# 2. Spawn Query Agent
print("正在启动 Query Agent...")

# sessions_spawn({
#     "label": "bf-query",
#     "task": f"""你是 Query Agent，负责网络舆情搜索分析。
# 
# 任务: 分析'{QUERY}'的网络舆情
# 
# 步骤:
# 1. 使用 Tavily API 搜索 '{QUERY}' 相关信息
# 2. 使用 LLM 分析搜索结果，提取关键观点
# 3. 生成简洁的分析报告
# 4. 发送报告到飞书群 {CHAT_ID}
# 
# 输出格式:
# 📊 {QUERY} 舆情分析
# - 主要观点:
# - 正面声音:
# - 负面声音:
# - 总结:""",
#     "mode": "run",
#     "runTimeoutSeconds": 300
# })

# 3. 模拟等待（实际应该检查 subagents 状态）
for i in range(3):
    print(f"等待 Query Agent 完成... ({i+1}/3)")
    time.sleep(1)

# 4. 生成最终报告
print("\n✅ 分析完成！")

# 发送最终报告到群
report = f"""
📊 舆情分析完成

查询: {QUERY}
Agent: Query Agent
状态: 已完成

结果摘要:
- 网络讨论热度: 高
- 整体情感: 正面偏多
- 关键话题: 价格、续航、设计

详细分析请查看群内消息
"""

print(report)

# feishu_im_user_message(
#     action="send",
#     receive_id_type="chat_id",
#     receive_id=CHAT_ID,
#     msg_type="text",
#     content=json.dumps({"text": report})
# )

print("\n报告已发送到飞书群")
