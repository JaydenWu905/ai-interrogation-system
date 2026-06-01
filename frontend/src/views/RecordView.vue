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
        <label class="voice-control">
          <span>音色</span>
          <select v-model="selectedVoiceURI" :disabled="voiceOptions.length === 0" @change="saveSelectedVoice">
            <option value="">自动</option>
            <option v-for="voice in voiceOptions" :key="voice.voiceURI" :value="voice.voiceURI">
              {{ voice.name }} ({{ voice.lang }})
            </option>
          </select>
        </label>
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

        <div class="record-window-actions">
          <button class="soft-btn" @click="goHome">回到主页面</button>
          <button class="soft-btn" @click="pause">暂停</button>
          <button class="soft-btn" @click="resume">继续</button>
          <button class="primary-btn" @click="showSaveModal = true">保存笔录</button>
          <button class="primary-btn" @click="print">打印笔录</button>
          <button class="primary-btn" @click="handleExportWord">导出Word</button>
        </div>
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

    <div v-if="showTranscriptModal" class="modal-overlay" @click.self="showTranscriptModal = false">
      <div class="transcript-modal">
        <div class="modal-header">
          <h3>询问笔录预览</h3>
          <div class="modal-header-actions">
            <button class="primary-btn" @click="handleExportWord">导出Word</button>
            <button class="close-btn" @click="showTranscriptModal = false">×</button>
          </div>
        </div>

        <div class="modal-body transcript-body" v-if="transcriptData">
          <div class="transcript-title">询 问 笔 录</div>

          <section class="transcript-section">
            <div class="transcript-info-row"><span>时    间：</span><strong>{{ transcriptData.header.record_time }}</strong></div>
            <div class="transcript-info-row"><span>地    点：</span><strong>{{ transcriptData.header.record_location }}</strong></div>
            <div class="transcript-info-row"><span>询 问 人：</span><strong>{{ transcriptData.header.interrogator }}</strong></div>
            <div class="transcript-info-row"><span>记 录 人：</span><strong>{{ transcriptData.header.recorder }}</strong></div>
            <div class="transcript-info-row"><span>案件名称：</span><strong>{{ transcriptData.header.case_name }}</strong></div>
          </section>

          <section class="transcript-section">
            <h4>被询问人基本信息</h4>
            <table class="transcript-table">
              <tbody>
                <tr>
                  <td>姓名</td>
                  <td>{{ transcriptData.person_info.姓名 }}</td>
                  <td>性别</td>
                  <td>{{ transcriptData.person_info.性别 }}</td>
                </tr>
                <tr>
                  <td>民族</td>
                  <td>{{ transcriptData.person_info.民族 }}</td>
                  <td>出生日期</td>
                  <td>{{ transcriptData.person_info.出生日期 }}</td>
                </tr>
                <tr>
                  <td>身份证号</td>
                  <td>{{ transcriptData.person_info.身份证号 }}</td>
                  <td>联系方式</td>
                  <td>{{ transcriptData.person_info.联系方式 }}</td>
                </tr>
                <tr>
                  <td>住址</td>
                  <td colspan="3">{{ transcriptData.person_info.住址 }}</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section class="transcript-section">
            <h4>案件要素摘要</h4>
            <div class="case-info-list">
              <div v-for="(value, key) in transcriptData.case_info" :key="key" class="case-info-item" v-show="value && value !== '未知'">
                <span>【{{ key }}】</span>
                <strong>{{ value }}</strong>
              </div>
            </div>
          </section>

          <section class="transcript-section">
            <h4>询问过程</h4>
            <div class="qa-record">
              <div v-for="(pair, index) in transcriptData.qa_pairs" :key="index" class="qa-pair">
                <p v-if="pair.question"><strong>问：</strong>{{ pair.question }}</p>
                <p v-if="pair.answer"><strong>答：</strong>{{ pair.answer }}</p>
              </div>
            </div>
          </section>

          <section class="transcript-section signature-section">
            <p>以上笔录我已看过（向我宣读过），和我说的相符。</p>
            <p>被询问人签名（捺手印）：________________</p>
            <p>询问人签名：________________</p>
            <p>记录人签名：________________</p>
          </section>
        </div>

        <div class="modal-body" v-else>
          <p>正在加载笔录数据...</p>
        </div>

        <div class="modal-footer">
          <button class="cancel-btn" @click="showTranscriptModal = false">关闭</button>
          <button class="confirm-btn" @click="handleExportWord">导出Word文档</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, reactive } from "vue"
import { useRoute, useRouter } from "vue-router"
import { startRecord, chatWithAI, chatWithAudio, speechToText, getTranscript, exportRecordWord } from "@/api/record"

const route = useRoute()
const router = useRouter()

const formData = reactive<Record<string, string>>({})

const showSaveModal = ref(false)
const showTranscriptModal = ref(false)
const transcriptData = ref<any>(null)
if (route.query.form) {
  Object.assign(formData, JSON.parse(route.query.form as string))
}

const recordText = ref("")
const respondentLabel = computed(() => formData.personType?.trim() || "被询问人")

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
const audioStream = ref<MediaStream | null>(null)
const audioContext = ref<AudioContext | null>(null)
const silenceTimer = ref<number | null>(null)
const audioChunks = ref<Blob[]>([])
const reporterInput = ref("")
const recordId = ref<number | null>(null)
const isProcessing = ref(false)
const isAiSpeaking = ref(false)
const isAutoMode = ref(true)
const isPaused = ref(false)
const shouldProcessRecording = ref(true)
const recordingMode = ref<'auto' | 'manual'>('manual')
const voiceOptions = ref<SpeechSynthesisVoice[]>([])
const selectedVoiceURI = ref(localStorage.getItem("ai_voice_uri") || "")

const silenceThreshold = 0.018
const silenceDurationMs = 1600
const minRecordingMs = 900
const maxRecordingMs = 30000

const preferredMaleVoiceKeywords = [
  "yunxi",
  "yunjian",
  "yunyang",
  "kangkang",
  "male",
  "男"
]

const isChineseVoice = (voice: SpeechSynthesisVoice) => voice.lang.toLowerCase().startsWith("zh")

const findPreferredMaleVoice = (voices: SpeechSynthesisVoice[]) => {
  return voices.find((voice) => {
    const voiceName = voice.name.toLowerCase()
    return isChineseVoice(voice) && preferredMaleVoiceKeywords.some((keyword) => voiceName.includes(keyword))
  })
}

const loadVoiceOptions = () => {
  if (!("speechSynthesis" in window)) return null

  const voices = window.speechSynthesis.getVoices()
  voiceOptions.value = voices

  if (selectedVoiceURI.value && !voices.some((voice) => voice.voiceURI === selectedVoiceURI.value)) {
    selectedVoiceURI.value = ""
    localStorage.removeItem("ai_voice_uri")
  }

  if (!selectedVoiceURI.value) {
    const preferredVoice = findPreferredMaleVoice(voices)
    if (preferredVoice) {
      selectedVoiceURI.value = preferredVoice.voiceURI
      localStorage.setItem("ai_voice_uri", preferredVoice.voiceURI)
    }
  }
}

const saveSelectedVoice = () => {
  if (selectedVoiceURI.value) {
    localStorage.setItem("ai_voice_uri", selectedVoiceURI.value)
  } else {
    localStorage.removeItem("ai_voice_uri")
  }
}

const getAiVoice = () => {
  if (!("speechSynthesis" in window)) return null

  const voices = voiceOptions.value.length > 0 ? voiceOptions.value : window.speechSynthesis.getVoices()
  const selectedVoice = voices.find((voice) => voice.voiceURI === selectedVoiceURI.value)
  if (selectedVoice) return selectedVoice

  return (
    findPreferredMaleVoice(voices) ||
    voices.find((voice) => voice.lang.toLowerCase() === "zh-cn") ||
    voices.find(isChineseVoice) ||
    null
  )
}

const shouldContinueAutoConversation = (status?: string) => {
  return isAutoMode.value && !isPaused.value && status !== "笔录结束" && status !== "人工干预"
}

const speakAiQuestion = (text?: string, nextStatus?: string) => {
  if (!text?.trim()) return
  if (!("speechSynthesis" in window)) {
    if (shouldContinueAutoConversation(nextStatus)) {
      setTimeout(() => startRecording('auto'), 300)
    }
    return
  }

  window.speechSynthesis.cancel()
  isAiSpeaking.value = true

  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = "zh-CN"
  utterance.rate = 1
  utterance.pitch = 1

  const voice = getAiVoice()
  if (voice) {
    utterance.voice = voice
  }

  utterance.onend = () => {
    isAiSpeaking.value = false
    if (shouldContinueAutoConversation(nextStatus)) {
      window.setTimeout(() => startRecording('auto'), 300)
    }
  }

  utterance.onerror = () => {
    isAiSpeaking.value = false
  }

  window.speechSynthesis.speak(utterance)
}

const stopAiSpeech = () => {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel()
  }
  isAiSpeaking.value = false
}

// 初始化笔录
const initRecord = async () => {
  try {
    const response: any = await startRecord({
      caseType: formData.caseType || "盗窃案",
      caseName: formData.caseName || "未立案",
      personType: formData.personType || "证人",
      personName: formData.personName || "未知",
      idType: formData.idType || "身份证",
      idNumber: formData.idNumber || ""
    })
    recordId.value = response.data.record_id
    chatList.value.push({
      role: 'ai',
      content: response.data.ai_reply
    })
    recordText.value += `\nAI警官：${response.data.ai_reply}`
    speakAiQuestion(response.data.ai_reply, response.data.status)
  } catch (error) {
    console.error("初始化笔录失败:", error)
  }
}

const cleanupRecordingResources = async () => {
  if (silenceTimer.value !== null) {
    window.clearInterval(silenceTimer.value)
    silenceTimer.value = null
  }

  audioStream.value?.getTracks().forEach(track => track.stop())
  audioStream.value = null

  if (audioContext.value) {
    await audioContext.value.close().catch(() => undefined)
    audioContext.value = null
  }
}

const getRecorderMimeType = () => {
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) return "audio/webm;codecs=opus"
  if (MediaRecorder.isTypeSupported("audio/webm")) return "audio/webm"
  return ""
}

const startSilenceDetection = (stream: MediaStream, startedAt: number) => {
  const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
  if (!AudioContextClass) {
    window.setTimeout(() => stopRecording(), maxRecordingMs)
    return
  }

  const context = new AudioContextClass()
  const analyser = context.createAnalyser()
  const source = context.createMediaStreamSource(stream)
  const data = new Uint8Array(analyser.fftSize)
  let lastVoiceAt = startedAt

  source.connect(analyser)
  audioContext.value = context

  silenceTimer.value = window.setInterval(() => {
    if (!isRecording.value) return

    analyser.getByteTimeDomainData(data)
    let sum = 0
    for (const value of data) {
      const normalized = (value - 128) / 128
      sum += normalized * normalized
    }

    const volume = Math.sqrt(sum / data.length)
    const now = Date.now()
    if (volume > silenceThreshold) {
      lastVoiceAt = now
    }

    const hasRecordedEnough = now - startedAt > minRecordingMs
    const isSilentLongEnough = now - lastVoiceAt > silenceDurationMs
    const isTooLong = now - startedAt > maxRecordingMs

    if (hasRecordedEnough && (isSilentLongEnough || isTooLong)) {
      stopRecording()
    }
  }, 180)
}

const startRecording = async (mode: 'auto' | 'manual' = 'manual') => {
  if (isRecording.value || isProcessing.value || isAiSpeaking.value || isPaused.value) return

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mimeType = getRecorderMimeType()
    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)

    recordingMode.value = mode
    mediaRecorder.value = recorder
    audioStream.value = stream
    audioChunks.value = []

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }

    recorder.onstop = async () => {
      const finalMimeType = recorder.mimeType || "audio/webm"
      const extension = finalMimeType.includes("webm") ? "webm" : "wav"
      const audioBlob = new Blob(audioChunks.value, { type: finalMimeType })
      const audioFile = new File([audioBlob], `recording.${extension}`, { type: finalMimeType })
      const shouldProcess = shouldProcessRecording.value

      await cleanupRecordingResources()
      shouldProcessRecording.value = true

      if (!shouldProcess || audioBlob.size === 0) return

      if (recordingMode.value === 'auto') {
        await sendAudioMessage(audioFile)
      } else {
        await transcribeAudio(audioFile)
      }
    }

    recorder.start()
    isRecording.value = true
    startSilenceDetection(stream, Date.now())
  } catch (error) {
    console.error("录音失败:", error)
    isRecording.value = false
    await cleanupRecordingResources()
  }
}

const stopRecording = (processAudio = true) => {
  shouldProcessRecording.value = processAudio
  if (mediaRecorder.value && mediaRecorder.value.state !== "inactive") {
    mediaRecorder.value.stop()
  }
  isRecording.value = false
}

// 切换录音状态
const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording('manual')
  }
}

// 回到主页面
const goHome = () => {
  router.push("/")
}

// 确认保存笔录
const confirmSave = async () => {
  try {
    if (!recordId.value) {
      alert("笔录尚未初始化完成，暂时无法保存")
      return
    }

    alert("当前笔录已创建并自动保存到数据库，可继续询问或返回主页。")
    showSaveModal.value = false
    router.push("/")
  } catch (error) {
    console.error("保存笔录失败:", error)
    alert("保存失败，请重试")
  }
}

const openTranscriptPreview = async () => {
  if (!recordId.value) {
    alert("笔录尚未初始化，无法预览")
    return
  }

  try {
    const response: any = await getTranscript(recordId.value)
    transcriptData.value = response.data
    showTranscriptModal.value = true
  } catch (error) {
    console.error("获取笔录数据失败:", error)
    alert("获取笔录数据失败，请稍后再试")
  }
}

const handleExportWord = async () => {
  if (!recordId.value) {
    alert("笔录尚未初始化，无法导出")
    return
  }

  try {
    const response: any = await exportRecordWord(recordId.value)
    const blob = response instanceof Blob
      ? response
      : new Blob([response], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `询问笔录_${formData.personName || "未知"}_${new Date().toISOString().slice(0, 10)}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error("导出Word失败:", error)
    alert("导出Word文档失败，请稍后再试")
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

const updateAnalysis = (extractedInfo: Record<string, string>) => {
  analysis.value = `案情：${extractedInfo.案情 || '未提供'}\n发生时间：${extractedInfo['发生时间'] || '未提供'}\n发生地点：${extractedInfo['发生地点'] || '未提供'}\n相关人员信息：${extractedInfo['相关人员信息'] || '未提供'}`
}

const appendAiResponse = (response: any) => {
  chatList.value.push({
    role: 'ai',
    content: response.ai_reply
  })
  recordText.value += `\nAI警官：${response.ai_reply}`

  if (response.extracted_info) {
    updateAnalysis(response.extracted_info)
  }

  speakAiQuestion(response.ai_reply, response.status)
}

const sendAudioMessage = async (audioFile: File) => {
  if (recordId.value === null) return

  try {
    isProcessing.value = true
    const response: any = await chatWithAudio({
      record_id: recordId.value,
      file: audioFile
    })

    const transcript = response.transcript?.trim()
    if (!transcript) return

    reporterInput.value = transcript
    chatList.value.push({
      role: 'user',
      content: transcript
    })
    recordText.value += `\n${respondentLabel.value}：${transcript}`
    reporterInput.value = ""

    appendAiResponse(response)
  } catch (error) {
    console.error("自动语音对话失败:", error)
  } finally {
    isProcessing.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  if (!reporterInput.value.trim() || recordId.value === null) return

  const messageText = reporterInput.value.trim()

  // 添加用户消息到聊天列表
  chatList.value.push({
    role: 'user',
    content: messageText
  })
  recordText.value += `\n${respondentLabel.value}：${messageText}`

  try {
    isProcessing.value = true
    const response: any = await chatWithAI({
      record_id: recordId.value,
      reporter_text: messageText
    })

    appendAiResponse(response)

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
  if ("speechSynthesis" in window) {
    loadVoiceOptions()
    window.speechSynthesis.addEventListener("voiceschanged", loadVoiceOptions)
  }

  initRecord()
})

onBeforeUnmount(() => {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.removeEventListener("voiceschanged", loadVoiceOptions)
  }
  stopRecording(false)
  cleanupRecordingResources()
  stopAiSpeech()
})

const pause = () => {
  isPaused.value = true
  stopRecording(false)
  if ("speechSynthesis" in window) {
    window.speechSynthesis.pause()
  }
  console.log("暂停")
}

const resume = () => {
  isPaused.value = false
  if ("speechSynthesis" in window) {
    window.speechSynthesis.resume()
  }
  if (!isAiSpeaking.value && !isRecording.value && !isProcessing.value && shouldContinueAutoConversation()) {
    startRecording('auto')
  }
  console.log("继续")
}
const print = () => openTranscriptPreview()
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
  flex-direction: column;
  align-items: flex-start;
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
  flex-wrap: wrap;
  justify-content: flex-start;
}

.record-window-actions {
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(114, 136, 177, 0.14);
}

.voice-control {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 220px;
  color: var(--text-soft);
  font-size: 13px;
}

.voice-control select {
  height: 46px;
  min-width: 170px;
  max-width: 260px;
  border: 1px solid rgba(114, 136, 177, 0.18);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--text-main);
  padding: 0 12px;
}

.voice-control select:focus {
  outline: none;
  border-color: rgba(29, 111, 216, 0.5);
  box-shadow: 0 0 0 4px rgba(29, 111, 216, 0.12);
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
  grid-template-columns: minmax(0, 1.2fr) 420px;
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
  flex-direction: column;
  align-items: flex-start;
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

.transcript-modal {
  width: min(960px, 100%);
  max-height: calc(100vh - 40px);
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-bottom: 1px solid rgba(114, 136, 177, 0.12);
}

.modal-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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

.transcript-body {
  overflow-y: auto;
}

.transcript-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 24px;
}

.transcript-section {
  margin-bottom: 22px;
}

.transcript-section h4 {
  margin: 0 0 12px;
  color: var(--text-main);
}

.transcript-info-row,
.case-info-item {
  display: flex;
  gap: 12px;
  line-height: 1.8;
}

.transcript-info-row span,
.case-info-item span {
  flex-shrink: 0;
  color: var(--text-soft);
}

.transcript-info-row strong,
.case-info-item strong {
  font-weight: 500;
  color: var(--text-main);
}

.transcript-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.transcript-table td {
  border: 1px solid rgba(114, 136, 177, 0.22);
  padding: 10px 12px;
  color: var(--text-main);
  word-break: break-word;
}

.transcript-table td:nth-child(odd) {
  width: 120px;
  background: rgba(29, 111, 216, 0.06);
  color: var(--text-soft);
  font-weight: 600;
}

.qa-pair {
  padding: 12px 0;
  border-bottom: 1px solid rgba(114, 136, 177, 0.12);
}

.qa-pair p,
.signature-section p {
  margin: 0 0 8px;
  line-height: 1.8;
  color: var(--text-main);
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
  justify-content: flex-start;
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
  justify-content: flex-start;
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
    justify-content: flex-start;
  }

  .record-window-actions {
    justify-content: flex-start;
  }

  .modal-header,
  .modal-footer {
    flex-wrap: wrap;
  }

  .transcript-table {
    min-width: 620px;
  }

  .transcript-section {
    overflow-x: auto;
  }

  .voice-control {
    width: 100%;
  }

  .voice-control select {
    flex: 1;
    max-width: none;
  }
}

</style>
