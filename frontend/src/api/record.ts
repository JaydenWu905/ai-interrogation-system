import request from "@/utils/request"

// 开始新笔录
export const startRecord = (data: {
  reporter_name: string
  case_type?: string
}) => {
  return request({
    url: "/v1/records/start",
    method: "POST",
    data
  })
}

// 与AI对话
export const chatWithAI = (data: {
  record_id: string
  reporter_text: string
}) => {
  return request({
    url: "/v1/records/chat",
    method: "POST",
    data
  })
}

// 语音转文字
export const speechToText = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: "/v1/audio/speech-to-text",
    method: "POST",
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const createRecord = (data: any) => {
  return request({
    url: "/v1/record/create", // 后端接口
    method: "POST",
    data
  })
}