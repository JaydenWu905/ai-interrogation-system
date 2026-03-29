from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 引入我们刚才写的业务路由
from app.api.routers import record

# 1. 实例化 FastAPI，这里的 title 和 description 会直接展示在接口文档的网页头上！
app = FastAPI(
    title="AI 警讯笔录系统 API",
    description="用于支撑前端 Electron 桌面的核心后端接口，包含大模型对话流控制与信息提取。",
    version="1.0.0"
)

# 2. 配置 CORS 跨域（非常重要，保证前端能调通）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许 GET, POST, PUT, DELETE 等所有方法
    allow_headers=["*"],  # 允许所有请求头
)

# 3. 注册路由 (把传菜员挂载到主程序上)
# 这样 record 里的接口就会加上 /api/v1 的前缀，比如 /api/v1/records/start
app.include_router(record.router, prefix="/api/v1")

# 4. 系统健康检查接口（用来确认后端活没活着）
@app.get("/health", tags=["系统服务"])
def health_check():
    return {
        "code": 200, 
        "message": "后端服务运行正常！",
        "data": {"status": "Running"}
    }

# 5. 根路径重定向提示
@app.get("/", include_in_schema=False)
def root():
    return {"message": "欢迎使用 AI 警讯笔录系统，请访问 /docs 查看 API 文档。"}

# 6. 启动服务器
if __name__ == "__main__":
    # 使用 uvicorn 启动，host="0.0.0.0" 允许局域网访问，reload=True 开启热更新
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)