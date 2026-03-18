#!/usr/bin/env python3
"""
BettaFish - OpenClaw 网关

这个文件在 OpenClaw 主会话中运行，负责：
1. 接收飞书群消息，转发给 Agent
2. 读取 Agent 的消息文件，发送到飞书群

启动方式：在 OpenClaw 会话中直接执行此代码
"""

import os
import json
import time
from datetime import datetime

# 配置
CHAT_ID = "oc_xxx"  # 替换为你的群聊 ID
WORKSPACE = "/workspace/projects/workspace"
POLL_INTERVAL = 3

def ensure_dirs():
    """确保目录存在"""
    dirs = [
        f"{WORKSPACE}/.feishu_outbox",     # Agent 写入，网关读取发送
        f"{WORKSPACE}/.feishu_inbox",      # 网关写入，Agent 读取
        f"{WORKSPACE}/.agent_inbox",       # 网关写入，Agent 读取
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

# ============ 飞书消息网关 ============

def process_agent_messages():
    """读取 Agent 的消息文件，发送到飞书"""
    outbox = f"{WORKSPACE}/.feishu_outbox"
    
    if not os.path.exists(outbox):
        return
    
    for filename in os.listdir(outbox):
        if not filename.endswith(".json"):
            continue
        
        filepath = f"{outbox}/{filename}"
        try:
            with open(filepath, "r") as f:
                msg = json.load(f)
            
            # 发送到飞书
            text = msg.get("text", "")
            agent = msg.get("agent", "Agent")
            
            print(f"[网关] 发送 {agent} 的消息到飞书")
            
            # 实际调用 OpenClaw 工具
            # feishu_im_user_message(
            #     action="send",
            #     receive_id_type="chat_id",
            #     receive_id=CHAT_ID,
            #     msg_type="text",
            #     content=json.dumps({"text": text})
            # )
            
            # 删除已处理的消息文件
            os.remove(filepath)
            
        except Exception as e:
            print(f"[网关] 处理消息失败: {e}")


def dispatch_to_agent(sender, content, is_at_coordinator=False, is_at_query=False):
    """将飞书消息分发给 Agent"""
    
    # 如果 @了 Query Agent
    if is_at_query or "@bf-query" in content or "@query" in content.lower():
        # 从消息中提取 session_id 和任务
        inbox = f"{WORKSPACE}/.agent_inbox/bf-query"
        os.makedirs(inbox, exist_ok=True)
        
        task_file = f"{inbox}/task_{int(time.time())}.json"
        with open(task_file, "w") as f:
            json.dump({
                "type": "task_assign",
                "sender": sender,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False)
        
        print(f"[网关] 已转发任务到 bf-query")


def process_feishu_messages():
    """获取飞书消息，转发给 Agent"""
    # 实际: 调用 feishu_im_user_get_messages
    # 这里简化，消息由用户在其他地方获取后写入文件
    
    inbox = f"{WORKSPACE}/.feishu_inbox"
    if not os.path.exists(inbox):
        return
    
    for filename in os.listdir(inbox):
        if not filename.endswith(".json"):
            continue
        
        filepath = f"{inbox}/{filename}"
        try:
            with open(filepath, "r") as f:
                msg = json.load(f)
            
            # 解析消息
            sender = msg.get("sender_name", "")
            content = msg.get("content", "")
            
            # 检查 @了谁
            is_at_coordinator = "@coordinator" in content.lower() or "@bf-coordinator" in content.lower()
            is_at_query = "@query" in content.lower() or "@bf-query" in content.lower()
            
            # 分发给相应 Agent
            if is_at_coordinator or is_at_query:
                dispatch_to_agent(sender, content, is_at_coordinator, is_at_query)
            
            # 删除已处理的消息
            os.remove(filepath)
            
        except Exception as e:
            print(f"[网关] 处理飞书消息失败: {e}")


# ============ 主循环 ============

def main_loop():
    """网关主循环"""
    print("[BettaFish 网关] 已启动")
    print(f"  Chat ID: {CHAT_ID}")
    print(f"  工作目录: {WORKSPACE}")
    
    ensure_dirs()
    
    while True:
        try:
            # 1. 处理 Agent 的消息（发送到飞书）
            process_agent_messages()
            
            # 2. 处理飞书消息（分发给 Agent）
            process_feishu_messages()
            
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"[网关] 错误: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main_loop()
