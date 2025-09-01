<template>
  <div class="day-schedule-container">
    <div class="schedule-header">
      <div class="header-left">
        <el-button @click="handleClose">关闭</el-button>
        <h3>{{ formatDate(currentDate) }} 日程安排</h3>
      </div>
      <el-button type="primary" @click="handleAddSchedule">新建日程</el-button>
    </div>

    <div class="schedule-content">
      <el-timeline>
        <el-timeline-item
          v-for="schedule in scheduleList"
          :key="schedule.id"
          :type="getTimelineItemType(schedule)"
          :timestamp="formatDateTime(schedule.startTime)"
          placement="top"
        >
          <el-card class="schedule-card">
            <template #header>
              <div class="schedule-card-header">
                <span class="schedule-title">{{ schedule.eventName }}</span>
                <div class="schedule-actions">
                  <el-button type="primary" link @click="handleEditSchedule(schedule)">编辑</el-button>
                  <el-button type="danger" link @click="handleDeleteSchedule(schedule)">删除</el-button>
                </div>
              </div>
            </template>
            <div class="schedule-info">
              <p class="schedule-time">
                <el-icon><Clock /></el-icon>
                {{ formatDateTime(schedule.startTime) }} - {{ formatDateTime(schedule.endTime) }}
              </p>
              <p class="schedule-desc" v-if="schedule.description">
                <el-icon><Document /></el-icon>
                {{ schedule.description }}
              </p>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 日程编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentSchedule.id ? '编辑日程' : '新建日程'"
      width="500px"
    >
      <el-form :model="currentSchedule" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="currentSchedule.eventName" placeholder="请输入日程标题" />
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker
            v-model="currentSchedule.startTime"
            type="datetime"
            placeholder="开始时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
          <span class="mx-2">至</span>
          <el-date-picker
            v-model="currentSchedule.endTime"
            type="datetime"
            placeholder="结束时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="currentSchedule.description"
            type="textarea"
            placeholder="请输入日程描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveSchedule">确定</el-button>
          <el-button 
            v-if="currentSchedule.id" 
            type="danger" 
            @click="handleDeleteSchedule(currentSchedule)"
          >删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getScheduleBydate, addSchedule, updateSchedule, cancelScheduleById } from '@/api/schedule'

// 定义props
const props = defineProps({
  date: {
    type: String,
    required: true
  }
})

// 定义emits
const emit = defineEmits(['close', 'schedule-updated'])

const currentDate = ref(props.date)
const scheduleList = ref([])
const dialogVisible = ref(false)
const currentSchedule = ref({
  id: '',
  eventName: '',
  startTime: '',
  endTime: '',
  description: '',
  userId: ''
})

// 格式化日期显示
const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

// 格式化日期时间显示
const formatDateTime = (dateTime) => {
  const d = new Date(dateTime)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 关闭组件
const handleClose = () => {
  emit('close')
}

// 获取日程列表
const fetchScheduleList = async () => {
  try {
    const userId = JSON.parse(localStorage.getItem('userInfo')).id
    const res = await getScheduleBydate(userId, currentDate.value)
    scheduleList.value = Array.isArray(res.data.data) ? res.data.data : []
  } catch (error) {
    console.error('获取日程列表失败:', error)
    ElMessage.error('获取日程列表失败')
    scheduleList.value = []
  }
}

// 获取时间线项目类型
const getTimelineItemType = (schedule) => {
  const now = new Date()
  const scheduleTime = new Date(schedule.startTime)
  if (scheduleTime < now) {
    return 'info'
  }
  return 'primary'
}

// 新建日程
const handleAddSchedule = () => {
  const userId = JSON.parse(localStorage.getItem('userInfo')).id
  currentSchedule.value = {
    id: '',
    eventName: '',
    startTime: '',
    endTime: '',
    description: '',
    userId: userId
  }
  dialogVisible.value = true
}

// 编辑日程
const handleEditSchedule = (schedule) => {
  currentSchedule.value = {
    id: schedule.id,
    eventName: schedule.eventName,
    startTime: schedule.startTime,
    endTime: schedule.endTime,
    description: schedule.description,
    userId: schedule.userId
  }
  dialogVisible.value = true
}

// 保存日程
const handleSaveSchedule = async () => {
  try {
    if (!currentSchedule.value.eventName) {
      ElMessage.warning('请输入日程标题')
      return
    }
    if (!currentSchedule.value.startTime || !currentSchedule.value.endTime) {
      ElMessage.warning('请选择开始和结束时间')
      return
    }

    const scheduleData = {
      ...currentSchedule.value,
      startTime: currentSchedule.value.startTime,
      endTime: currentSchedule.value.endTime
    }

    if (currentSchedule.value.id) {
      await updateSchedule(scheduleData)
      ElMessage.success('更新日程成功')
    } else {
      await addSchedule(scheduleData)
      ElMessage.success('添加日程成功')
    }
    dialogVisible.value = false
    fetchScheduleList()
    emit('schedule-updated')
  } catch (error) {
    console.error('保存日程失败:', error)
    ElMessage.error('保存日程失败')
  }
}

// 删除日程
const handleDeleteSchedule = async (schedule) => {
  try {
    await ElMessageBox.confirm('确定要删除这个日程吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await cancelScheduleById(schedule.id)
    ElMessage.success('删除日程成功')
    if (dialogVisible.value) {
      dialogVisible.value = false
    }
    fetchScheduleList()
    emit('schedule-updated')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除日程失败')
    }
  }
}

// 监听日期变化
watch(() => props.date, (newDate) => {
  currentDate.value = newDate
  fetchScheduleList()
}, { immediate: true })

// 暴露方法给父组件
defineExpose({
  fetchScheduleList
})

onMounted(() => {
  fetchScheduleList()
})
</script>

<style scoped>
.day-schedule-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.schedule-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.schedule-card {
  margin-bottom: 8px;
}

.schedule-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.schedule-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.schedule-actions {
  display: flex;
  gap: 8px;
}

.schedule-info {
  color: #606266;
}

.schedule-time {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
}

.schedule-desc {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 8px 0;
  line-height: 1.5;
}

.mx-2 {
  margin: 0 8px;
}

:deep(.el-timeline-item__node) {
  background-color: #409eff;
}

:deep(.el-timeline-item__tail) {
  border-left: 2px solid #e4e7ed;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 13px;
}
</style> 