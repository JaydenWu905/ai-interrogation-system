# AI警讯笔录系统

## 项目简介
AI警讯笔录系统是一个专为公安审讯场景设计的智能化笔录平台。系统通过AI技术辅助审讯流程，实现语音识别、智能对话引导和案件信息结构化提取，提高审讯效率和记录准确性。

## 核心功能

### 1. 警员身份认证
- 警号密码登录系统
- 支持"记住我"功能（3天/2小时有效期）
- Token验证机制保护API安全

### 2. 智能语音识别
- 集成FunASR大模型（paraformer-zh）
- 支持.wav格式录音文件上传
- 自动语音端点检测和标点预测
- 实时将语音转换为文字

### 3. AI引导审讯流程
- **状态机驱动的智能对话系统**
  - 阶段1：权利义务告知与确认
  - 阶段2：AI自由询问与信息收集
  - 阶段3：笔录结束与确认
- **结构化信息提取**
  - 自动提取案情、时间、地点、嫌疑人等关键信息
  - 实时更新案件信息表

### 4. 案件管理
- 唯一笔录ID生成
- 审讯状态跟踪
- 案件信息结构化存储

## 技术架构

### 后端技术栈
- **框架**: FastAPI (Python 3.8+)
- **AI模型**: FunASR paraformer-zh + fsmn-vad + ct-punc
- **认证**: JWT-like Token验证
- **API文档**: 自动生成OpenAPI文档 (访问 `/docs`)

### 系统架构
```
前端(Electron) → FastAPI后端 → AI模型服务
       ↓               ↓           ↓
   用户界面       业务逻辑层   语音识别/对话
```

## API接口文档

### 认证模块 (`/api/v1/auth`)
- `POST /login` - 警员登录
  ```json
  {
    "police_number": "PC123456",
    "password": "123456",
    "remember_me": true
  }
  ```

### 笔录核心业务 (`/api/v1/records`)
- `POST /start` - 开启新笔录
  ```json
  {
    "reporter_name": "张三",
    "case_type": "盗窃案"
  }
  ```

- `POST /chat` - AI对话交互
  ```json
  {
    "record_id": "abc123",
    "reporter_text": "听明白了"
  }
  ```

### 语音识别模块 (`/api/v1/audio`)
- `POST /speech-to-text` - 语音转文字
  - 上传.wav格式录音文件
  - 返回识别后的文字内容

## 安装与运行

### 环境要求
- Python 3.8+
- pip 包管理工具

### 后端安装步骤
1. 克隆项目
   ```bash
   git clone <repository-url>
   cd ai-interrogation-system/backend
   ```

2. 安装依赖（根据实际requirements.txt）
   ```bash
   pip install fastapi uvicorn funasr
   ```

3. 运行后端服务
   ```bash
   python main.py
   ```

4. 访问API文档
   - OpenAPI文档: http://127.0.0.1:8000/docs
   - 健康检查: http://127.0.0.1:8000/health

### 前端配置
- 前端为Electron桌面应用（待开发）
- 配置API地址为 `http://127.0.0.1:8000`

## 使用示例

### 完整审讯流程
1. **警员登录**
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"police_number":"PC123456","password":"123456"}'
   ```

2. **开始新笔录**
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/v1/records/start" \
        -H "x-token: token_for_PC123456_3days" \
        -H "Content-Type: application/json" \
        -d '{"reporter_name":"张三","case_type":"盗窃案"}'
   ```

3. **语音识别（上传录音）**
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/v1/audio/speech-to-text" \
        -H "x-token: token_for_PC123456_3days" \
        -F "file=@record_out.wav"
   ```

4. **AI对话交互**
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/v1/records/chat" \
        -H "x-token: token_for_PC123456_3days" \
        -H "Content-Type: application/json" \
        -d '{"record_id":"abc123","reporter_text":"听明白了"}'
   ```

## 项目结构
```
ai-interrogation-system/
├── backend/                    # 后端代码
│   ├── main.py                # FastAPI应用入口
│   ├── requirements.txt       # Python依赖
│   ├── test_asr.py           # 语音识别测试
│   └── app/
│       ├── api/
│       │   ├── deps.py       # 依赖项（token验证）
│       │   └── routers/      # API路由
│       │       ├── audio.py  # 语音识别接口
│       │       ├── record.py # 笔录核心业务
│       │       └── user.py   # 用户认证接口
│       ├── schemas/          # Pydantic数据模型
│       │   ├── record.py     # 笔录相关模型
│       │   └── user.py       # 用户相关模型
│       └── services/         # 业务服务层
├── frontend/                  # 前端代码（待开发）
└── README.md                 # 项目说明文档
```

## 未来规划

### 短期改进
1. 集成真实数据库（SQLite/PostgreSQL）
2. 实现完整的案件管理功能
3. 添加录音文件管理

### 长期规划
1. 集成DeepSeek等大模型进行智能对话
2. 开发Electron桌面前端应用
3. 支持多语言识别
4. 添加实时语音流识别
5. 实现案件分析和报告生成

## 注意事项
1. 当前版本使用模拟数据库，生产环境需替换为真实数据库
2. 密码存储应使用加密哈希（当前为演示用途）
3. Token验证为简化版本，生产环境应使用JWT
4. 语音识别模型首次运行会自动下载，请确保网络连接

## 贡献指南
欢迎提交Issue和Pull Request来改进本项目。

## 许可证
[待添加]
