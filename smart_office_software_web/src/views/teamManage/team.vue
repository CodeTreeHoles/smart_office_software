<template>
  <div class="page-content">
    <div class="header-row">
      <h2>团队管理</h2>
      <button class="add-dept-btn-inline" @click="showAddDeptDialog">新增部门</button>
    </div>
    <div v-if="loading" class="loading-state">加载中...</div>
    <template v-else>
      <div v-if="!showDetail">
        <div v-if="teamList.length === 0" class="empty-state">
          <i class="fas fa-users-cog empty-icon"></i>
          <div class="empty-text">没有加入任何组织</div>
        </div>
        <div v-else class="team-list">
          <div v-for="team in teamList" :key="team.id" class="team-card" @click="goToDept(team.id)" style="cursor:pointer">
            <div class="team-card-bar"></div>
            <div class="team-header">
              <i class="fas fa-users-cog team-icon"></i>
              <span class="team-name">{{ team.deptName }}</span>
            </div>
            <div class="team-intro">{{ team.deptIntro }}</div>
            <div class="team-info">
              <span class="info-item"><i class="fas fa-user-tie info-icon"></i> 负责人：{{ team.leader }}</span>
              <span class="info-item"><i class="fas fa-calendar-alt info-icon"></i> 创建时间：{{ formatDate(team.createdAt) }}</span>
            </div>
            <div class="team-actions">
              <button class="team-action-btn edit" @click.stop="editTeam(team)">编辑</button>
              <button class="team-action-btn delete" @click.stop="deleteTeam(team)">删除</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <button class="back-btn-prominent" @click="backToList">返回团队列表</button>
        <div class="team-detail-card">
          <div class="team-header">
            <i class="fas fa-users-cog team-icon"></i>
            <span class="team-name">{{ currentTeamDetail.deptName }}</span>
          </div>
          <div class="team-intro">{{ currentTeamDetail.deptIntro }}</div>
          <div class="team-info">
            <span class="info-item"><i class="fas fa-user-tie info-icon"></i> 负责人：{{ currentTeamDetail.leader }}</span>
            <span class="info-item"><i class="fas fa-calendar-alt info-icon"></i> 创建时间：{{ formatDate(currentTeamDetail.createdAt) }}</span>
          </div>
        </div>
        <div v-if="currentTeamDetail.userList && currentTeamDetail.userList.length > 0" class="user-list-wide">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <h4>成员列表</h4>
            <button class="user-action-btn add prominent" @click="showAddUserDialog">新增成员</button>
          </div>
          <table class="user-table-wide">
            <thead>
              <tr>
                <th>账号</th>
                <th>邮箱</th>
                <th style="width:120px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in currentTeamDetail.userList" :key="user.id">
                <td>{{ user.account }}</td>
                <td>{{ user.email || '—' }}</td>
                <td>
                  <button class="user-action-btn edit" @click.stop="editUser(user)">修改</button>
                  <button class="user-action-btn delete" @click.stop="deleteUser(user)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else style="color:#aaa;margin-top:16px;text-align:center;">
          暂无成员
          <div style="margin-top:16px;">
            <button class="user-action-btn add prominent" @click="showAddUserDialog">新增成员</button>
          </div>
        </div>
      </div>
    </template>
  </div>
  <!-- 新增/编辑成员弹窗 -->
  <el-dialog v-model="showUserDialog" :title="isEditUser ? '编辑成员' : '新增成员'" width="400px">
    <el-form :model="addUserForm" label-width="60px">
      <el-form-item label="账号">
        <el-input v-model="addUserForm.account" autocomplete="off" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="addUserForm.email" autocomplete="off" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showUserDialog = false">取消</el-button>
      <el-button type="primary" @click="submitUser">确定</el-button>
    </template>
  </el-dialog>
  <el-dialog v-model="showDeptDialog" :title="isEditDept ? '编辑部门' : '新增部门'" width="400px">
    <el-form :model="deptForm" label-width="80px">
      <el-form-item label="部门名称">
        <el-input v-model="deptForm.deptName" autocomplete="off" />
      </el-form-item>
      <el-form-item label="简介">
        <el-input v-model="deptForm.deptIntro" autocomplete="off" />
      </el-form-item>
      <el-form-item label="负责人工号">
        <el-input v-model="deptForm.leaderJobNumber" autocomplete="off" placeholder="可选，新增部门时可不填" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showDeptDialog = false">取消</el-button>
      <el-button type="primary" @click="submitDept">{{ isEditDept ? '保存' : '新增' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDepartmentList, getDepartmentDetail, addTeamUser, updateTeamUser, deleteTeamUser, addDepartment, updateDepartment, deleteDepartment } from '@/api/department.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const teamList = ref([])
const loading = ref(true)
const router = useRouter()
const currentTeamDetail = ref(null)
const showDetail = ref(false)
const showUserDialog = ref(false)
const isEditUser = ref(false)
const editUserId = ref(null)
const addUserForm = ref({
  account: '',
  email: ''
})
const showDeptDialog = ref(false)
const isEditDept = ref(false)
const deptForm = ref({
  id: null,
  deptName: '',
  deptIntro: '',
  leaderId: null,
  leaderJobNumber: ''
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

const goToDept = async (deptId) => {
  try {
    const res = await getDepartmentDetail(deptId)
    if (res && res.data) {
      currentTeamDetail.value = res.data.data
      showDetail.value = true
    } else {
      ElMessage.error('获取部门详情失败')
    }
  } catch (e) {
    ElMessage.error('获取部门详情失败')
  }
}

const backToList = () => {
  showDetail.value = false
  currentTeamDetail.value = null
}

const fetchTeams = async () => {
  loading.value = true
  try {
    // const userId = JSON.parse(localStorage.getItem('userInfo')).id
    const res = await getDepartmentList()
    if (res && res.data && Array.isArray(res.data.data)) {
      teamList.value = res.data.data
      console.log(res)
    } else {
      teamList.value = []
    }
  } catch (e) {
    ElMessage.error('获取团队信息失败')
    teamList.value = []
  } finally {
    loading.value = false
  }
}

const fetchCurrentTeamDetail = async () => {
  if (!currentTeamDetail.value?.id) return
  try {
    const res = await getDepartmentDetail(currentTeamDetail.value.id)
    if (res && res.data) {
      currentTeamDetail.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('刷新团队详情失败')
  }
}

const editUser = (user) => {
  isEditUser.value = true
  editUserId.value = user.id
  addUserForm.value = {
    account: user.account,
    email: user.email || ''
  }
  showUserDialog.value = true
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm('确定要删除该成员吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteTeamUser(currentTeamDetail.value.id, user.id)
    ElMessage.success('删除成功')
    await fetchCurrentTeamDetail()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const showAddUserDialog = () => {
  isEditUser.value = false
  editUserId.value = null
  addUserForm.value = { account: '', email: '' }
  showUserDialog.value = true
}

const submitUser = async () => {
  if (!addUserForm.value.account) {
    ElMessage.warning('请输入账号')
    return
  }
  try {
    if (isEditUser.value) {
      await updateTeamUser(currentTeamDetail.value.id, editUserId.value, addUserForm.value)
      ElMessage.success('修改成功')
    } else {
      await addTeamUser(currentTeamDetail.value.id, addUserForm.value)
      ElMessage.success('新增成功')
    }
    showUserDialog.value = false
    addUserForm.value = { account: '', email: '' }
    await fetchCurrentTeamDetail()
  } catch (e) {
    ElMessage.error(isEditUser.value ? '修改失败' : '新增失败')
  }
}

// 编辑部门
const editTeam = (team) => {
  isEditDept.value = true
  // 先获取部门详情，确保 currentTeamDetail.userList 有数据
  getDepartmentDetail(team.id).then(res => {
    if (res && res.data && res.data.data) {
      currentTeamDetail.value = res.data.data
      let leaderJobNumber = ''
      if (currentTeamDetail.value.userList && team.leaderId) {
        const leader = currentTeamDetail.value.userList.find(u => u.id === team.leaderId)
        leaderJobNumber = leader ? leader.account : ''
      }
      deptForm.value = { ...team, leaderJobNumber }
      showDeptDialog.value = true
    }
  })
}

// 删除部门
const deleteTeam = async (team) => {
  try {
    await ElMessageBox.confirm('确定要删除该部门吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteDepartment(team.id)
    ElMessage.success('删除成功')
    fetchTeams()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const showAddDeptDialog = () => {
  isEditDept.value = false
  deptForm.value = {
    id: null,
    deptName: '',
    deptIntro: '',
    leaderId: null,
    leaderJobNumber: ''
  }
  showDeptDialog.value = true
}

const submitDept = async () => {
  if (!deptForm.value.deptName) {
    ElMessage.warning('请输入部门名称')
    return
  }

  // 新增部门时可以不填负责人
  if (isEditDept.value) {
    // 编辑部门时，负责人仍然必填
    if (!deptForm.value.leaderJobNumber) {
      ElMessage.warning('请输入负责人工号')
      return
    }
    // 用当前部门详情的成员列表查找
    let userList = currentTeamDetail.value && currentTeamDetail.value.userList ? currentTeamDetail.value.userList : []
    const leader = userList.find(u => u.account === deptForm.value.leaderJobNumber)
    if (!leader) {
      ElMessage.error('该工号不在当前部门成员中')
      return
    }
    deptForm.value.leaderId = leader.id
  } else {
    // 新增部门时，如果填写了负责人，则校验
    if (deptForm.value.leaderJobNumber) {
      // 新增时没有成员列表，不能校验，直接传递 leaderJobNumber 字段
      // 这里假设后端会根据 leaderJobNumber 处理
    } else {
      // 没有填写负责人，清空 leaderId
      deptForm.value.leaderId = null
      deptForm.value.leaderJobNumber = ''
    }
  }

  try {
    if (isEditDept.value) {
      await updateDepartment(deptForm.value)
      ElMessage.success('修改成功')
    } else {
      await addDepartment(deptForm.value)
      ElMessage.success('新增成功')
    }
    showDeptDialog.value = false
    fetchTeams()
  } catch (e) {
    ElMessage.error(isEditDept.value ? '修改失败' : '新增失败')
  }
}

onMounted(() => {
  fetchTeams()
})
</script>

<style scoped>
.page-content {
  width: 100%;
  padding: 32px;
}
.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.add-dept-btn-inline {
  background: linear-gradient(90deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 24px;
  padding: 8px 32px;
  box-shadow: 0 2px 12px rgba(64,158,255,0.10);
  cursor: pointer;
  letter-spacing: 1px;
  transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
}
.add-dept-btn-inline:hover, .add-dept-btn-inline:focus {
  background: linear-gradient(90deg, #66b1ff 0%, #409eff 100%);
  box-shadow: 0 4px 24px rgba(64,158,255,0.18);
  transform: translateY(-2px) scale(1.04);
}
.loading-state {
  text-align: center;
  color: #aaa;
  font-size: 18px;
  margin: 40px 0;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #bbb;
  font-size: 16px;
  margin-top: 40px;
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
.team-list {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  margin-top: 32px;
  justify-content: flex-start;
}
.team-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(64,158,255,0.10);
  padding: 32px 32px 24px 32px;
  min-width: 300px;
  max-width: 360px;
  flex: 1 1 320px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  position: relative;
  transition: box-shadow 0.25s, transform 0.25s;
  border: 1.5px solid #f0f4fa;
}
.team-card-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 6px;
  border-radius: 16px 16px 0 0;
  background: linear-gradient(90deg, #409eff 0%, #66b1ff 100%);
}
.team-card:hover {
  box-shadow: 0 8px 32px 0 rgba(64,158,255,0.18);
  transform: translateY(-4px) scale(1.02);
  border-color: #a0cfff;
}
.team-header {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 4px;
}
.team-icon {
  font-size: 32px;
  color: #409eff;
}
.team-name {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
}
.team-intro {
  color: #444;
  font-size: 16px;
  margin-bottom: 10px;
  padding-left: 2px;
}
.team-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #888;
  font-size: 14px;
  margin-top: 4px;
}
.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.info-icon {
  font-size: 15px;
  color: #a0cfff;
}
@media (max-width: 900px) {
  .team-list {
    flex-direction: column;
    gap: 20px;
  }
  .team-card {
    max-width: 100%;
    min-width: 0;
    padding: 24px 16px 16px 16px;
  }
  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .add-dept-btn-inline {
    width: 100%;
    font-size: 15px;
    padding: 8px 0;
  }
}
.team-detail-card {
  max-width: 500px;
  margin: 0 auto 32px auto;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(64,158,255,0.10);
  padding: 32px 32px 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  border: 1.5px solid #f0f4fa;
}
.user-list-wide {
  width: 90%;
  margin: 0 auto;
  margin-top: 24px;
}
.user-table-wide {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}
.user-table-wide th, .user-table-wide td {
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  text-align: left;
}
.user-table-wide th {
  background: #f6f8fa;
}
.user-action-btn {
  margin-right: 8px;
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}
.user-action-btn.edit {
  background: #e6f7ff;
  color: #1890ff;
}
.user-action-btn.edit:hover {
  background: #bae7ff;
}
.user-action-btn.delete {
  background: #fff1f0;
  color: #ff4d4f;
}
.user-action-btn.delete:hover {
  background: #ffa39e;
  color: #fff;
}
.user-action-btn.add {
  background: #52c41a;
  color: #fff;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(82,196,26,0.10);
  border: none;
  transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
}
.user-action-btn.add:hover, .user-action-btn.add:focus {
  background: #73d13d;
  box-shadow: 0 4px 16px rgba(82,196,26,0.18);
  transform: translateY(-2px) scale(1.04);
}
.user-action-btn.add.prominent {
  font-size: 16px;
  padding: 8px 28px;
  border-radius: 24px;
  letter-spacing: 1px;
  margin: 0 0 0 12px;
  box-shadow: 0 4px 16px rgba(82,196,26,0.15);
}
.back-btn-prominent {
  display: inline-block;
  background: linear-gradient(90deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 24px;
  padding: 8px 32px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(64,158,255,0.10);
  cursor: pointer;
  letter-spacing: 1px;
  transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
}
.back-btn-prominent:hover, .back-btn-prominent:focus {
  background: linear-gradient(90deg, #66b1ff 0%, #409eff 100%);
  box-shadow: 0 4px 24px rgba(64,158,255,0.18);
  transform: translateY(-2px) scale(1.04);
}
.team-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}
.team-action-btn {
  padding: 4px 14px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}
.team-action-btn.edit {
  background: #e6f7ff;
  color: #1890ff;
}
.team-action-btn.edit:hover {
  background: #bae7ff;
}
.team-action-btn.delete {
  background: #fff1f0;
  color: #ff4d4f;
}
.team-action-btn.delete:hover {
  background: #ffa39e;
  color: #fff;
}
/* 移除原有右下角悬浮按钮样式 */
.add-dept-btn {
  display: none;
}
</style> 