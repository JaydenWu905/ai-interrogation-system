import json
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
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

@router.post("/chat", response_model=ChatResponse, summary="2. 核心对话流 (根据状态自动流转)")
async def chat_with_ai(
    req: ChatRequest, 
    token: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    # 1. 去数据库查一下当前这个案件
    db_record = session.get(Record, req.record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="找不到该笔录ID，请先调用 start 接口创建")

    user_text = req.reporter_text
    current_status = db_record.status
    # 把数据库里的字符串，反解析成 Python 字典，方便修改
    extracted_info = json.loads(db_record.extracted_info)
    
    # 无论说什么，先把嫌疑人的原话记入长篇聊天记录 (content)
    db_record.content += f"\n嫌疑人：{user_text}"
    
    ai_reply = ""

    # ============== 状态机核心逻辑 (原汁原味保留) ============== #
    
    if current_status == "等待权利义务确认":
        if "不明白" in user_text or "不知道" in user_text or "不清楚" in user_text:
            ai_reply = "如果你对刚才宣读的权利和义务有疑问，我可以为你重新解释一遍。请问需要重播吗？"
        elif "明白" in user_text or "知道" in user_text or "清楚" in user_text:
            db_record.status = "AI询问中"  # 状态晋级！
            ai_reply = "好的，请你详细叙述一下案件发生的经过。"
        else:
            ai_reply = "你需要明确回答“明白”或“不明白”。请问你清楚刚才宣读的权利和义务了吗？"

    elif current_status == "AI询问中":
        if "没有了" in user_text or "就这些" in user_text:
            db_record.status = "笔录结束"
            ai_reply = FIXED_CLOSING
        else:
            # 模拟追加案情
            extracted_info["案情"] += user_text + " "
            ai_reply = "你提到的情况我已经记录。请继续补充案发的具体时间和地点，以及嫌疑人的长相特征？"

    else:
        ai_reply = "本次笔录已结束，感谢您的配合。"

    # ============== 结束处理，保存入库 ============== #
    
    # 1. 把 AI 的回复也记入长篇聊天记录
    db_record.content += f"\nAI警官：{ai_reply}"
    
    # 2. 把修改后的字典，重新打包成字符串存回数据库
    db_record.extracted_info = json.dumps(extracted_info, ensure_ascii=False)
    
    # 3. 提交给硬盘永久保存
    session.add(db_record)
    session.commit()

    return ChatResponse(
        ai_reply=ai_reply,
        status=db_record.status,
        extracted_info=extracted_info
    )