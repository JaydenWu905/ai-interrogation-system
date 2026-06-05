from pydantic import BaseModel, Field
from typing import Dict


# 1. 请求：新建笔录
class RecordStartRequest(BaseModel):
    case_type: str = Field(default="盗窃案", description="案件类型")
    case_name: str = Field(default="", description="案件名称", example="手机被盗案")
    person_type: str = Field(default="", description="被询问人身份", example="证人")
    person_name: str = Field(default="", description="被询问人姓名", example="张三")
    id_type: str = Field(default="", description="证件类型", example="居民身份证")
    id_number: str = Field(default="", description="证件号码", example="110101199001011234")


# 2. 请求：发送报案人语音转出的文字
class ChatRequest(BaseModel):
    record_id: int = Field(..., description="当前笔录的唯一标识ID", example=1001)
    reporter_text: str = Field(..., description="报案人说的文字", example="听明白了。")


# 3. 响应：AI 的回复与当前提取的信息
class ChatResponse(BaseModel):
    ai_reply: str = Field(..., description="AI下一步要播报的语音文字")
    status: str = Field(..., description="当前所处阶段：等待确认/AI询问中/笔录结束")
    extracted_info: Dict[str, str] = Field(..., description="AI实时提取的关键信息")


class ChatAudioResponse(ChatResponse):
    transcript: str = Field(..., description="语音识别得到的被询问人文本")
