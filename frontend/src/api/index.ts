import axios from 'axios'

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api", // 你的 Python 后端地址
  timeout: 5000,
})

export default api