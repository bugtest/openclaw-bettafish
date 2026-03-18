#!/usr/bin/env python3
"""
BettaFish - Coordinator Agent (独立运行)

功能:
1. 长期运行，监听飞书群消息
2. 发现用户查询后，创建 Session
3. 在群里分配任务给 Worker Agents
4. 监听 Worker 结果，汇总生成报告

启动方式:
sessions_spawn({
    "label": "bf-coordinator",
    "task": "运行 /workspace/projects/workspace/skills/openclaw-bettafish/coordinator.py",
    "mode": "session",
    "thread": true
})
"""

import json
import time
import uuid
import os
from datetime import datetime

# ============ 配置 ============
CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_xxx")
POLL_INTERVAL = 5  # 秒

# ============ 状态 ============
sessions = {}  # session_id -> session_info

# ============ 消息协议 ============
def send_msg(text):
    """发送消息到飞书群"""
    print(f"[发送到群] {text}")
    # 实际调用:
    # feishu_im_user_message(
    #     action="send",
    #     receive_id_type="chat_id",
    #     receive_id=CHAT_ID,
    #     msg_type="text",
    #     content=json.dumps({"text": text})
    # )

def parse_task(text):
    """解析用户查询"""
    # 简单规则: 包含 "分析" 或 "舆情" 就认为是任务
    if "分析" in text or "舆情" in text or "查一下" in text:
        return text.replace("@Coordinator", "").strip()
    return None

# ============ 核心逻辑 ============
def start_analysis(query):
    """启动分析流程"""
    session_id = f"sess-{uuid.uuid4().hex[:6]}"
    
    # 记录 session
    sessions[session_id] = {
        "id": session_id,
        "query": query,
        "status": "running",
        "agents": {},
        "started": datetime.now().isoformat()
    }
    
    # 1. 通知群聊
    send_msg(f"""📋 新分析任务
Session: {session_id}
查询: {query}

分配任务:
@QueryAgent 请进行网络搜索分析""")
    
    # 2. 等待 QueryAgent 完成（通过轮询群消息）
    print(f"[Coordinator] 等待 QueryAgent 完成 {session_id}...")
    
    return session_id

def check_worker_result(session_id, agent_name):
    """检查 Worker Agent 是否返回结果"""
    # 实际: 读取飞书群消息，查找 agent 的完成通知
    # 这里简化处理
    return None

def generate_report(session_id):
    """生成最终报告"""
    session = sessions.get(session_id)
    if not session:
        return
    
    send_msg(f"""📊 舆情分析报告

Session: {session_id}
查询: {session['query']}
状态: ✅ 完成

参与 Agent: QueryAgent
详细结果请查看群内消息记录
""")
    
    session["status"] = "completed"

# ============ 主循环 ============
def main_loop():
    """主循环 - 持续监听"""
    print(f"[Coordinator] 已启动，监听群 {CHAT_ID}")
    send_msg("🤖 Coordinator 已上线，发送查询开始分析")
    
    while True:
        try:
            # 1. 获取群消息（实际调用 feishu_im_user_get_messages）
            # messages = feishu_im_user_get_messages(
            #     chat_id=CHAT_ID,
            #     relative_time="last_1_minutes"
            # )
            
            # 模拟: 检查是否有新任务
            # 实际应该解析消息内容
            
            # 2. 检查进行中的 session
            for sid, session in list(sessions.items()):
                if session["status"] == "running":
                    # 检查是否所有 agent 完成
                    # 实际: 检查群消息中 agent 的完成通知
                    pass
            
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"[Coordinator] 错误: {e}")
            time.sleep(POLL_INTERVAL)

# ============ 测试入口 ============
if __name__ == "__main__":
    # 测试模式: 直接启动一次分析
    if len(sys.argv) > 1:
        query = sys.argv[1]
        start_analysis(query)
    else:
        # 正常运行模式
        main_loop()
