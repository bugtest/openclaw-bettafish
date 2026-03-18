# BettaFish - 独立 Agent + 文件消息总线

## 架构

```
飞书群聊
    ↑↓
OpenClaw 网关 (gateway.py)  ← 在 OpenClaw 会话中运行
    ↑↓ 通过文件交换
Agent 进程 (coordinator.py, agent_query.py)  ← 独立运行
```

## 文件总线

| 目录 | 用途 | 写入者 | 读取者 |
|------|------|--------|--------|
| `.feishu_outbox/` | Agent 要发送到飞书的消息 | Agent | 网关 |
| `.feishu_inbox/` | 飞书消息/Agent 完成通知 | 网关 | Agent |
| `.agent_inbox/<agent>/` | 分配给 Agent 的任务 | 网关 | Agent |

## 启动步骤

### 1. 启动网关（在 OpenClaw 会话中）
```python
# 修改 CHAT_ID 为你的群聊 ID
CHAT_ID = "oc_xxx"

# 然后执行 gateway.py 的代码
```

### 2. 启动 Coordinator Agent
```python
sessions_spawn({
    "label": "bf-coordinator",
    "task": "python /workspace/projects/workspace/skills/openclaw-bettafish/coordinator.py",
    "mode": "session",
    "thread": true
})
```

### 3. 启动 Query Agent
```python
sessions_spawn({
    "label": "bf-query",
    "task": "python /workspace/projects/workspace/skills/openclaw-bettafish/agent_query.py",
    "mode": "session",
    "thread": true
})
```

## 使用流程

```
1. 用户在飞书群: "@bf-query 分析一下小米SU7"

2. OpenClaw 网关:
   - 接收飞书消息
   - 写入 .agent_inbox/bf-query/task_xxx.json

3. Query Agent:
   - 轮询 .agent_inbox/bf-query/
   - 发现任务，开始处理
   - 发送进度消息: 写入 .feishu_outbox/

4. OpenClaw 网关:
   - 轮询 .feishu_outbox/
   - 读取消息文件
   - 调用 feishu_im_user_message 发送到群

5. Query Agent 完成:
   - 写入 .feishu_inbox/complete_sess_xxx.json
   - Coordinator 检测到完成，生成报告
```

## 消息格式

### Agent 发送消息
```json
// .feishu_outbox/<agent>_<timestamp>.json
{
  "agent": "bf-query",
  "text": "分析完成...",
  "timestamp": "2026-03-18T12:00:00"
}
```

### 分配给 Agent 的任务
```json
// .agent_inbox/bf-query/task_<timestamp>.json
{
  "type": "task_assign",
  "session_id": "sess-xxx",
  "query": "小米SU7舆情分析",
  "timestamp": "2026-03-18T12:00:00"
}
```

### Agent 完成通知
```json
// .feishu_inbox/complete_sess_xxx_bf-query.json
{
  "type": "agent_complete",
  "session_id": "sess-xxx",
  "agent": "bf-query",
  "result": "分析结果..."
}
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `gateway.py` | OpenClaw 侧网关，桥接飞书 API 和文件总线 |
| `coordinator.py` | 协调器 Agent，负责创建 session 和汇总 |
| `agent_query.py` | Query Worker，执行搜索分析 |

## 待完善

需要在 `gateway.py` 中实现：
1. `feishu_im_user_message` 实际调用（发送消息到群）
2. `feishu_im_user_get_messages` 实际调用（获取群消息）

当前使用文件作为消息队列，Agent 和 OpenClaw 解耦。
