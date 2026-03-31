from funasr import AutoModel

print("正在加载 AI 语音大模型，请稍候 (首次运行会自动下载)...")

# 1. 组装“满配版”语音识别引擎
# 为什么是满配？因为做笔录必须要有断句！
model = AutoModel(
    model="paraformer-zh",  # 核心：语音转文字模型 (主攻中文)
    vad_model="fsmn-vad",   # 辅助：语音端点检测 (自动切除前后的空白静音，提升速度)
    punc_model="ct-punc",   # 辅助：标点符号预测 (给转出来的文字自动加上逗号、句号)
)

# 2. 指定你的录音文件路径
# 你可以用手机随便录一段话，保存为 test_audio.wav 放到这个代码同级目录下
audio_file = "record_out.wav" 

print(f"开始识别文件: {audio_file} ...")

# 3. 核心调用：执行识别
# 返回的是一个列表，里面包含了识别结果的字典
res = model.generate(input=audio_file)

# 4. 提取并打印纯文本结果
if res and len(res) > 0:
    text_result = res[0].get("text", "")
    print("\n✅ 识别成功！笔录文字如下：")
    print("-" * 30)
    print(text_result)
    print("-" * 30)
else:
    print("❌ 识别失败，未提取到文字。")