// 引入 axios
import axios from 'axios'

// 封装 baseURL
const request = axios.create({
    baseURL:"http://localhost:8080",
    withCredentials: true,            // 关键：让浏览器带上 Cookie
    timeout: 8000
})

// 请求拦截器
request.interceptors.request.use(
    config => {
      // 从 localStorage 或 sessionStorage 里取出 token
      const token = localStorage.getItem("token") || sessionStorage.getItem("token")
      if (token) {
        // 加上 Bearer 前缀
        config.headers["Authorization"] = `Bearer ${token}`
      }
      return config
    },
    error => {
      return Promise.reject(error)
    }
  )

// 封装 baseURL
const aiRequest = axios.create({
    baseURL:"http://localhost:5000"
})

// 向外暴露 request
export default request
export {aiRequest}