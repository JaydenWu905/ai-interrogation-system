import request from "@/utils/request"

// 开始新笔录
export const startRecord = (data: {
  caseType?: string
  caseName?: string
  personType?: string
  personName?: string
  idType?: string
  idNumber?: string
}) => {
  return request({
    url: "/v1/records/start",
    method: "POST",
    data: {
      case_type: data.caseType || "盗窃案",
      case_name: data.caseName || "",
      person_type: data.personType || "",
      person_name: data.personName || "",
      id_type: data.idType || "",
      id_number: data.idNumber || ""
    }
  })
}

// 与AI对话
export const chatWithAI = (data: {
  record_id: number
  reporter_text: string
}) => {
  return request({
    url: "/v1/records/chat",
    method: "POST",
    data
  })
}

// 语音输入并自动进入 AI 对话
export const chatWithAudio = (data: {
  record_id: number
  file: File
}) => {
  const formData = new FormData()
  formData.append("record_id", String(data.record_id))
  formData.append("file", data.file)

  return request({
    url: "/v1/records/chat-audio",
    method: "POST",
    data: formData,
    timeout: 120000,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  })
}

// 语音转文字
export const speechToText = (file: File) => {
  const formData = new FormData()
  formData.append("file", file)
  return request({
    url: "/v1/audio/speech-to-text",
    method: "POST",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  })
}

// 获取格式化笔录数据（预览用）
export const getTranscript = (recordId: number) => {
  return request({
    url: `/v1/records/${recordId}/transcript`,
    method: "GET"
  })
}

// 导出 Word 笔录
export const exportRecordWord = (recordId: number) => {
  return request({
    url: `/v1/records/${recordId}/export`,
    method: "GET",
    responseType: "blob",
    timeout: 120000
  })
}

// 提交电子签名
export const submitSignature = (data: {
  record_id: number
  signer_type: string
  signer_name: string
  signature_data: string
}) => {
  return request({
    url: `/v1/records/${data.record_id}/signature`,
    method: "POST",
    data
  })
}

// 获取笔录的所有签名
export const getSignatures = (recordId: number) => {
  return request({
    url: `/v1/records/${recordId}/signatures`,
    method: "GET"
  })
}

// 获取指定类型的签名图片
export const getSignatureImage = (recordId: number, signerType: string) => {
  return request({
    url: `/v1/records/${recordId}/signature/${encodeURIComponent(signerType)}`,
    method: "GET"
  })
}

// 更新笔录内容（手动编辑）
export const updateTranscript = (recordId: number, data: {
  person_info: Record<string, string>
  case_info: Record<string, string>
  qa_pairs: Array<{ question: string; answer: string }>
}) => {
  return request({
    url: `/v1/records/${recordId}/transcript`,
    method: "PUT",
    data
  })
}
