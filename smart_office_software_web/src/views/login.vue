<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-left">
        <div class="overlay"></div>
        <img :src="backgroundImage" alt="Background" class="background-image" />
        <div class="welcome-text">
          <h1>智能办公系统</h1>
          <p>提升工作效率，优化办公体验</p>
        </div>
      </div>
      <div class="login-right">
        <div class="login-form">
          <div class="form-header">
            <h2>欢迎回来</h2>
            <p class="subtitle">请登录您的账号</p>
          </div>
          
          <div class="form-group">
            <div class="input-wrapper">
              <i class="fas fa-user"></i>
              <input 
                type="text" 
                id="account" 
                v-model="account" 
                placeholder="请输入工号"
              />
            </div>
          </div>
          
          <div class="form-group">
            <div class="input-wrapper">
              <i class="fas fa-lock"></i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password" 
                placeholder="请输入密码"
              />
              <i 
                class="fas" 
                :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"
                @click="showPassword = !showPassword"
              ></i>
            </div>
          </div>
          
          <button class="login-button" @click="handleLogin" :disabled="isLoading">
            <span v-if="!isLoading">登录</span>
            <i v-else class="fas fa-spinner fa-spin"></i>
          </button>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/login'
import { getDepartmentByUserId } from '@/api/department'
import { ElMessage } from 'element-plus'

const router = useRouter()
const account = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const backgroundImage = ref('https://picsum.photos/1920/1080?random=1')

const handleLogin = async () => {
  if (!account.value || !password.value) {
    ElMessage.warning('请输入工号和密码')
    return
  }

  isLoading.value = true
  try {
    const res = await login({
      account: account.value,
      password: password.value,
    })
    console.log(res);
    
    if(res.data.code == 0) {
      console.log('登录成功:', res.data)
      ElMessage.success('欢迎回来,'+res.data.data.account)
      // 存储用户信息到localStorage
      localStorage.setItem('userInfo', JSON.stringify(res.data.data))
      
      // 存储token
      localStorage.setItem('token', res.data.data.token)
      const department = await getDepartmentByUserId(res.data.data.id)
      localStorage.setItem('departmentId', JSON.stringify(department.data.data))
      // 如果勾选了记住我,则保存账号密码
      localStorage.removeItem('account')
      localStorage.removeItem('password') 
      router.replace('/index')
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    console.error('登录失败：', error)
    ElMessage.error(error.message || '登录失败，请重试')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 添加全局样式 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  height: 100%;
  width: 100%;
  overflow: hidden;
}
</style>

<style scoped>
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  overflow: hidden;
}

.login-box {
  display: flex;
  width: 1000px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-left {
  flex: 1.2;
  position: relative;
  overflow: hidden;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(0,0,0,0.6), rgba(0,0,0,0.3));
  z-index: 1;
}

.background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.login-left:hover .background-image {
  transform: scale(1.05);
}

.welcome-text {
  position: absolute;
  bottom: 40px;
  left: 40px;
  color: white;
  z-index: 2;
}

.welcome-text h1 {
  font-size: 32px;
  margin-bottom: 10px;
  font-weight: 600;
}

.welcome-text p {
  font-size: 16px;
  opacity: 0.9;
}

.login-right {
  flex: 1;
  padding: 40px;
  display: flex;
  align-items: center;
}

.login-form {
  width: 100%;
}

.form-header {
  margin-bottom: 40px;
}

h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.form-group {
  margin-bottom: 24px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper i {
  position: absolute;
  left: 12px;
  color: #666;
}

.input-wrapper i:last-child {
  left: auto;
  right: 12px;
  cursor: pointer;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 12px 40px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

input[type="text"]:focus,
input[type="password"]:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
  outline: none;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.forgot-password {
  color: #4a90e2;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.forgot-password:hover {
  color: #357abd;
}

.login-button {
  width: 100%;
  padding: 14px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-button:hover:not(:disabled) {
  background-color: #357abd;
  transform: translateY(-1px);
}

.login-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-link {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.register-link:hover {
  color: #357abd;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.fa-spinner {
  animation: spin 1s linear infinite;
}
</style>
