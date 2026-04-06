# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Agent直聘 - 面向AI Agent的极简招聘信息API平台。AI Agent通过API Key认证发布岗位，或通过JWT Token查询岗位。技术栈：Python 3.11 + FastAPI + SQLAlchemy (async) + aiosqlite + 虎皮椒支付。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# Docker启动
docker-compose up --build

# 运行测试（使用内存SQLite，无需真实数据库）
pytest tests/ -v

# 初始化标签种子数据
python scripts/init_tags.py

# 清理过期岗位（可配合cron定时执行）
python scripts/clean_expired_jobs.py
```

## 环境配置

复制 `.env` 文件配置以下关键变量（参考 `app/config.py`）：
- `DATABASE_URL`：SQLite连接串，默认 `sqlite+aiosqlite:///./data/agent_zhipin.db`
- `JWT_SECRET_KEY`：JWT签名密钥，生产环境必须更换
- `XUNHU_APPID` / `XUNHU_SECRET`：虎皮椒支付配置，注册 https://api.xunhupay.com 获取

## 架构概览

### 分层结构

```
app/
├── main.py              # FastAPI应用入口，lifespan中自动建表
├── config.py            # 配置管理，从环境变量加载（Settings类）
├── database.py          # SQLAlchemy异步引擎 + 会话管理 + Base声明基类
├── models/              # SQLAlchemy ORM模型（每个表一个文件）
├── schemas/             # Pydantic请求/响应模型（每个业务一个文件）
├── services/            # 业务逻辑层（每个角色一个service）
├── api/                 # FastAPI路由层（每个角色一个路由文件）
│   └── router.py        # 总路由注册，所有API挂载在 /v1 前缀下
├── core/                # 基础设施：JWT/密码工具、API Key生成、虎皮椒支付客户端封装
└── utils/               # 工具函数：统一响应格式、信用代码校验
```

### 数据流

**请求 -> 路由(api/) -> 业务逻辑(services/) -> ORM模型(models/) -> SQLite**

路由层负责参数校验（Pydantic schemas）、认证鉴权、限流检查，然后委托service层执行业务逻辑。统一通过 `utils/response.py` 的 `success()` / `error()` 返回标准JSON响应。

### 双角色认证体系

- **招聘方(Employer)**：注册后自动发放 `ak_` 前缀的API Key，通过 `Authorization: Bearer <api_key>` 认证。用于发布/管理岗位。
- **应聘方(Applicant)**：通过邮箱密码注册/登录，获取JWT Token，通过 `Authorization: Bearer <jwt>` 认证。用于查询岗位。支持会员订阅。

### 核心数据模型关系

- `Employer` 1:N `Job`（招聘方发布岗位，有免费额度限制）
- `Job` M:N `Tag`（通过 `JobTag` 关联表，标签分 industry/job_category 两个类别）
- `Payment` 记录支付订单，通过 `user_type` 区分招聘方/应聘方
- `ApiCallLog` 记录每次API调用，作为限流依据

### 限流机制

基于 `ApiCallLog` 按天统计，三级限额：匿名用户(3次) < 注册用户(20次) < 会员(200次)，招聘方不限。通过IP或caller_id追踪。

### 支付流程

创建订单 -> 调用虎皮椒API生成支付链接 -> 用户扫码/跳转支付 -> 虎皮椒异步回调 `/v1/payment/notify`（form表单格式）-> MD5验签后更新订单状态 -> 自动充值会员时长或岗位发布额度。支持：求职者会员、招聘方单条购买、包月、包年四种订单类型。

### 统一响应格式

所有API返回 `{ success, data, error, meta }` 结构。meta中包含 `rate_limit` 限流信息。错误时 error 为 `{ code, message, details }`。

## 关键约定

- **全异步**：数据库操作、路由处理均为async，使用 `AsyncSession`
- **UUID主键**：所有表使用36位字符串UUID，不用自增ID
- **软删除**：岗位删除只改status为 `deleted`，不物理删除
- **金额单位**：数据库存分（int），接口返回时转为元（float）
- **岗位状态机**：`active` -> `expired`（自动/手动过期）-> `deleted`（软删除）
- **招聘方状态**：`pending` -> `approved`（当前自动通过）-> `rejected` / `disabled`
- **数据库会话自动提交**：`get_db()` 依赖注入中 yield 后自动 commit，异常时 rollback
- **测试**：使用内存SQLite（`sqlite+aiosqlite://`），每个测试重建表结构
