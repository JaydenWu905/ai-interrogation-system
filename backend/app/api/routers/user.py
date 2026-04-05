from fastapi import APIRouter, HTTPException,Depends
from sqlmodel import Session, select

# 引入契约（用于校验输入输出）
from app.schemas.user import LoginRequest, LoginResponse, UserInfo
# 引入数据库模型和连接工具
from app.models import User
from app.database import get_session
router = APIRouter(prefix="/auth", tags=["权限与登录模块"])

@router.post("/login", response_model=LoginResponse, summary="警员登录接口")
async def login(
    req: LoginRequest, 
    session: Session = Depends(get_session)  # <--- 挂上数据库连接的“依赖”
):
    """
    警员登录：去真实的 SQLite 数据库中核对警号和密码
    """
    # 1. 拿着前端传来的警号，去真实数据库里捞人！
    # 这行代码等同于 SQL 语句: SELECT * FROM user WHERE police_number = 'PC123456'
    statement = select(User).where(User.police_number == req.police_number)
    db_user = session.exec(statement).first() #这行代码会返回一个 User 对象，或者 None(没这个人)
    
    # 2. 查无此人，或者密码对不上
    if not db_user or db_user.password != req.password:
        raise HTTPException(status_code=401, detail="警号或密码错误，请重试！")
    
    # 3. 登录成功，签发 Token (这部分“记住我”的逻辑完全不用动)
    if req.remember_me:
        expire_seconds = 3 * 24 * 60 * 60
        fake_token = f"token_for_{req.police_number}_3days"
    else:
        expire_seconds = 2 * 60 * 60
        fake_token = f"token_for_{req.police_number}_2hours"
    
    # 4. 把从数据库里捞出来的真实姓名和部门，打包返回给前端
    return LoginResponse(
        token=fake_token,
        expires_in=expire_seconds,
        user=UserInfo(
            police_number=db_user.police_number,
            name=db_user.name,              # <--- 直接读取数据库对象的属性
            department=db_user.department   # <--- 直接读取数据库对象的属性
        )
    )