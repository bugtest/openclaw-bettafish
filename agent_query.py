#!/usr/bin/env python3
"""
BettaFish - Query Agent (独立运行)

启动:
sessions_spawn({
    "label": "bf-query",
    "task": "python /workspace/projects/workspace/skills/openclaw-bettafish/agent_query.py",
    "mode": "session",
    "thread": true
})
"""

import json
import time
import os
import re
from datetime import datetime

# ============ 配置 ============
AGENT_NAME = "bf-query"
WORKSPACE = "/workspace/projects/workspace"
POLL_INTERVAL = 3

# ============ 消息通信 ============

def send_msg(text):
    """发送消息到飞书群"""
    print(f"\n[{AGENT_NAME}] {text[:60]}...\n")
    
    # 写入 outbox，由 OpenClaw 网关发送
    msg_file = f"{WORKSPACE}/.feishu_outbox/{AGENT_NAME}_{int(time.time())}.json"
    os.makedirs(os.path.dirname(msg_file), exist_ok=True)
    
    with open(msg_file, "w") as f:
        json.dump({
            "agent": AGENT_NAME,
            "text": text,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False)
    
    return True


def get_messages():
    """获取分配给自己的任务"""
    inbox_dir = f"{WORKSPACE}/.agent_inbox/{AGENT_NAME}"
    
    if not os.path.exists(inbox_dir):
        return []
    
    messages = []
    for f in os.listdir(inbox_dir):
        if f.endswith(".json"):
            with open(f"{inbox_dir}/{f}") as fp:
                messages.append(json.load(fp))
            os.remove(f"{inbox_dir}/{f}")
    
    return messages


def report_complete(session_id, result):
    """报告任务完成"""
    report_file = f"{WORKSPACE}/.feishu_inbox/complete_{session_id}_{AGENT_NAME}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, "w") as f:
        json.dump({
            "type": "agent_complete",
            "session_id": session_id,
            "agent": AGENT_NAME,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False)


# ============ 搜索/分析 ============

def search(query):
    """搜索（模拟，用户可替换为 Tavily）"""
    print(f"[{AGENT_NAME}] 搜索: {query}")
    time.sleep(1)  # 模拟网络延迟
    return [
        {"title": f"{query} 相关新闻1", "source": "news", "snippet": "..."},
        {"title": f"{query} 相关讨论2", "source": "forum", "snippet": "..."},
        {"title": f"{query} 相关视频3", "source": "video", "snippet": "..."},
    ]


def analyze(query, results):
    """分析（模拟 LLM）"""
    return f"""基于 {len(results)} 条信息的分析:

📌 主要发现:
• 话题热度: 较高
• 讨论焦点: 产品特性、价格、用户体验
• 情感倾向: 正面居多

📊 数据分布:
• 新闻: {sum(1 for r in results if r['source']=='news')} 条
• 讨论: {sum(1 for r in results if r['source']=='forum')} 条
• 视频: {sum(1 for r in results if r['source']=='video')} 条

✅ 总结: 整体舆情积极，建议持续关注用户反馈。
"""


# ============ 任务处理 ============

def process_task(session_id, query):
    """处理分析任务"""
    print(f"[{AGENT_NAME}] 处理 Session:{session_id} Query:{query}")
    
    # Round 1: 首次搜索
    send_msg(f"🚀 Session:{session_id} 开始分析\n🔍 首次搜索: {query}")
    results1 = search(query)
    
    summary1 = f"找到 {len(results1)} 条相关信息"
    send_msg(f"【首次总结】{summary1}")
    
    # Round 2: 反思搜索
    send_msg(f"🤔 反思搜索...")
    results2 = search(f"{query} 问题 负面")
    
    summary2 = f"补充搜索找到 {len(results2)} 条信息"
    send_msg(f"【反思总结】{summary2}")
    
    # 生成最终分析
    analysis = analyze(query, results1 + results2)
    
    # 发送完整结果
    send_msg(f"""✅ Session:{session_id} 分析完成

{analysis}

@{AGENT_NAME} 任务完成""")
    
    # 报告完成状态
    report_complete(session_id, analysis)
    
    print(f"[{AGENT_NAME}] Session:{session_id} 完成")


# ============ 主循环 ============

def main_loop():
    """主循环 - 持续监听任务"""
    print(f"[{AGENT_NAME}] 已启动")
    print(f"  工作目录: {WORKSPACE}")
    
    # 确保目录存在
    os.makedirs(f"{WORKSPACE}/.agent_inbox/{AGENT_NAME}", exist_ok=True)
    
    send_msg(f"🤖 {AGENT_NAME} 已上线，等待任务分配")
    
    while True:
        try:
            # 获取新任务
            tasks = get_messages()
            for task in tasks:
                if task.get("type") == "task_assign":
                    process_task(
                        task.get("session_id"),
                        task.get("query")
                    )
            
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"[{AGENT_NAME}] 错误: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main_loop()
