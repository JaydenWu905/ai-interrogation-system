import json
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from openai import AsyncOpenAI
from app.models import Record
from app.database import get_session
from app.api.deps import verify_token
from app.schemas.record import RecordStartRequest, ChatRequest, ChatResponse

router = APIRouter(prefix="/records", tags=["AI笔录核心业务"])


# 固定话术定义
FIXED_OPENING = "我们是xx区公安分局刑警大队的民警（出示人民警察证），现依法向你询问有关问题。根据刑事诉讼法的有关规定，你应当如实提供证据、证言，如果有意作伪证或者隐匿罪证的，要负法律责任。你明白吗？"
FIXED_CLOSING = "你还有什么需要补充说明的吗？如果以上笔录核对无误，请仔细阅读后签名按手印。"

@router.post("/start", summary="1. 开启新笔录 (播报开场固定内容)")
async def start_record(
    req: RecordStartRequest, 
    token: str = Depends(verify_token),
    session: Session = Depends(get_session) # 接入数据库管家
):
    parts = token.split("_")
    police_number = parts[2] if len(parts) >= 3 else "unknown_police"
    
    # 初始化的 JSON 字符串
    init_info = json.dumps({
        "案情": "", "发生时间": "", "发生地点": "", "嫌疑人信息": ""
    }, ensure_ascii=False)

    # 1. 在真实数据库里初始化这条笔录
    new_record = Record(
        police_number=police_number,
        title="AI智能笔录",
        content=f"AI警官：{FIXED_OPENING}", # 开局第一句话直接记入聊天记录
        status="等待权利义务确认",
        extracted_info=init_info
    )
    
    session.add(new_record)
    session.commit()
    session.refresh(new_record)
    
    return {
        "code": 200,
        "message": "笔录初始化成功",
        "data": {
            "record_id": new_record.id, # 返回真实的数据库ID
            "ai_reply": FIXED_OPENING,
            "status": new_record.status
        }
    }

DEEPSEEK_API_KEY = "sk-cc4fb462867446d78ad8b6beb1f85c8f" 
client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY, 
    base_url="https://api.deepseek.com" # 魔法：把对讲机频段调到 DeepSeek
)

@router.post("/chat", response_model=ChatResponse, summary="2. 核心对话流 (大模型接管)")
async def chat_with_ai(
    req: ChatRequest, 
    token: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    # 1. 查出数据库中的笔录记录
    db_record = session.get(Record, req.record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="找不到该笔录ID")

    user_text = req.reporter_text
    current_status = db_record.status
    extracted_info = db_record.extracted_info # 这是之前的 JSON 字符串

    # 2. 将嫌疑人的最新发言追加到长篇对话记录中
    db_record.content += f"\n嫌疑人：{user_text}"

    # ============== 🤖 大模型核心工作区 ============== #
    
    # 撰写发给大模型的“系统提示词”
    system_prompt = f"""
    你是一名经验丰富的中国刑警。当前案件审讯状态为：【{current_status}】。
    你目前已经掌握的线索是：{extracted_info}
    
    你的任务是仔细阅读我接下来发给你的完整聊天记录，然后：
    1. 根据嫌疑人最新的话，给出你作为警察的下一句合理回应或追问。
    2. 如果当前状态是'等待权利义务确认'，且嫌疑人表示明白，你需要把状态改为'AI询问中'并开始询问案情；如果他说没有补充了，状态改为'笔录结束'并输出固定结语。
    3. 整合嫌疑人提到的最新线索，更新已有线索（案情、时间、地点、嫌疑人特征）。如果未提到，保持原样。

    【极度重要】：你必须且只能回复一个合法的 JSON 数据包！不要包裹在 markdown 代码块里，直接输出 JSON！
    必须严格包含以下三个字段：
    {{
        "ai_reply": "你对嫌疑人说的话",
        "new_status": "案件的新状态",
        "extracted_info": {{
            "案情": "...",
            "发生时间": "...",
            "发生地点": "...",
            "嫌疑人信息": "..."
        }}
    }}
    """

    try:
        # 调用 DeepSeek 大模型
        response = await client.chat.completions.create(
            model="deepseek-chat", # 使用 DeepSeek 对话模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"以下是完整的聊天记录，请分析并给出下一步回应：\n{db_record.content}"}
            ],
            response_format={"type": "json_object"}, # 强制要求模型输出 JSON 格式
            temperature=0.3 # 温度调低点，让警察显得严谨、不啰嗦
        )
        
        # 提取模型回复的文本内容
        ai_response_text = response.choices[0].message.content
        
        # 将模型回复的 JSON 字符串反序列化为 Python 字典
        result_data = json.loads(ai_response_text)
        
        ai_reply = result_data.get("ai_reply", "抱歉，系统处理出现异常。")
        new_status = result_data.get("new_status", current_status)
        new_extracted_info = result_data.get("extracted_info", {})
        
    except Exception as e:
        print(f"大模型调用失败: {e}")
        raise HTTPException(status_code=500, detail="AI 大脑暂时开小差了，请稍后再试。")

    # ============== 收尾，保存入库 ============== #
    
    # 1. 把 AI 的回复记入长篇聊天记录
    db_record.content += f"\nAI警官：{ai_reply}"
    
    # 2. 更新状态和线索
    db_record.status = new_status
    db_record.extracted_info = json.dumps(new_extracted_info, ensure_ascii=False)
    
    # 3. 提交给硬盘永久保存
    session.add(db_record)
    session.commit()

    return ChatResponse(
        ai_reply=ai_reply,
        status=db_record.status,
        extracted_info=new_extracted_info
    )