# BettaFish - 独立 Agent + 飞书消息总线

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     飞书群聊 (消息总线)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │  用户: "分析一下小米SU7"                               │  │
│  │     ↓                                                 │  │
│  │  Coordinator: "📋 新任务 @QueryAgent 请分析"           │  │
│  │     ↓                                                 │  │
│  │  QueryAgent: "🔍 搜索中..."                           │  │
│  │     ↓                                                 │  │
│  │  QueryAgent: "✅ 分析完成: ..."                       │  │
│  │     ↓                                                 │  │
│  │  Coordinator: "📊 最终报告"                           │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↑                                    ↑
         │                                    │
   ┌─────┴──────┐                    ┌───────┴──────┐
   │Coordinator │◄──── 无直接通信 ───►│  QueryAgent  │
   │(独立Agent) │                    │ (独立Agent)  │
   └────────────┘                    └──────────────┘
```

**核心**: Agent 之间不直接通信，都通过飞书群聊消息中转。

## 文件说明

| 文件 | 角色 | 功能 |
|------|------|------|
| `coordinator.py` | Coordinator Agent | 监听群消息 -> 发现任务 -> 分配 -> 汇总报告 |
| `agent_query.py` | Worker Agent | 监听群消息 -> 发现分配 -> 执行 -> 发结果 |

## 启动方式

### 1. 启动 Coordinator
```python
sessions_spawn({
    "label": "bf-coordinator",
    "task": "python /workspace/projects/workspace/skills/openclaw-bettafish/coordinator.py",
    "mode": "session",
    "thread": true
})
```

### 2. 启动 Query Agent
```python
sessions_spawn({
    "label": "bf-query",
    "task": "python /workspace/projects/workspace/skills/openclaw-bettafish/agent_query.py",
    "mode": "session",
    "thread": true
})
```

### 3. 在飞书群里使用
```
用户: @Coordinator 分析一下小米SU7的舆情

Coordinator: 📋 新分析任务
             Session: sess-xxx
             查询: 小米SU7舆情
             @QueryAgent 请进行网络搜索分析

QueryAgent:  🔍 开始处理 Session:sess-xxx
             【首次总结】找到 5 条信息
             🤔 反思搜索...
             ✅ 分析完成
             分析内容...

Coordinator: 📊 舆情分析报告
             查询: 小米SU7舆情
             状态: ✅ 完成
```

## 消息协议

### 任务分配
```
[Coordinator] @QueryAgent 请分析 "小米SU7"
              Session: sess-xxx
```

### 进度更新
```
[QueryAgent] 🔍 首次搜索...
[QueryAgent] 【首次总结】找到 N 条信息
```

### 结果提交
```
[QueryAgent] ✅ 分析完成 Session:sess-xxx
              
              分析内容...
              
              @QueryAgent 任务完成
```

## 扩展

添加 Media Agent:
1. 创建 `agent_media.py`
2. 同样的监听模式
3. Coordinator 分配任务时 @MediaAgent
4. Media Agent 完成后发结果到群

## 优缺点

| 优点 | 缺点 |
|------|------|
| Agent 独立运行，可单独重启 | 需要飞书 API 调用 |
| 可跨网关部署 | 消息有延迟 (~秒级) |
| 人可直接观察/介入 | 需要轮询群消息 |
| 结果自动沉淀在群聊历史 | 状态管理稍复杂 |

## 待实现

需要用户补充飞书 API 调用:
- `coordinator.py` 中的 `send_msg()` 和消息获取
- `agent_query.py` 中的 `send_msg()` 和任务解析
