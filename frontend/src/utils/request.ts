import axios from "axios"

const service = axios.create({
  baseURL: "https://m1.apifoxmock.com/m1/8016126-7770654-7390704/api",
  timeout: 5000,
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