from fastapi import APIRouter, HTTPException
from app.schemas.record import RecordStartRequest, ChatRequest, ChatResponse
import uuid

router = APIRouter(prefix="/records", tags=["AI笔录核心业务"])

# 【核心】临时模拟数据库，用来记忆每个案件进行到了哪一步
MOCK_DB = {}

# 固定话术定义
FIXED_OPENING = "我们是xx区公安分局刑警大队的民警（出示人民警察证），现依法向你询问有关问题。根据刑事诉讼法的有关规定，你应当如实提供证据、证言，如果有意作伪证或者隐匿罪证的，要负法律责任。你明白吗？"
FIXED_CLOSING = "你还有什么需要补充说明的吗？如果以上笔录核对无误，请仔细阅读后签名按手印。"

@router.post("/start", summary="1. 开启新笔录 (播报开场固定内容)")
async def start_record(req: RecordStartRequest):
    # 随机生成一个简短的档案ID
    record_id = str(uuid.uuid4())[:6] 
    
    # 在数据库中初始化这条笔录的状态
    MOCK_DB[record_id] = {
        "status": "等待权利义务确认", # 初始状态
        "extracted_info": {
            "案情": "",
            "发生时间": "",
            "发生地点": "",
            "嫌疑人信息": ""
        }
    }
    
    return {
        "code": 200,
        "message": "笔录初始化成功",
        "data": {
            "record_id": record_id,
            "ai_reply": FIXED_OPENING,
            "status": MOCK_DB[record_id]["status"]
        }
    }

@router.post("/chat", response_model=ChatResponse, summary="2. 核心对话流 (根据状态自动流转)")
async def chat_with_ai(req: ChatRequest):
    # 1. 去数据库查一下当前这个案件的状态
    record = MOCK_DB.get(req.record_id)
    if not record:
        raise HTTPException(status_code=404, detail="找不到该笔录ID，请先调用 start 接口创建")

    user_text = req.reporter_text
    current_status = record["status"]
    
    # ============== 状态机核心逻辑 ============== #
    
    # 状态 1：等待报案人确认权利义务
    if current_status == "等待权利义务确认":
        # 1. 先拦截“否定”回答
        if "不明白" in user_text or "不知道" in user_text or "不清楚" in user_text:
            return ChatResponse(
                ai_reply="如果你对刚才宣读的权利和义务有疑问，我可以为你重新解释一遍。请问需要重播吗？",
                status=current_status, # 状态不晋级，继续卡在这里
                extracted_info=record["extracted_info"]
            )
            
        # 2. 再匹配“肯定”回答
        elif "明白" in user_text or "知道" in user_text or "清楚" in user_text:
            record["status"] = "AI询问中"  # 状态晋级！
            return ChatResponse(
                ai_reply="好的，请你详细叙述一下案件发生的经过。",
                status=record["status"],
                extracted_info=record["extracted_info"]
            )
            
        # 3. 处理瞎扯或者模棱两可的回答
        else:
            return ChatResponse(
                ai_reply="你需要明确回答“明白”或“不明白”。请问你清楚刚才宣读的权利和义务了吗？",
                status=current_status, # 状态不晋级
                extracted_info=record["extracted_info"]
            )
            
    # 状态 2：AI 自由询问与信息提取阶段
    elif current_status == "AI询问中":
        # 【未来这里会替换成调用 DeepSeek 大模型的代码】
        # 这里用 Mock 逻辑演示：如果报案人说“没有了”，触发固定收尾
        if "没有了" in user_text or "就这些" in user_text:
            record["status"] = "笔录结束" # 状态完结！
            return ChatResponse(
                ai_reply=FIXED_CLOSING,
                status=record["status"],
                extracted_info=record["extracted_info"]
            )
        else:
            # 模拟大模型正在工作，把报案人的话填进 JSON 表格里
            record["extracted_info"]["案情"] = user_text 
            return ChatResponse(
                ai_reply="你提到的情况我已经记录。请继续补充案发的具体时间和地点，以及嫌疑人的长相特征？",
                status=record["status"],
                extracted_info=record["extracted_info"]
            )
            
    # 状态 3：笔录已经结束
    else:
        return ChatResponse(
            ai_reply="本次笔录已结束，感谢您的配合。",
            status=record["status"],
            extracted_info=record["extracted_info"]
        )