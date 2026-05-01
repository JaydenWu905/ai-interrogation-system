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
