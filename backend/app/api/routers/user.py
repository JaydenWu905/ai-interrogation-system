from fastapi import APIRouter, HTTPException
from app.schemas.user import LoginRequest, LoginResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["权限与登录模块"])

# 【临时模拟】假装这是你的 SQLite 数据库里的用户表
MOCK_USER_DB = {
    "PC123456": {
        "password": "123456",  # 实际开发中密码绝对不能明文存储，这里仅做演示！
        "name": "张警官",
        "department": "刑侦大队"
    }
}

@router.post("/login", response_model=LoginResponse, summary="警员登录接口")
async def login(req: LoginRequest):
    user_record = MOCK_USER_DB.get(req.police_number)
    
    if not user_record or user_record["password"] != req.password:
        raise HTTPException(status_code=401, detail="警号或密码错误，请重试！")
    
    # 【新增核心逻辑】：判断是否勾选了“记住我”
    if req.remember_me:
        # 勾选了：有效期 3 天 (3天 * 24小时 * 60分 * 60秒 = 259200秒)
        expire_seconds = 3 * 24 * 60 * 60
        fake_token = f"token_for_{req.police_number}_3days"
    else:
        # 没勾选：默认有效期 2 小时 (2小时 * 60分 * 60秒 = 7200秒)
        expire_seconds = 2 * 60 * 60
        fake_token = f"token_for_{req.police_number}_2hours"
    
    return LoginResponse(
        token=fake_token,
        expires_in=expire_seconds, # 把过期时间告诉前端
        user=UserInfo(
            police_number=req.police_number,
            name=user_record["name"],
            department=user_record["department"]
        )
    )