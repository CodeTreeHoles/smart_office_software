<template>
  <div class="schedule-container">
    <div class="schedule-header">
      <div class="header-left">
        <h2>日程管理</h2>
      </div>
      <div class="header-right">
        <el-date-picker
          v-model="currentDate"
          type="month"
          placeholder="选择年月"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          @change="handleMonthChange"
        />
        <el-button type="primary" @click="handleAddSchedule">新建日程</el-button>
      </div>
    </div>

    <div class="schedule-main-layout">
      <!-- 左侧日历 -->
      <div class="schedule-content">
        <div class="calendar-header">
          <span class="calendar-title">{{ formatYearMonth(currentDate) }}</span>
        </div>
        
        <div class="calendar-grid">
          <!-- 星期表头 -->
          <div class="week-header">
            <div v-for="day in weekDays" :key="day" class="week-day">{{ day }}</div>
          </div>
          
          <!-- 日期格子 -->
          <div class="days-grid">
            <div 
              v-for="(day, index) in calendarDays" 
              :key="index"
              class="day-cell"
              :class="{
                'other-month': !day.isCurrentMonth,
                'today': day.isToday,
                'selected': day.date === selectedDate,
                'has-schedule': getSchedulesByDate(day.date).length > 0
              }"
              @click="handleDateClick(day.date)"
            >
              <div class="day-number">{{ day.dayNumber }}</div>
              <div class="schedule-list">
                <div 
                  v-for="schedule in getSchedulesByDate(day.date)" 
                  :key="schedule.id"
                  class="schedule-item"
                  @click.stop="handleScheduleClick(schedule)"
                >
                  <span class="schedule-time">{{ formatScheduleTime(schedule.startTime) }}</span>
                  <span class="schedule-title">{{ schedule.eventName }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧日程详情 -->
      <div class="schedule-day-detail" v-if="showDayDetail">
        <DayView 
          :date="selectedDate" 
          @close="showDayDetail = false"
          @schedule-updated="handleScheduleUpdated"
        />
      </div>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getScheduleByUserId, addSchedule, updateSchedule, cancelScheduleById } from '@/api/schedule'
import DayView from '../scheduleManage/day.vue'

const router = useRouter()
const currentDate = ref(new Date())
const dialogVisible = ref(false)
const scheduleList = ref([])
const currentSchedule = ref({
  id: '',
  eventName: '',
  startTime: '',
  endTime: '',
  description: '',
  userId: '',
  dateStr: ''
})

// 右侧 day 详情相关
const showDayDetail = ref(false)
const selectedDate = ref('')

// 星期几的中文显示
const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 返回首页
const goToHome = () => {
  router.push('/index')
}

// 格式化年月显示
const formatYearMonth = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月`
}

// 处理月份变化
const handleMonthChange = (date) => {
  currentDate.value = new Date(date)
  fetchScheduleList()
}

// 获取日历数据
const calendarDays = computed(() => {
  const date = new Date(currentDate.value)
  const year = date.getFullYear()
  const month = date.getMonth()
  
  // 获取当月第一天
  const firstDay = new Date(year, month, 1)
  // 获取当月最后一天
  const lastDay = new Date(year, month + 1, 0)
  
  // 获取当月第一天是星期几
  const firstDayWeek = firstDay.getDay()
  
  // 获取上个月的最后几天
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  
  const days = []
  
  // 添加上个月的日期
  for (let i = firstDayWeek - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i
    days.push({
      date: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
      dayNumber: day,
      isCurrentMonth: false
    })
  }
  
  // 添加当月的日期
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const today = new Date()
    const isToday = today.getFullYear() === year && 
                   today.getMonth() === month && 
                   today.getDate() === i
    
    days.push({
      date: `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`,
      dayNumber: i,
      isCurrentMonth: true,
      isToday
    })
  }
  
  // 添加下个月的日期
  const remainingDays = 42 - days.length // 6行7列
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      date: `${year}-${String(month + 2).padStart(2, '0')}-${String(i).padStart(2, '0')}`,
      dayNumber: i,
      isCurrentMonth: false
    })
  }
  
  return days
})

// 获取日程列表
const fetchScheduleList = async () => {
  try {
    const userId = JSON.parse(localStorage.getItem('userInfo')).id
    const res = await getScheduleByUserId(userId)
    scheduleList.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('获取日程列表失败:', error)
    ElMessage.error('获取日程列表失败')
    scheduleList.value = []
  }
}

// 根据日期获取日程
const getSchedulesByDate = (date) => {
  if (!Array.isArray(scheduleList.value)) {
    return []
  }
  return scheduleList.value.filter(schedule => {
    const scheduleDate = schedule.startTime.split('T')[0]
    return scheduleDate === date
  })
}

// 格式化日程时间显示
const formatScheduleTime = (dateTime) => {
  const time = dateTime.split('T')[1]
  return time.substring(0, 5) // 只显示时:分
}

// 处理日期点击
const handleDateClick = (date) => {
  selectedDate.value = date
  showDayDetail.value = true
}

// 处理日程点击
const handleScheduleClick = (schedule) => {
  // 从ISO格式时间中提取日期和时间
  const startTime = schedule.startTime.split('T')[1]
  const endTime = schedule.endTime.split('T')[1]
  const dateStr = schedule.startTime.split('T')[0]

  currentSchedule.value = {
    id: schedule.id,
    eventName: schedule.eventName,
    startTime: startTime,
    endTime: endTime,
    description: schedule.description,
    userId: schedule.userId,
    dateStr: dateStr
  }
  dialogVisible.value = true
}

// 处理日程更新
const handleScheduleUpdated = () => {
  fetchScheduleList()
}

// 新建日程
const handleAddSchedule = () => {
  const userId = JSON.parse(localStorage.getItem('userInfo')).id
  const today = new Date()
  const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  
  currentSchedule.value = {
    eventName: '',
    startTime: '',
    endTime: '',
    description: '',
    userId: userId,
    dateStr: dateStr
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

    // 组合完整的日期时间，使用ISO格式
    const scheduleData = {
      ...currentSchedule.value,
      startTime: `${currentSchedule.value.startTime}`,
      endTime: `${currentSchedule.value.endTime}`
    }
    delete scheduleData.dateStr

    if (currentSchedule.value.id) {
      await updateSchedule(scheduleData)
      ElMessage.success('更新日程成功')
    } else {
      await addSchedule(scheduleData)
      ElMessage.success('添加日程成功')
    }
    dialogVisible.value = false
    fetchScheduleList()
  } catch (error) {
    console.error('保存日程失败:', error)
    ElMessage.error('保存日程失败')
  }
}

// 删除日程
const handleDeleteSchedule = async (schedule) => {
  try {
    await cancelScheduleById(schedule.id)
    ElMessage.success('删除日程成功')
    if (dialogVisible.value) {
      dialogVisible.value = false
    }
    fetchScheduleList()
  } catch (error) {
    ElMessage.error('删除日程失败')
  }
}

onMounted(() => {
  fetchScheduleList()
})
</script>

<style scoped>
.schedule-container {
  padding: 10px;
  background: #f5f7fa;
  height: 93vh;
  width: 100%;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: #fff;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.schedule-main-layout {
  display: flex;
  gap: 24px;
  height: calc(100vh - 160px);
}

.schedule-content {
  background: #fff;
  padding: 24px;
  height: 95%;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  flex: 1;
  min-width: 0;
}

.schedule-day-detail {
  width: 35em;
  min-width: 350px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.calendar-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px 0 16px;
}

.calendar-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.calendar-grid {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.week-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.week-day {
  padding: 12px;
  text-align: center;
  font-weight: 500;
  color: #606266;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  height: 100%;
}

.day-cell {
  min-height: 6.4vh;
  border-right: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.day-cell:hover {
  background-color: #f5f7fa;
}

.day-cell:nth-child(7n) {
  border-right: none;
}

.day-cell:nth-last-child(-n+7) {
  border-bottom: none;
}

.day-number {
  text-align: right;
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.day-cell.other-month {
  background-color: #fafafa;
}

.day-cell.other-month .day-number {
  color: #c0c4cc;
}

.day-cell.today .day-number {
  color: #409eff;
  font-weight: bold;
}

.day-cell.selected {
  background-color: #e6f7ff;
}

.day-cell.selected .day-number {
  color: #409eff;
  font-weight: bold;
}

.day-cell.has-schedule {
  background-color: #f0f9ff;
}

.schedule-list {
  overflow-y: auto;
  max-height: calc(100% - 24px);
}

.schedule-item {
  font-size: 12px;
  padding: 4px 8px;
  margin: 2px 0;
  background-color: #ecf5ff;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.3s;
}

.schedule-item:hover {
  background-color: #409eff;
  color: white;
}

.schedule-item:hover .schedule-time {
  color: white;
}

.schedule-time {
  margin-right: 4px;
  color: #409eff;
  font-weight: 500;
}

.schedule-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-button--primary.is-link) {
  font-weight: 500;
}
</style>
