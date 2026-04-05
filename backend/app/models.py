from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# 1. 警员表 (User)
# table=True 的意思是：这不仅仅是个数据校验格式，还要真正在数据库里建一张表！
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    police_number: str = Field(unique=True, index=True, description="警号/账号")
    password: str = Field(description="密码 (开发阶段暂存明文)")
    name: str = Field(description="警官姓名")
    department: str = Field(description="所属部门")

# 2. 笔录表 (Record)
class Record(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    police_number: str = Field(index=True, description="是谁建立的这份笔录")
    title: str = Field(default="未命名笔录", description="笔录标题")
    content: str = Field(default="", description="笔录的完整聊天记录")
    status: str = Field(default="等待权利义务确认", description="当前案件状态")
    extracted_info: str = Field(
        default='{"案情": "", "发生时间": "", "发生地点": "", "嫌疑人信息": ""}', 
        description="提取的结构化信息 (JSON字符串格式)"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")