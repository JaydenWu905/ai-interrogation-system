from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 实例化 FastAPI
app = FastAPI(title="AI 警讯笔录系统后端")

# 配置 CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 写一个最简单的测试接口
@app.get("/health")
def health_check():
    return {
        "code": 200, 
        "message": "太棒了，FastAPI 后端已成功启动！",
        "data": {"status": "Running", "version": "0.1"}
    }

# 启动服务器
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)