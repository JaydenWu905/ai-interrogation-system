from fastapi import Header, HTTPException

# 这就是我们的“保安”函数
async def verify_token(x_token: str = Header(..., description="请填入登录获取的 Token 字符串")):
    """
    检查前端请求头中是否携带了合法的 Token
    """
    # 模拟简单的校验逻辑：只要你的 token 是以 "token_for_" 开头的，我就认
    if not x_token.startswith("token_for_"):
        raise HTTPException(
            status_code=401, 
            detail="无效的通行证或通行证已过期，请重新登录！"
        )
    
    # 如果验证通过，就把 token 原封不动地放行
    return x_token