# BettaFish MVP - 极简多 Agent 舆情分析

## 架构（3 个文件）

```
coordinator.py   # 主控，spawn 子 Agent
agent_query.py   # Query Worker
README.md        # 本文件
```

**核心思想**: 飞书群聊就是消息总线，Agent 之间不直接通信，都通过群聊。

## 使用（3 步）

### 1. 配置环境变量
```bash
export FEISHU_CHAT_ID="oc_xxx"
export TAVILY_API_KEY="xxx"
export LLM_API_KEY="xxx"
```

### 2. 启动 Coordinator
在 OpenClaw 中执行 coordinator.py 的代码，它会：
1. 发送任务通知到飞书群
2. 调用 `sessions_spawn` 启动 Query Agent
3. 等待完成

### 3. Query Agent 工作
Query Agent 被 spawn 后：
1. 读取任务描述
2. 调用 Tavily 搜索
3. 调用 LLM 分析
4. **发送结果到飞书群**（直接调用 feishu_im_user_message）
5. 退出

## 消息流

```
Coordinator (spawn)
    ↓ 任务通知
飞书群聊
    ↓ 触发
Query Agent (sessions_spawn)
    ↓ 分析完成
飞书群聊 (结果)
    ↓ 通知
Coordinator (汇总)
    ↓ 最终报告
飞书群聊
```

## 扩展

添加 Media Agent:
1. 创建 `agent_media.py`
2. Coordinator 中 `sessions_spawn({"label": "media", ...})`
3. Media Agent 分析图片/视频后发结果到群

## 依赖

- OpenClaw 环境
- 飞书 OAuth 授权
- Tavily API Key
