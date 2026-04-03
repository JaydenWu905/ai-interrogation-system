from pydantic import BaseModel, Field

# 1. 前端发给我们的：登录请求包
class LoginRequest(BaseModel):
    # 这里先用 police_number 示范，以后如果想加普通账号，可以再加一个字段
    police_number: str = Field(..., description="警号/账号", example="PC123456")
    password: str = Field(..., description="登录密码", example="123456")
    remember_me: bool = Field(False, description="是否记住登录状态", example=True)

# 2. 我们返回给前端的：用户信息
class UserInfo(BaseModel):
    police_number: str = Field(..., description="警号")
    name: str = Field(..., description="警官姓名")
    department: str = Field(..., description="所属部门")

# 3. 我们返回给前端的：完整的登录响应包
class LoginResponse(BaseModel):
    token: str = Field(..., description="身份令牌(前端以后每次请求都要带上它)")
    expires_in: int = Field(..., description="Token有效时间（秒）")
    user: UserInfo = Field(..., description="登录成功后的警官基本信息")