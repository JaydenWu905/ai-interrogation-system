<template>
  <div class="record-page">
    <header class="record-top">
      <div>
        <span class="kicker">笔录进行中</span>
        <h1>{{ formData.caseName || "未命名案件" }}</h1>
        <p>
          被询问人：{{ formData.personName || "待填写" }} · 身份：{{ formData.personType || "未设置" }} ·
          证件：{{ formData.idType || "未设置" }}
        </p>
      </div>

      <div class="top-actions">
        <button class="soft-btn" @click="goHome">回到主页面</button>
        <button class="soft-btn" @click="pause">暂停</button>
        <button class="soft-btn" @click="resume">继续</button>
        <button class="primary-btn" @click="showSaveModal = true">保存笔录</button>
        <button class="primary-btn" @click="print">打印笔录</button>
      </div>
    </header>

    <main class="record-layout">
      <section class="record-editor panel">
        <div class="section-head">
          <div>
            <span class="section-kicker">主记录区</span>
            <h2>询问笔录</h2>
          </div>
          <span class="state-pill">自动保存中</span>
        </div>

        <textarea v-model="recordText" />
      </section>

      <aside class="record-side">
        <section class="panel chat-panel">
          <div class="section-head compact">
            <div>
              <span class="section-kicker">对话摘录</span>
              <h2>现场记录</h2>
            </div>
          </div>

          <div class="chat-list">
            <article v-for="(item, index) in formattedChatList" :key="index" class="chat-item">
              <div class="chat-pair">
                <div class="chat-row ai-row">
                  <span class="chat-label">问：</span>
                  <span class="chat-text">{{ item.question }}</span>
                </div>
                <div class="chat-row user-row" v-if="item.answer">
                  <span class="chat-label">答：</span>
                  <span class="chat-text">{{ item.answer }}</span>
                </div>
              </div>
            </article>
          </div>

          <div class="recording-section">
            <div class="recording-input">
              <textarea v-model="reporterInput" placeholder="请输入或点击录音按钮进行语音输入..." :disabled="isProcessing"></textarea>
              <button 
                class="record-btn" 
                :class="{ 'recording': isRecording }" 
                @click="toggleRecording"
                :disabled="isProcessing"
              >
                {{ isRecording ? '停止录音' : '开始录音' }}
              </button>
            </div>
            <div class="input-actions">
              <button class="soft-btn" @click="sendMessage" :disabled="isProcessing || !reporterInput.trim()">
                {{ isProcessing ? '处理中...' : '发送' }}
              </button>
            </div>
          </div>
        </section>

        <section class="panel info-panel">
          <div class="section-head compact">
            <div>
              <span class="section-kicker">人员信息</span>
              <h2>当前对象</h2>
            </div>
          </div>

          <dl class="info-list">
            <div>
              <dt>案件类型</dt>
              <dd>{{ formData.caseType || "未填写" }}</dd>
            </div>
            <div>
              <dt>案件名称</dt>
              <dd>{{ formData.caseName || "未填写" }}</dd>
            </div>
            <div>
              <dt>被询问人</dt>
              <dd>{{ formData.personName || "未填写" }}</dd>
            </div>
            <div>
              <dt>证件号码</dt>
              <dd>{{ formData.idNumber || "未填写" }}</dd>
            </div>
          </dl>
        </section>
      </aside>
    </main>

    <section class="analysis-panel panel">
      <div class="section-head compact">
        <div>
          <span class="section-kicker">AI 分析</span>
          <h2>要素摘要</h2>
        </div>
        <button class="soft-btn" @click="finish">结束并归档</button>
      </div>

      <div class="analysis-grid">
        <article class="analysis-card">
          <strong>案件概况</strong>
          <p>{{ analysis }}</p>
        </article>
        <article class="analysis-card">
          <strong>缺失信息提醒</strong>
          <p>建议补充到场时间、联系方式与案发地点描述，后续更方便归档和打印。</p>
        </article>
        <article class="analysis-card accent">
          <strong>下一步动作</strong>
          <p>可继续编辑笔录正文，确认无误后打印并进入案件管理环节。</p>
        </article>
      </div>
    </section>

    <div v-if="showSaveModal" class="modal-overlay" @click.self="showSaveModal = false">
      <div class="save-modal">
        <div class="modal-header">
          <h3>确认保存笔录</h3>
          <button class="close-btn" @click="showSaveModal = false">×</button>
        </div>
        <div class="modal-body">
          <p>您确定要保存当前笔录吗？</p>
          <div class="record-preview">
            <strong>笔录内容预览：</strong>
            <textarea readonly>{{ recordText }}</textarea>
          </div>
          <p class="modal-tip">保存后可在案件管理中查看和编辑。</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showSaveModal = false">取消</button>
          <button class="confirm-btn" @click="confirmSave">确认保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from "vue"
import { useRoute, useRouter } from "vue-router"
import { startRecord, chatWithAI, speechToText, createRecord, saveRecord } from "@/api/record"

const route = useRoute()
const router = useRouter()

const formData = reactive<Record<string, string>>({})

const showSaveModal = ref(false)
if (route.query.form) {
  Object.assign(formData, JSON.parse(route.query.form as string))
}

const recordText = ref("")

// 对话列表，存储AI和用户的交替消息
const chatList = ref<Array<{ role: 'ai' | 'user', content: string }>>([])

// 格式化聊天列表为一问一答的格式
const formattedChatList = computed(() => {
  const pairs: Array<{ question: string; answer: string | null }> = []
  let currentQuestion: string | null = null
  
  chatList.value.forEach((item) => {
    if (item.role === 'ai') {
      if (currentQuestion) {
        pairs.push({ question: currentQuestion, answer: null })
      }
      currentQuestion = item.content
    } else {
      if (currentQuestion) {
        pairs.push({ question: currentQuestion, answer: item.content })
        currentQuestion = null
      }
    }
  })
  
  if (currentQuestion) {
    pairs.push({ question: currentQuestion, answer: null })
  }
  
  return pairs
})

const analysis = ref("系统将根据对话内容自动生成案件要素摘要，并辅助提示待补全的信息字段。")

// 录音相关状态
const isRecording = ref(false)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])
const reporterInput = ref("")
const recordId = ref("")
const isProcessing = ref(false)

// 初始化笔录
const initRecord = async () => {
  try {
    const response = await startRecord({
      reporter_name: formData.personName || "未知",
      case_type: formData.caseType || "盗窃案",
      case_name: formData.caseName || "未立案",
      person_type: formData.personType || "证人",
      id_type: formData.idType || "身份证",
      id_number: formData.idNumber || ""
    })
    recordId.value = response.data.record_id
    chatList.value.push({
      role: 'ai',
      content: response.data.ai_reply
    })
    recordText.value += `\nAI警官：${response.data.ai_reply}`
  } catch (error) {
    console.error("初始化笔录失败:", error)
  }
}

// 切换录音状态
const toggleRecording = async () => {
  if (isRecording.value) {
    // 停止录音
    if (mediaRecorder.value) {
      mediaRecorder.value.stop()
      isRecording.value = false
    }
  } else {
    // 开始录音
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder.value = new MediaRecorder(stream)
      audioChunks.value = []

      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }

      mediaRecorder.value.onstop = async () => {
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
        const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' })
        await transcribeAudio(audioFile)
        
        // 停止媒体流
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.value.start()
      isRecording.value = true
    } catch (error) {
      console.error("录音失败:", error)
    }
  }
}

// 回到主页面
const goHome = () => {
  router.push("/")
}

// 确认保存笔录
const confirmSave = async () => {
  try {
    const response = await saveRecord({
      record_id: recordId.value,
      title: formData.caseName || "AI智能笔录",
      content: recordText.value,
      reporter_name: formData.personName || "未知",
      case_type: formData.caseType || "盗窃案"
    })
    if (response.code === 200) {
      alert("笔录保存成功！")
      showSaveModal.value = false
      router.push("/")
    } else {
      alert("保存失败：" + response.message)
    }
  } catch (error) {
    console.error("保存笔录失败:", error)
    alert("保存失败，请重试")
  }
}

// 语音转文字
const transcribeAudio = async (audioFile: File) => {
  try {
    isProcessing.value = true
    const response = await speechToText(audioFile)
    reporterInput.value = response.data.text
  } catch (error) {
    console.error("语音识别失败:", error)
  } finally {
    isProcessing.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  if (!reporterInput.value.trim() || !recordId.value) return

  // 添加用户消息到聊天列表
  chatList.value.push({
    role: 'user',
    content: reporterInput.value
  })
  recordText.value += `\n嫌疑人：${reporterInput.value}`

  try {
    isProcessing.value = true
    const response = await chatWithAI({
      record_id: recordId.value,
      reporter_text: reporterInput.value
    })

    // 添加AI回复到聊天列表
    chatList.value.push({
      role: 'ai',
      content: response.data.ai_reply
    })
    recordText.value += `\nAI警官：${response.data.ai_reply}`

    // 更新分析信息
    if (response.data.extracted_info) {
      const info = response.data.extracted_info
      analysis.value = `案情：${info.案情 || '未提供'}\n发生时间：${info['发生时间'] || '未提供'}\n发生地点：${info['发生地点'] || '未提供'}\n嫌疑人信息：${info['嫌疑人信息'] || '未提供'}`
    }

    // 清空输入
    reporterInput.value = ""
  } catch (error) {
    console.error("发送消息失败:", error)
  } finally {
    isProcessing.value = false
  }
}

// 生命周期钩子，组件挂载时初始化笔录
onMounted(() => {
  initRecord()
})

const pause = () => console.log("暂停")
const resume = () => console.log("继续")
const print = () => console.log("打印")
const finish = () => console.log("结束")
</script>

<style scoped>
.record-page {
  min-height: 100vh;
  padding: 24px;
}

.panel,
.record-top {
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-xl);
  background: var(--bg-panel);
  backdrop-filter: blur(24px);
  box-shadow: var(--shadow-md);
}

.record-top {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 28px;
}

.kicker,
.section-kicker {
  display: inline-block;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-faint);
}

.record-top h1,
.section-head h2 {
  margin: 8px 0 0;
}

.record-top p,
.analysis-card p {
  color: var(--text-soft);
}

.top-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.soft-btn,
.primary-btn {
  height: 46px;
  padding: 0 18px;
  border-radius: 14px;
}

.soft-btn {
  background: rgba(29, 111, 216, 0.08);
  color: var(--brand);
}

.primary-btn {
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  color: #fff;
}

.record-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) 360px;
  gap: 20px;
  margin-top: 20px;
}

.record-editor,
.chat-panel,
.info-panel,
.analysis-panel {
  padding: 24px;
}

.chat-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 400px;
}

.chat-panel .section-head {
  flex-shrink: 0;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  max-height: 400px;
  padding-right: 8px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 18px;
}

.section-head.compact {
  margin-bottom: 16px;
}

.state-pill {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(17, 166, 161, 0.12);
  color: var(--accent);
  font-size: 12px;
}

.record-editor textarea {
  width: 100%;
  min-height: 560px;
  padding: 22px;
  border-radius: 20px;
  border: 1px solid rgba(114, 136, 177, 0.16);
  background: rgba(255, 255, 255, 0.96);
  color: var(--text-main);
  line-height: 1.8;
}

.record-editor textarea:focus {
  outline: none;
  border-color: rgba(29, 111, 216, 0.5);
  box-shadow: 0 0 0 4px rgba(29, 111, 216, 0.12);
}

.record-side {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-item {
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(114, 136, 177, 0.14);
}

.chat-pair {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-row {
  display: flex;
  gap: 8px;
  line-height: 1.6;
}

.chat-label {
  font-weight: 600;
  flex-shrink: 0;
}

.ai-row .chat-label {
  color: var(--brand);
}

.user-row .chat-label {
  color: var(--accent);
}

.chat-text {
  color: var(--text-main);
  flex: 1;
  word-break: break-word;
}

.recording-section {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid rgba(114, 136, 177, 0.14);
  flex-shrink: 0;
}

.recording-input {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.recording-input textarea {
  flex: 1;
  min-height: 100px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(114, 136, 177, 0.16);
  background: rgba(255, 255, 255, 0.96);
  color: var(--text-main);
  resize: vertical;
}

.recording-input textarea:focus {
  outline: none;
  border-color: rgba(29, 111, 216, 0.5);
  box-shadow: 0 0 0 4px rgba(29, 111, 216, 0.12);
}

.record-btn {
  width: 120px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(29, 111, 216, 0.08);
  color: var(--brand);
  border: 1px solid rgba(29, 111, 216, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.record-btn:hover {
  background: rgba(29, 111, 216, 0.12);
}

.record-btn.recording {
  background: rgba(220, 53, 69, 0.12);
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.3);
  animation: pulse 1.5s infinite;
}

.record-btn:disabled,
.soft-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.recording-input textarea:disabled {
  background: rgba(255, 255, 255, 0.7);
  cursor: not-allowed;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(220, 53, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
  }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(12, 20, 36, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.save-modal {
  width: min(600px, 100%);
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(114, 136, 177, 0.12);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.modal-header .close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(114, 136, 177, 0.1);
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-soft);
}

.modal-body {
  padding: 24px;
}

.modal-body p {
  margin: 0 0 16px;
  color: var(--text-soft);
}

.record-preview {
  margin-bottom: 16px;
}

.record-preview strong {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-soft);
}

.record-preview textarea {
  width: 100%;
  min-height: 150px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(114, 136, 177, 0.16);
  background: rgba(248, 249, 251, 0.9);
  color: var(--text-main);
  resize: vertical;
  font-family: inherit;
}

.modal-tip {
  font-size: 14px;
  color: var(--text-soft) !important;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(114, 136, 177, 0.12);
  background: rgba(248, 249, 251, 0.5);
}

.cancel-btn {
  padding: 12px 24px;
  border-radius: 12px;
  background: rgba(114, 136, 177, 0.12);
  color: var(--text-soft);
  border: none;
  cursor: pointer;
}

.confirm-btn {
  padding: 12px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  color: #fff;
  border: none;
  cursor: pointer;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.info-list {
  display: grid;
  gap: 14px;
  margin: 0;
}

.info-list div {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(114, 136, 177, 0.14);
}

.info-list dt {
  color: var(--text-faint);
  font-size: 13px;
}

.info-list dd {
  margin: 8px 0 0;
  color: var(--text-main);
  font-weight: 600;
}

.analysis-panel {
  margin-top: 20px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.analysis-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(114, 136, 177, 0.14);
}

.analysis-card strong {
  display: block;
  margin-bottom: 10px;
}

.analysis-card.accent {
  background: linear-gradient(145deg, rgba(29, 111, 216, 0.1), rgba(17, 166, 161, 0.12));
}

@media (max-width: 1100px) {
  .record-layout,
  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .record-top {
    flex-direction: column;
  }
}

@media (max-width: 720px) {
  .record-page {
    padding: 16px;
  }

  .top-actions {
    flex-wrap: wrap;
  }
}

</style>