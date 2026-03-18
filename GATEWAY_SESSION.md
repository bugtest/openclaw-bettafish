# BettaFish 网关 - OpenClaw 会话版

## 使用方式

在 OpenClaw 会话中直接执行以下代码，它会启动一个循环，持续转发消息。

```python
# ============ 配置 ============
CHAT_ID = "oc_你的群聊ID"
WORKSPACE = "/workspace/projects/workspace"
POLL_INTERVAL = 5

import os
import json
import time
from datetime import datetime

# 确保目录存在
for d in [f"{WORKSPACE}/.feishu_outbox", f"{WORKSPACE}/.agent_inbox/bf-query"]:
    os.makedirs(d, exist_ok=True)

# ============ 消息处理函数 ============

def process_outbox():
    """读取 Agent 消息，发送到飞书"""
    outbox = f"{WORKSPACE}/.feishu_outbox"
    if not os.path.exists(outbox):
        return
    
    for f in os.listdir(outbox):
        if not f.endswith(".json"):
            continue
        
        filepath = f"{outbox}/{f}"
        try:
            with open(filepath, "r") as fp:
                msg = json.load(fp)
            
            text = msg.get("text", "")
            
            # 发送到飞书
            feishu_im_user_message(
                action="send",
                receive_id_type="chat_id",
                receive_id=CHAT_ID,
                msg_type="text",
                content=json.dumps({"text": text})
            )
            
            print(f"[网关] 发送消息: {text[:50]}...")
            os.remove(filepath)
            
        except Exception as e:
            print(f"[网关] 发送失败: {e}")

def dispatch_task(sender, content):
    """分配任务给 Query Agent"""
    inbox = f"{WORKSPACE}/.agent_inbox/bf-query"
    os.makedirs(inbox, exist_ok=True)
    
    # 解析 session_id (简化: 使用时间戳)
    session_id = f"sess-{int(time.time()) % 10000}"
    
    task_file = f"{inbox}/task_{int(time.time())}.json"
    with open(task_file, "w") as f:
        json.dump({
            "type": "task_assign",
            "session_id": session_id,
            "query": content,
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False)
    
    print(f"[网关] 已分配任务: {content[:30]}...")

# ============ 主循环 ============

print("[BettaFish 网关] 已启动")
print(f"  Chat ID: {CHAT_ID}")

# 启动时发送上线通知
feishu_im_user_message(
    action="send",
    receive_id_type="chat_id",
    receive_id=CHAT_ID,
    msg_type="text",
    content=json.dumps({"text": "🤖 BettaFish 网关已上线"})
)

# 持续运行
while True:
    try:
        # 1. 处理 Agent 消息
        process_outbox()
        
        # 2. 获取飞书消息 (最近1分钟)
        # 注意: 这里使用 feishu_im_user_get_messages 工具
        messages = feishu_im_user_get_messages(
            chat_id=CHAT_ID,
            relative_time="last_1_minutes"
        )
        
        # 解析并分发给 Agent
        for msg in messages.get("items", []):
            content = msg.get("content", "")
            sender = msg.get("sender", {}).get("name", "")
            
            # 只处理 @bf-query 的消息
            if "@bf-query" in content or "@query" in content.lower():
                # 提取查询内容
                query = content.replace("@bf-query", "").replace("@query", "").strip()
                if query:
                    dispatch_task(sender, query)
        
        time.sleep(POLL_INTERVAL)
        
    except Exception as e:
        print(f"[网关] 错误: {e}")
        time.sleep(POLL_INTERVAL)
```

## 启动步骤

1. **修改配置**: 将 `CHAT_ID` 改为你的实际群聊 ID

2. **在 OpenClaw 会话中执行**: 直接粘贴上面的代码运行

3. **启动 Agent**:
```python
sessions_spawn({
    "label": "bf-query",
    "task": "python /workspace/projects/workspace/skills/openclaw-bettafish/agent_query.py",
    "mode": "session",
    "thread": true
})
```

4. **在飞书群中使用**:
```
@bf-query 分析一下小米SU7
```

## 消息流

```
用户: @bf-query 分析一下小米SU7
  ↓
OpenClaw 网关 (feishu_im_user_get_messages)
  ↓
写入 .agent_inbox/bf-query/task_xxx.json
  ↓
bf-query Agent (读取文件，处理)
  ↓
写入 .feishu_outbox/xxx.json
  ↓
OpenClaw 网关 (读取文件)
  ↓
feishu_im_user_message 发送到群
```
