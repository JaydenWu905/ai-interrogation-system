import axios from "axios"

const service = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  timeout: 30000,
})


service.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")

  if (token) {
    // ⚠️ 确保 headers 存在
    config.headers = config.headers || {}
    config.headers.x_token = token
  }

  return config
})


service.interceptors.response.use(
  (res) => {
    return res.data
  },
  (err) => {
  if (err.response?.status === 401) {
    localStorage.removeItem("token")
    localStorage.removeItem("user")

    window.location.href = "/login"
  }

  return Promise.reject(err)
}
)

export default service