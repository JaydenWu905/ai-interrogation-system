import axios from "axios"

const service = axios.create({
  baseURL: "http://127.0.0.1:8000/api", // 后端地址
  timeout: 5000,
})

// 请求拦截（加 token）
service.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截
service.interceptors.response.use(
  (res) => res.data,
  (err) => {
    console.error("API Error:", err)
    return Promise.reject(err)
  }
)

export default service