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
        <button class="soft-btn" @click="pause">暂停</button>
        <button class="soft-btn" @click="resume">继续</button>
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
            <article v-for="(item, index) in chatList" :key="index" class="chat-item">
              <div class="chat-role">{{ item.role === 'ai' ? 'AI' : '问' }}</div>
              <div class="chat-content">{{ item.content }}</div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { startRecord, chatWithAI, speechToText } from "@/api/record"

const route = useRoute()

let formData: Record<string, string> = {}
if (route.query.form) {
  formData = JSON.parse(route.query.form as string)
}

const recordText = ref(`
询问时间：2026-04-19

一、到场情况
被询问人已到场，身份信息已核验，正在进行基础情况确认。

二、询问内容
请按时间顺序补充案发经过、接触人员、关键物证和后续行动描述。

三、补充说明
此区域可继续接入语音转写或 AI 自动整理后的笔录内容。
`.trim())

// 对话列表，修改为更适合AI对话的结构
const chatList = ref<Array<{ role: 'ai' | 'user', content: string }>>([])

const analysis = ref("系统将根据对话内容自动生成案件要素摘要，并辅助提示待补全的信息字段。")

// 录音相关状态
const isRecording = ref(false)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])
const reporterInput = ref("")
const recordId = ref<number | null>(null)
const isProcessing = ref(false)

// 初始化笔录
const initRecord = async () => {
  try {
    const response = await startRecord({
      caseType: formData.caseType || "盗窃案",
      caseName: formData.caseName || "",
      personType: formData.personType || "",
      personName: formData.personName || "",
      idType: formData.idType || "",
      idNumber: formData.idNumber || ""
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

// 语音转文字
const transcribeAudio = async (audioFile: File) => {
  try {
    isProcessing.value = true
    const response: any = await speechToText(audioFile)
    reporterInput.value = response.text
  } catch (error) {
    console.error("语音识别失败:", error)
  } finally {
    isProcessing.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  if (!reporterInput.value.trim() || recordId.value === null) return

  // 添加用户消息到聊天列表
  chatList.value.push({
    role: 'user',
    content: reporterInput.value
  })
  recordText.value += `\n嫌疑人：${reporterInput.value}`

  try {
    isProcessing.value = true
    const response: any = await chatWithAI({
      record_id: recordId.value,
      reporter_text: reporterInput.value
    })

    // 添加AI回复到聊天列表
    chatList.value.push({
      role: 'ai',
      content: response.ai_reply
    })
    recordText.value += `\nAI警官：${response.ai_reply}`

    // 更新分析信息
    if (response.extracted_info) {
      const info = response.extracted_info
      analysis.value = `案情：${info.案情 || '未提供'}\n发生时间：${info['发生时间'] || '未提供'}\n发生地点：${info['发生地点'] || '未提供'}\n相关人员信息：${info['相关人员信息'] || '未提供'}`
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
const finish = () => console.log("结束并归档")
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
.section-head p {
  margin: 6px 0 0;
  color: var(--text-soft);
}

.top-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.record-layout {
  margin-top: 24px;
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(320px, 0.95fr);
  gap: 24px;
}

.record-editor,
.record-side,
.analysis-panel {
  min-width: 0;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}

.section-head.compact {
  margin-bottom: 14px;
}

.state-pill {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #166534;
  background: rgba(34, 197, 94, 0.14);
}

textarea {
  width: 100%;
  min-height: 480px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.7);
  padding: 18px;
  font: inherit;
  line-height: 1.7;
  resize: vertical;
}

.record-side {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chat-panel,
.info-panel,
.analysis-panel,
.record-editor {
  padding: 20px;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.chat-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.chat-role {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.12);
  color: var(--accent);
  display: grid;
  place-items: center;
  font-weight: 600;
}

.chat-content {
  flex: 1;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.82);
  line-height: 1.6;
}

.recording-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recording-input {
  display: flex;
  gap: 12px;
}

.recording-input textarea {
  min-height: 100px;
  flex: 1;
}

.record-btn {
  min-width: 100px;
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line-soft);
  background: white;
  cursor: pointer;
}

.record-btn.recording {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.info-list {
  display: grid;
  gap: 16px;
}

.info-list div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px dashed var(--line-soft);
  padding-bottom: 10px;
}

.info-list dt {
  color: var(--text-faint);
}

.info-list dd {
  margin: 0;
  color: var(--text-strong);
  text-align: right;
}

.analysis-panel {
  margin-top: 24px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.analysis-card {
  padding: 18px;
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.analysis-card strong {
  display: block;
  margin-bottom: 10px;
}

.analysis-card p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.65;
  white-space: pre-line;
}

.analysis-card.accent {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.14), rgba(99, 102, 241, 0.12));
}

.soft-btn,
.primary-btn {
  border: none;
  border-radius: var(--radius-lg);
  padding: 10px 16px;
  font: inherit;
  cursor: pointer;
}

.soft-btn {
  background: rgba(148, 163, 184, 0.14);
  color: var(--text-strong);
}

.primary-btn {
  background: linear-gradient(135deg, var(--accent), #4f46e5);
  color: white;
  box-shadow: 0 18px 32px rgba(79, 70, 229, 0.22);
}

@media (max-width: 1100px) {
  .record-layout,
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .record-page {
    padding: 18px;
  }

  .record-top {
    flex-direction: column;
  }

  .top-actions {
    width: 100%;
    justify-content: stretch;
    flex-wrap: wrap;
  }

  .top-actions button,
  .record-btn,
  .input-actions button {
    width: 100%;
  }

  .recording-input {
    flex-direction: column;
  }
}
</style>
