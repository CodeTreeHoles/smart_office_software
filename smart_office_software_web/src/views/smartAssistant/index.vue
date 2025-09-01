<template>
  <div class="main-layout">
    <!-- 智能助手侧边栏 -->
    <aside class="sidebar">
      <nav class="menu">
        <div class="menu-item" :class="{active: activeMenu === 'chat'}" @click="activeMenu = 'chat'">
          <i class="fas fa-comments"></i>
        </div>
        <div class="menu-item" :class="{active: activeMenu === 'doc'}" @click="activeMenu = 'doc'">
          <i class="fas fa-book"></i>
        </div>
      </nav>
      <div class="sidebar-footer">
        <div class="avatar-btn">
          <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" alt="avatar" />
        </div>
      </div>
    </aside>
    <!-- 主内容区 -->
    <section class="main-content">
      <header class="topbar">
        <div class="nav-left">
          <span>智能助手</span>
        </div>
        <!-- 右上角图标已移除 -->
      </header>
      <div class="content-area">
        <Chat v-if="activeMenu === 'chat'" />
        <KnowledgeBase v-if="activeMenu === 'doc'" />
      </div>
    </section>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import Chat from '../smartAssistant/chat.vue'
import KnowledgeBase from '../smartAssistant/knowledgeBase.vue'
import '@fortawesome/fontawesome-free/css/all.css'
const activeMenu = ref('chat')
</script>
<style lang="scss" scoped>
.main-layout {
  display: flex;
  height: 95vh;
  width: 100%;
  .sidebar {
    width: 72px;
    background: #fff;
    border-right: 1px solid #eee;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0 24px 0;
    box-sizing: border-box;
    .menu {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 18px;
      flex: 1;
      margin-top: 32px;
      width: 100%;
      .menu-item {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        margin: 0 auto;
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
        color: #888;
        font-size: 22px;
        &:hover {
          background: #f0f6ff;
          color: #2563eb;
        }
        &.active {
          background: #e6f0ff;
          color: #2563eb;
        }
      }
    }
    .sidebar-footer {
      width: 100%;
      display: flex;
      justify-content: center;
      .avatar-btn {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        overflow: hidden;
        border: 2px solid #e6f0ff;
        box-shadow: 0 2px 8px rgba(37,99,235,0.08);
        cursor: pointer;
        transition: border 0.2s;
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        &:hover {
          border: 2px solid #2563eb;
        }
      }
    }
  }
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #f5f5f5;
    .topbar {
      height: 60px;
      background: #fff;
      border-bottom: 1px solid #eee;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 2.3em;
      .nav-right {
        i {
          font-size: 20px;
          color: #666;
          margin-left: 24px;
          cursor: pointer;
          &:hover {
            color: #1890ff;
          }
        }
      }
    }
    .content-area {
      flex: 1;
      padding: 1em;
    }
  }
}
</style> 