from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import os

# 1. 引入 FunASR
from funasr import AutoModel

router = APIRouter(prefix="/audio", tags=["多媒体与语音识别"])

print("🚀 正在将 FunASR 模型装载入内存，请稍候...")
# 2. 【核心点】全局加载模型！
# 这样模型只会在终端敲 `python main.py` 的时候加载一次，常驻内存
asr_model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
    # disable_update=True # 如果你不想它每次启动都去检查更新，可以解除这行注释
)
print("✅ FunASR 模型装载完毕！")

# 3. 定义返回的契约
class ASRResponse(BaseModel):
    code: int = 200
    message: str = "识别成功"
    text: str

@router.post("/speech-to-text", response_model=ASRResponse, summary="上传语音并转为文字")
async def convert_speech_to_text(file: UploadFile = File(..., description="请上传 .wav 录音文件")):
    """
    接收前端上传的语音文件，调用本地 FunASR 大模型提取纯文本。
    """
    # 1. 检查是不是空文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="未找到上传的文件")

    # 2. 找个临时的地方把前端传来的录音存下来
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. 呼叫大模型开始干活！(传入刚刚存好的临时文件路径)
        res = asr_model.generate(input=temp_file_path)
        
        # 4. 提取文字结果
        text_result = ""
        if res and len(res) > 0:
            text_result = res[0].get("text", "")
            
        return ASRResponse(text=text_result)

    except Exception as e:
        # 如果模型抽风了，报错返回
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")
        
    finally:
        # 5. 【极其重要】过河拆桥！用完立刻删掉临时录音文件，防止把服务器硬盘塞满
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)