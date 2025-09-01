<template>
  <div class="main-layout">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <img class="logo" src="https://picsum.photos/40/40?random=logo" alt="logo" />
        <span class="brand">智能办公</span>
      </div>
      <nav class="menu">
        <!-- <div class="menu-item" :class="{active: activeMenu === 'msg'}" @click="activeMenu = 'msg'"><i class="fas fa-envelope"></i> 我的消息</div> -->
        <div class="menu-item" :class="{active: activeMenu === 'doc'}" @click="activeMenu = 'doc'" ><i class="fas fa-folder"></i> 我的文档</div>
        <!-- <div class="menu-item"><i class="fas fa-share-alt"></i> 分享的项目</div> -->
        <div class="menu-item" v-if="showTeamMenu" :class="{active: activeMenu === 'team'}" @click="activeMenu = 'team'"><i class="fas fa-users"></i>团队管理</div>
        <div class="menu-item" :class="{active: activeMenu === 'schedule'}" @click="activeMenu = 'schedule'"><i class="fas fa-calendar-alt"></i> 日程管理</div>
        <div class="menu-item" :class="{active: activeMenu === 'assistant'}" @click="activeMenu = 'assistant'"><i class="fas fa-robot"></i> 智能助手</div>
      </nav>
      <!-- <button class="create-btn" v-if="activeMenu === 'doc'">新建文档</button> -->
    </aside>
    <!-- 右侧主内容区 -->
    <section class="main-content">
      <header class="topbar">
        <div class="nav-left">
          <span>工作台</span>
        </div>
        <div class="nav-right">
          <el-dropdown
          size="large">
            <h2 class="el-dropdown-link">
              设置
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </h2>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="editDialogVisible = true">修改</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <div class="content-area">
        <Document v-if="activeMenu === 'doc'" />
        <Team v-if="activeMenu === 'team'" />
        <Schedule v-if="activeMenu === 'schedule'" />
        <Assistant v-if="activeMenu === 'assistant'" />
      </div>
    </section>
    <!-- 个人信息编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="修改个人信息" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="editForm.password" type="password" placeholder="请输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Document from '@/views/documentManage/document.vue'
import Team from '@/views/teamManage/team.vue'
import Schedule from '@/views/scheduleManage/index.vue'
import Assistant from '@/views/smartAssistant/index.vue'
import { updateUser } from '@/api/login'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { logout } from '@/api/login.js'
const router = useRouter()
const activeMenu = ref('doc')
const docs = ref([
  { id: 1, title: '项目计划书', desc: '项目整体规划与目标说明。', author: '张三', date: '2024-04-02', cover: 'https://picsum.photos/80/80?random=401' },
  { id: 2, title: '需求文档', desc: '详细需求分析与功能列表。', author: '李四', date: '2024-04-10', cover: 'https://picsum.photos/80/80?random=402' },
  { id: 3, title: '技术白皮书', desc: '技术方案与实现细节。', author: '王五', date: '2024-04-15', cover: 'https://picsum.photos/80/80?random=403' }
])

const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
const showTeamMenu = userInfo.role === 0

const editDialogVisible = ref(false)
const editForm = ref({
  email: userInfo.email || '',
  password: ''
})

const submitEdit = async () => {
  if (!editForm.value.email) {
    ElMessage.warning('请输入邮箱')
    return
  }
  try {
    await updateUser(userInfo.id, {
      email: editForm.value.email,
      password: editForm.value.password
    })
    ElMessage.success('修改成功，请重新登录')
    editDialogVisible.value = false
    // 清除所有本地存储数据，包括token和用户信息
    localStorage.clear()
    // 退出登录并跳转到登录页
    router.replace('/login')
  } catch (e) {
    ElMessage.error('修改失败')
  }
}

const goBack = () => {
  router.push('/index')
}

const handleLogout = () => {
  logout()
  localStorage.clear()
  router.replace('/login')
}
</script>

<style scoped>
.example-showcase .el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
.main-layout {
  display: flex;
  height: 92vh;
  background: #fafbfc;
}
.sidebar {
  width: 240px;
  background: #fff;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 0 24px 0;
}
.sidebar-header {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 24px 0 2em 32px;
  box-sizing: border-box;
}
.logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  margin-right: 8px;
}
.brand {
  font-size: 20px;
  font-weight: bold;
  color: #1890ff;
  letter-spacing: 1px;
}
.profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  margin-bottom: 8px;
  border: 2px solid #e6e6e6;
}
.nickname {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 2px;
}
.email {
  font-size: 13px;
  color: #1890ff;
  margin-bottom: 8px;
}
.edit-btn {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  padding: 4px 16px;
  font-size: 13px;
  color: #333;
  margin-bottom: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.edit-btn:hover {
  background: #f6f6f6;
}
.profile-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
  gap: 10px;
}
.logout-btn {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  padding: 4px 16px;
  font-size: 13px;
  color: #d93026;
  margin-bottom: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.logout-btn:hover {
  background: #ffeaea;
}
.menu {
  width: 100%;
  margin-bottom: 16px;
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 32px;
  font-size: 15px;
  color: #333;
  cursor: pointer;
  border-radius: 6px;
  margin-bottom: 2px;
  transition: background 0.2s, color 0.2s;
}
.menu-item i {
  margin-right: 10px;
  font-size: 16px;
}
.menu-item.active, .menu-item:hover {
  background: #e6f7ff;
  color: #1890ff;
}
.create-btn {
  margin-top: auto;
  width: 80%;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 0;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 12px;
}
.create-btn:hover {
  background: #096dd9;
}
.back-btn {
  width: 100%;
  background: #fff;
  color: #666;
  border: none;
  border-bottom: 1px solid #e6e6e6;
  padding: 12px 32px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}
.back-btn:hover {
  background: #f6f6f6;
  color: #1890ff;
}
.back-btn i {
  margin-right: 8px;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.topbar {
  height: 5em;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  font-size: 15px;
}
.nav-left span {
  margin-right: 24px;
  font-size: 1.4em;
  color: #333;
  cursor: pointer;
}
.nav-left span:hover {
  color: #1890ff;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 4em;
}
.nav-right i {
  margin-left: 20px;
  font-size: 18px;
  color: #888;
  cursor: pointer;
  transition: color 0.2s;
}
.nav-right i:hover {
  color: #1890ff;
}
.content-area {
  padding: 0;
  padding-top: 0;
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: #fafbfc;
  /* padding-top: 32px; */
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #bbb;
  font-size: 16px;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  color: #e0e0e0;
}
.empty-text {
  color: #aaa;
  font-size: 16px;
}
.page-content {
  width: 100%;
  padding: 32px;
}
.doc-list {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-top: 24px;
}
.doc-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  width: 260px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.doc-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 16px;
}
.doc-info h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
}
.doc-info p {
  color: #666;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}
.doc-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #888;
}
</style>
