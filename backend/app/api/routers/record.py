import json
from typing import List, Tuple

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from openai import AsyncOpenAI

from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from app.models import Record, RecordCreateInfo
from app.database import get_session
from app.api.deps import verify_token
from app.schemas.record import RecordStartRequest, ChatRequest, ChatResponse
from app.prompts import get_interrogation_prompt

router = APIRouter(prefix="/records", tags=["AI笔录核心业务"])


STATUS_WITNESS_OPENING_1 = "证人_告知如实作证义务"
STATUS_WITNESS_OPENING_2 = "证人_告知书阅读确认"
STATUS_WITNESS_OPENING_3 = "证人_确认健康状况"
STATUS_WITNESS_OPENING_4 = "证人_确认可接受询问"
STATUS_WITNESS_OPENING_5 = "证人_采集个人信息"
STATUS_AI_ASKING = "AI询问中"
STATUS_MANUAL_INTERVENTION = "人工干预"
STATUS_FINISHED = "笔录结束"

OPENING_STEPS = {
    STATUS_WITNESS_OPENING_1: "我们是新城区公安分局刑警大队的民警（出示人民警察证），现依法向你询问有关问题。根据刑事诉讼法的有关规定，你应当如实提供证据、证言，如果有意作伪证或者隐匿罪证的，要负法律责任。你明白吗？",
    STATUS_WITNESS_OPENING_2: "这是《证人诉讼权利义务告知书》，交给你收执并阅读，你如果不识字，我们可以读给你听？",
    STATUS_WITNESS_OPENING_3: "你是否患有严重疾病或其他不适宜作证的情况？",
    STATUS_WITNESS_OPENING_4: "你现在头脑是否清醒，能够接受公安机关的询问？",
    STATUS_WITNESS_OPENING_5: "你的个人情况？请陈述姓名、性别、民族、出生日期、住址、身份证号、联系方式等。"
}
FIXED_CLOSING = "你还有什么需要补充说明的吗？如果以上笔录核对无误，请仔细阅读后签名按手印。"


client = AsyncOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)


def contains_any(text: str, keywords: List[str]) -> bool:
    normalized_text = text.strip()
    return any(keyword in normalized_text for keyword in keywords)


def contains_none(text: str, keywords: List[str]) -> bool:
    normalized_text = text.strip()
    return not any(keyword in normalized_text for keyword in keywords)


def is_clear_yes(text: str, yes_keywords: List[str], deny_keywords: List[str]) -> bool:
    normalized_text = text.strip()
    return contains_any(normalized_text, yes_keywords) and contains_none(normalized_text, deny_keywords)


def is_clear_no(text: str, no_keywords: List[str], exclude_keywords: List[str]) -> bool:
    normalized_text = text.strip()
    return contains_any(normalized_text, no_keywords) and contains_none(normalized_text, exclude_keywords)


def parse_extracted_info(extracted_info: str) -> dict:
    try:
        return json.loads(extracted_info) if extracted_info else {}
    except json.JSONDecodeError:
        return {}


def build_initial_extracted_info(req: RecordStartRequest) -> dict:
    return {
        "姓名": req.person_name.strip(),
        "性别": "",
        "民族": "",
        "出生日期": "",
        "住址": "",
        "身份证号": req.id_number.strip() if req.id_type.strip() in ["身份证", "居民身份证"] else "",
        "联系方式": "",
        "案情": req.case_name.strip(),
        "发生时间": "",
        "发生地点": "",
        "案发经过": "",
        "嫌疑人特征": "",
        "作案工具及涉案物品": "",
        "其他线索": "",
        "相关人员信息": ""
    }


def build_initial_context(req: RecordStartRequest) -> str:
    context_lines = [
        f"案件类型：{req.case_type.strip() or '未填写'}",
        f"案件名称：{req.case_name.strip() or '未填写'}",
        f"被询问人身份：{req.person_type.strip() or '未填写'}",
        f"被询问人姓名：{req.person_name.strip() or '未填写'}",
        f"证件类型：{req.id_type.strip() or '未填写'}",
        f"证件号码：{req.id_number.strip() or '未填写'}"
    ]
    return "案件基础信息：\n" + "\n".join(context_lines)



def handle_opening_flow(current_status: str, user_text: str) -> Tuple[str, str, bool]:
    # ==========================================
    # 状态 1：告知如实作证义务
    # ==========================================
    if current_status == STATUS_WITNESS_OPENING_1:
        # 1. 乖乖配合，流程推进
        if is_clear_yes(user_text, ["明白", "听明白", "清楚", "知道了", "理解了", "嗯", "对", "行"], ["不"]):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_2], STATUS_WITNESS_OPENING_2, True
        # 2. 明确拒绝/抗拒（非法回答）-> 严厉警告，状态原地锁定！
        elif is_clear_no(user_text, ["不明白", "没明白", "不清楚", "不理解", "不知道", "不想", "不愿"], []):
            return "【严厉提醒】作证是每个公民的法定义务。如果有意作伪证或者隐匿罪证，将面临三年以下有期徒刑等法律处罚。请明确回答，你现在听明白了吗？", current_status, True
        # 3. 顾左右而言他（非法回答）-> 纠正话术，状态原地锁定！
        else:
            return "请你针对我的问题明确回答“明白”或“不明白”。根据法律规定，你应当如实提供证据、证言。你明白了吗？", current_status, True

    # ==========================================
    # 状态 2：告知书阅读确认
    # ==========================================
    elif current_status == STATUS_WITNESS_OPENING_2:
        if is_clear_yes(user_text, ["可以", "能", "看过了", "已阅读", "读完了", "认字", "明白", "清楚", "嗯", "对"], ["不"]):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_3], STATUS_WITNESS_OPENING_3, True
        # 如果不识字，直接代为宣读，并且状态继续留在当前，等待确认听懂
        elif is_clear_no(user_text, ["不识字", "看不懂", "不会读", "不认识", "你读", "读给我听"], []):
            return "好的，那我现在向你宣读《证人诉讼权利义务告知书》的详细内容……（宣读完毕）。现在你清楚自己的权利和义务了吗？", current_status, True
        else:
            return "请明确回答。如果你能自己阅读，请仔细阅读；如果不识字或看不懂，请直接告诉我，我可以读给你听。", current_status, True

    # ==========================================
    # 状态 3：确认健康状况
    # ==========================================
    elif current_status == STATUS_WITNESS_OPENING_3:
        # 注意：这里的肯定代表“没病”，推进流程
        if contains_any(user_text, ["没有", "无", "没病", "挺好", "健康", "正常", "没"]):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_4], STATUS_WITNESS_OPENING_4, True
        # 这里的否定代表“有病”，给出医疗选项，并将状态推进到下一个去确认“能否接受询问”
        elif contains_any(user_text, ["有", "头晕", "发烧", "心脏病", "不舒服", "病", "疼", "难受"]):
            return "如果你目前身体极度不适，我们可以为你呼叫120医疗援助并暂停询问。请问你目前的身体状况，还能否坚持完成本次询问？", STATUS_WITNESS_OPENING_4, True
        else:
            return "请明确说明你是否有严重疾病或其他不适宜作证的情况？（如确无异常，请回答“没有”）", current_status, True

    # ==========================================
    # 状态 4：确认可接受询问
    # ==========================================
    elif current_status == STATUS_WITNESS_OPENING_4:
        if is_clear_yes(user_text, ["能够", "可以", "能", "清醒", "没问题", "坚持", "嗯", "对"], ["不"]):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_5], STATUS_WITNESS_OPENING_5, True
        # 借故推脱/真醉酒 -> 严肃处理
        elif contains_any(user_text, ["不能", "不可以", "不清醒", "喝醉", "头晕", "不行"]):
            return "【严正告知】如果你现在故意借故推脱，属于不配合公安机关工作。如果你确实处于醉酒或精神恍惚状态，我们将依法约束至你清醒或带你进行医学鉴定。请最后确认，你现在能否接受正常询问？", current_status, True
        else:
            return "请明确回答“能”或“不能”。你现在头脑是否清醒，能够接受询问？", current_status, True

    # ==========================================
    # 状态 5：采集个人信息 (大模型交接点！)
    # ==========================================
    elif current_status == STATUS_WITNESS_OPENING_5:
        # 拦截极其不配合的抗拒态度（非法回答）
        if contains_any(user_text, ["不想说", "不愿", "保密", "不知道", "凭什么", "不告诉你", "隐私"]):
            return "【法制教育】配合调查并如实提供真实身份信息，是公民法定义务。拒绝提供或提供虚假信息将承担相应法律后果。请如实陈述你的姓名、出生日期、住址及联系方式等信息。", current_status, True
        
        # 🌟 魔法交接点：只要他不拒绝，我们就认为他开始报个人信息了。
        # 此时，我们返回 matched = False。
        # 控制权将彻底移交给你的 Qwen 大模型！大模型会读取他的信息，提取出 JSON 字段，并极其丝滑地将状态推进到“AI询问中”。
        else:
            return "", current_status, False

    # 兜底：不在开场状态的，统统交给大模型
    return "", current_status, False


@router.post("/start", summary="1. 开启新笔录 (播报开场固定内容)")
async def start_record(
    req: RecordStartRequest,
    token: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    parts = token.split("_")
    police_number = parts[2] if len(parts) >= 3 else "unknown_police"

    initial_info = build_initial_extracted_info(req)
    opening_text = OPENING_STEPS[STATUS_WITNESS_OPENING_1]
    initial_context = build_initial_context(req)
    record_title = req.case_name.strip() or "AI智能笔录"

    new_record = Record(
        police_number=police_number,
        title=record_title,
        content=f"{initial_context}\nAI警官：{opening_text}",
        status=STATUS_WITNESS_OPENING_1,
        extracted_info=json.dumps(initial_info, ensure_ascii=False)
    )

    session.add(new_record)
    session.commit()
    session.refresh(new_record)

    create_info = RecordCreateInfo(
        record_id=new_record.id,
        police_number=police_number,
        case_type=req.case_type.strip(),
        case_name=req.case_name.strip(),
        person_type=req.person_type.strip(),
        person_name=req.person_name.strip(),
        id_type=req.id_type.strip(),
        id_number=req.id_number.strip()
    )

    session.add(create_info)
    session.commit()

    return {
        "code": 200,
        "message": "笔录初始化成功",
        "data": {
            "record_id": new_record.id,
            "ai_reply": opening_text,
            "status": new_record.status
        }
    }


@router.post("/chat", response_model=ChatResponse, summary="2. 核心对话流 (大模型接管)")
async def chat_with_ai(
    req: ChatRequest,
    token: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    db_record = session.get(Record, req.record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="找不到该笔录ID")

    user_text = req.reporter_text
    current_status = db_record.status
    extracted_info = db_record.extracted_info

    db_record.content += f"\n证人：{user_text}"

    current_extracted_info = parse_extracted_info(extracted_info)
    ai_reply = ""
    new_status = current_status
    new_extracted_info = current_extracted_info

    rule_reply, rule_status, matched = handle_opening_flow(current_status, user_text)
    if matched:
        ai_reply = rule_reply
        new_status = rule_status
    else:
        system_prompt = get_interrogation_prompt(current_status, current_extracted_info)

        try:
            # 🚀 修正了重复的行，并且确保了参数名绝对是 messages
            response = await client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"以下是完整的聊天记录，请分析并给出下一步回应：\n{db_record.content}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}, 
                max_tokens=800 
            )

            ai_response_text = response.choices[0].message.content
            print(f"🕵️‍♂️ 大模型原始回复内容是：\n{ai_response_text}\n") # 加上这句方便以后排错

            # 🚀 核心扒衣魔法：寻找第一个 '{' 和最后一个 '}' 之间的所有内容
            start_idx = ai_response_text.find('{')
            end_idx = ai_response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_json_str = ai_response_text[start_idx:end_idx+1]
                result_data = json.loads(clean_json_str)
            else:
                # 如果大模型彻底胡言乱语没返回 JSON，给个默认兜底
                print("❌ 警告：大模型没有返回有效的 JSON 结构！")
                result_data = {
                    "ai_reply": ai_response_text, # 把它说的话直接原样输出
                    "new_status": current_status,
                    "extracted_info": current_extracted_info
                }

            # 🚀 柔性容错：不管它是叫 ai_reply 还是 reply，甚至是 text，我们统统接住！
            ai_reply = result_data.get("ai_reply") or result_data.get("reply") or result_data.get("text", "（大模型正在思考案件，请稍候）")
            
            new_status = result_data.get("new_status") or result_data.get("status", current_status)
            
            # 如果大模型忘了返回 extracted_info，我们就用上一次的旧数据，防止清空
            new_extracted_info = result_data.get("extracted_info") or current_extracted_info

        except Exception as e:
            print(f"大模型调用失败: {e}")
            raise HTTPException(status_code=500, detail="AI 大脑暂时开小差了，请稍后再试。")

    db_record.content += f"\nAI警官：{ai_reply}"
    db_record.status = new_status
    db_record.extracted_info = json.dumps(new_extracted_info, ensure_ascii=False)

    session.add(db_record)
    session.commit()

    return ChatResponse(
        ai_reply=ai_reply,
        status=db_record.status,
        extracted_info=new_extracted_info
    )
