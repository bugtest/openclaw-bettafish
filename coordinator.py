#!/usr/bin/env python3
"""
BettaFish - Coordinator Agent (独立运行)

启动:
sessions_spawn({
    "label": "bf-coordinator",
    "task": "python /workspace/projects/workspace/skills/openclaw-bettafish/coordinator.py",
    "mode": "session",
    "thread": true
})
"""

import json
import time
import uuid
import os
import subprocess
from datetime import datetime

# ============ 配置 ============
CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_d6f8894c9c71ef84eb96c87e3a9ce7f5")  # 替换为你的群ID
WORKSPACE = "/workspace/projects/workspace"
POLL_INTERVAL = 5

# ============ OpenClaw 工具封装 ============

def openclaw_call(tool_name, **kwargs):
    """
    调用 OpenClaw 工具
    通过 openclaw CLI 或 HTTP API
    """
    # 方案1: 通过 openclaw CLI (如果可用)
    # 方案2: 通过直接 HTTP 调用 Gateway API
    
    # 这里使用简化方案: 调用 openclaw 命令行
    cmd = ["openclaw", "tools", tool_name]
    for k, v in kwargs.items():
        cmd.extend([f"--{k}", str(v)])
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=WORKSPACE
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"工具调用失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"工具调用异常: {e}")
        return None


def send_feishu_msg(text):
    """发送飞书群消息"""
    print(f"[发送消息] {text[:50]}...")
    
    # 通过调用 OpenClaw 的 feishu_im_user_message 工具
    # 实际实现需要通过 OpenClaw 的接口
    
    # 简化版: 写入文件, 由主会话读取并发送
    msg_file = f"{WORKSPACE}/.feishu_outbox/{int(time.time())}.json"
    os.makedirs(os.path.dirname(msg_file), exist_ok=True)
    
    with open(msg_file, "w") as f:
        json.dump({
            "action": "send",
            "receive_id_type": "chat_id",
            "receive_id": CHAT_ID,
            "msg_type": "text",
            "content": {"text": text}
        }, f)
    
    print(f"  -> 消息已写入: {msg_file}")
    return True


def get_feishu_messages(minutes=1):
    """获取飞书群消息"""
    # 通过读取 OpenClaw 写入的消息文件
    inbox_dir = f"{WORKSPACE}/.feishu_inbox"
    
    if not os.path.exists(inbox_dir):
        return []
    
    messages = []
    for f in os.listdir(inbox_dir):
        if f.endswith(".json"):
            with open(f"{inbox_dir}/{f}") as fp:
                messages.append(json.load(fp))
            os.remove(f"{inbox_dir}/{f}")  # 消费后删除
    
    return messages


# ============ 状态 ============
sessions = {}

# ============ 核心逻辑 ============

def send_msg(text):
    """发送消息到飞书群"""
    return send_feishu_msg(text)


def parse_task(text):
    """解析用户查询"""
    text_lower = text.lower()
    triggers = ["分析", "舆情", "查一下", "查询", "调研"]
    
    if any(t in text_lower for t in triggers):
        # 移除 @Coordinator 等前缀
        for prefix in ["@coordinator", "@bf-coordinator", "@协调器"]:
            text = text.replace(prefix, "").replace(prefix.title(), "")
        return text.strip()
    return None


def start_analysis(query):
    """启动分析流程"""
    session_id = f"sess-{uuid.uuid4().hex[:6]}"
    
    sessions[session_id] = {
        "id": session_id,
        "query": query,
        "status": "running",
        "agents": {"query": "pending"},
        "started": datetime.now().isoformat(),
        "results": {}
    }
    
    send_msg(f"""📋 新分析任务
━━━━━━━━━━━━━━━━━━━━
Session: {session_id}
查询: {query}

分配任务:
@bf-query 请进行网络搜索分析
━━━━━━━━━━━━━━━━━━━━""")
    
    print(f"[Coordinator] 已创建 Session:{session_id}")
    return session_id


def check_agent_complete(session_id):
    """检查 Agent 是否完成"""
    session = sessions.get(session_id)
    if not session:
        return False
    
    # 检查消息文件
    inbox_dir = f"{WORKSPACE}/.feishu_inbox"
    if not os.path.exists(inbox_dir):
        return False
    
    for f in os.listdir(inbox_dir):
        if f.endswith(".json") and session_id in f:
            with open(f"{inbox_dir}/{f}") as fp:
                data = json.load(fp)
                if data.get("type") == "agent_complete":
                    session["results"][data.get("agent")] = data.get("result")
                    session["agents"][data.get("agent")] = "completed"
                    os.remove(f"{inbox_dir}/{f}")
    
    # 检查是否所有 agent 完成
    return all(s == "completed" for s in session["agents"].values())


def generate_report(session_id):
    """生成最终报告"""
    session = sessions.get(session_id)
    if not session:
        return
    
    query = session["query"]
    results = session.get("results", {})
    
    # 汇总报告
    report = f"""📊 舆情分析报告
━━━━━━━━━━━━━━━━━━━━
查询: {query}
Session: {session_id}

参与 Agent:
"""
    for agent, result in results.items():
        report += f"\n• {agent}: 已完成"
    
    report += "\n\n✅ 分析完成！"
    report += "\n━━━━━━━━━━━━━━━━━━━━"
    
    send_msg(report)
    session["status"] = "completed"
    
    print(f"[Coordinator] Session:{session_id} 报告已发送")


# ============ 消息处理 ============

def handle_message(msg):
    """处理单条消息"""
    sender = msg.get("sender_name", "")
    content = msg.get("content", "")
    
    # 忽略自己的消息
    if sender == "Coordinator" or sender == "bf-coordinator":
        return
    
    # 解析任务
    task = parse_task(content)
    if task:
        print(f"[Coordinator] 收到任务: {task}")
        start_analysis(task)


# ============ 主循环 ============

def main_loop():
    """主循环"""
    print(f"[Coordinator] 已启动")
    print(f"  Chat ID: {CHAT_ID}")
    print(f"  工作目录: {WORKSPACE}")
    
    # 确保目录存在
    os.makedirs(f"{WORKSPACE}/.feishu_outbox", exist_ok=True)
    os.makedirs(f"{WORKSPACE}/.feishu_inbox", exist_ok=True)
    
    send_msg("🤖 Coordinator 已上线\n发送查询开始分析（例如：分析一下小米SU7）")
    
    while True:
        try:
            # 1. 获取新消息
            messages = get_feishu_messages()
            for msg in messages:
                handle_message(msg)
            
            # 2. 检查进行中的 session
            for sid, session in list(sessions.items()):
                if session["status"] == "running":
                    if check_agent_complete(sid):
                        generate_report(sid)
            
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"[Coordinator] 错误: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main_loop()
