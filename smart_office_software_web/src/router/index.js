// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/login.vue'
import DocumentManage from '@/views/index.vue'
import SetKnowledgeBase from '@/views/smartAssistant/setKnowledgeBase.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path:'/smart-assistant/knowledge-base/:id',
    name: 'SetKnowledgeBase',
    component: SetKnowledgeBase,
    meta: { requiresAuth: true }
  },
  {
    path: '/index',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'DocumentManage',
    component: DocumentManage,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    // 检查是否有token
    const token = localStorage.getItem('token')
    if (!token) {
      // 没有token，重定向到登录页
      next('/login')
    } else {
      // 有token，允许访问
      next()
    }
  } else {
    // 不需要认证的路由，直接允许访问
    next()
  }
})

export default router
