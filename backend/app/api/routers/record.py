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

router = APIRouter(prefix="/records", tags=["AI笔录核心业务"])


STATUS_WITNESS_OPENING_1 = "证人_告知如实作证义务"
STATUS_WITNESS_OPENING_2 = "证人_告知书阅读确认"
STATUS_WITNESS_OPENING_3 = "证人_确认健康状况"
STATUS_WITNESS_OPENING_4 = "证人_确认可接受询问"
STATUS_WITNESS_OPENING_5 = "证人_采集个人信息"
STATUS_AI_ASKING = "AI询问中"
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
    if current_status == STATUS_WITNESS_OPENING_1:
        if is_clear_yes(
            user_text,
            ["明白", "听明白", "清楚", "知道了", "理解了"],
            ["不明白", "没明白", "没听明白", "不太明白", "不清楚", "不理解"]
        ):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_2], STATUS_WITNESS_OPENING_2, True

    elif current_status == STATUS_WITNESS_OPENING_2:
        if is_clear_yes(
            user_text,
            ["可以阅读", "我可以阅读", "看过了", "已阅读", "看完了", "看过", "读完了"],
            ["不识字", "看不懂", "不会读", "你读给我听", "请你读给我听"]
        ):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_3], STATUS_WITNESS_OPENING_3, True

    elif current_status == STATUS_WITNESS_OPENING_3:
        if is_clear_no(
            user_text,
            ["没有", "无", "没有这种情况", "没有严重疾病"],
            ["但是", "不过", "头晕", "发烧", "不舒服", "有病", "有点"]
        ):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_4], STATUS_WITNESS_OPENING_4, True

    elif current_status == STATUS_WITNESS_OPENING_4:
        if is_clear_yes(
            user_text,
            ["能够", "可以", "能", "接受询问", "可以接受询问"],
            ["不能", "不可以", "不太能", "现在不行", "不接受", "头脑不清醒"]
        ):
            return OPENING_STEPS[STATUS_WITNESS_OPENING_5], STATUS_WITNESS_OPENING_5, True

    elif current_status == STATUS_WITNESS_OPENING_5:
        if contains_any(user_text, ["我叫", "姓名", "男", "女", "身份证", "联系方式", "住址"]):
            return "好的，我先记录你的个人情况。如有遗漏，我会继续向你核实补充。", STATUS_AI_ASKING, True

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
        system_prompt = f"""
        你是一名经验丰富、程序意识严谨的中国公安民警，正在依法询问证人。当前询问阶段为：【{current_status}】。
        你目前已经掌握并需要持续更新的信息是：{json.dumps(current_extracted_info, ensure_ascii=False)}

        当前阶段可能包括：
        1. 证人_告知如实作证义务
        2. 证人_告知书阅读确认
        3. 证人_确认健康状况
        4. 证人_确认可接受询问
        5. 证人_采集个人信息
        6. AI询问中
        7. 笔录结束

        你的任务是仔细阅读我接下来发给你的完整聊天记录，然后：
        1. 根据证人最新的话，给出你作为民警的下一句合理回应或追问。
        2. 如果证人的回答不是常规的肯定/否定回答，你要结合当前阶段和完整上下文，给出自然、严谨、符合法律程序的回应，并判断是保持当前阶段、补充解释，还是推进到下一阶段。
        3. 当处于“证人_采集个人信息”或“AI询问中”时，你要继续提取和更新这些字段：姓名、性别、民族、出生日期、住址、身份证号、联系方式、案情、发生时间、发生地点、相关人员信息。如果证人没有提到某项，就保持原值。
        4. 如果证人明确表示没有更多内容，且关键信息已经基本完整，你可以将状态改为“笔录结束”，并输出固定结语：“{FIXED_CLOSING}”。

        【极度重要】：你必须且只能回复一个合法的 JSON 数据包！不要包裹在 markdown 代码块里，直接输出 JSON！
        必须严格包含以下三个字段：
        {{
            "ai_reply": "你对证人说的话",
            "new_status": "案件的新状态",
            "extracted_info": {{
                "姓名": "...",
                "性别": "...",
                "民族": "...",
                "出生日期": "...",
                "住址": "...",
                "身份证号": "...",
                "联系方式": "...",
                "案情": "...",
                "发生时间": "...",
                "发生地点": "...",
                "相关人员信息": "..."
            }}
        }}
        """

        try:
            response = await client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"以下是完整的聊天记录，请分析并给出下一步回应：\n{db_record.content}"}
                ],
                temperature=0.3
            )

            ai_response_text = response.choices[0].message.content
            result_data = json.loads(ai_response_text)

            ai_reply = result_data.get("ai_reply", "抱歉，系统处理出现异常。")
            new_status = result_data.get("new_status", current_status)
            new_extracted_info = result_data.get("extracted_info", current_extracted_info)

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
