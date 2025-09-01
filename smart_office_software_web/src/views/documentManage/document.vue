<template>
  <div class="page-content">
    <h2>我的文档</h2>
    <FileUpload @uploaded="fetchFiles" />
    <div class="doc-list">
      <div class="doc-card" v-for="doc in docs" :key="doc.id" @click="openFile(doc)">
        <img :src="getFileTypeIcon(doc.fileType)" class="doc-cover" :alt="doc.fileName" />
        <div class="doc-info">
          <h3>{{ doc.fileName }}</h3>
          <p>{{ doc.desc }}</p>
          <div class="doc-meta">
            <span>大小：{{ formatFileSize(doc.fileSize) }}</span>
            <span>类型：{{ doc.fileType }}</span>
            <span>上传时间：{{ formatDate(doc.createdAt) }}</span>
          </div>
          <span class="delete-link" @click.stop="handleDeleteFile(doc.id)">删除</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FileUpload from '@/components/fileUpload/index.vue'
import { getFilesByUserId } from '@/api/file'
import { deleteFile } from '@/api/file'
import { ElMessage, ElMessageBox } from 'element-plus'

const docs = ref([])
const userInfo = ref(JSON.parse(localStorage.getItem('userInfo')))
const getFileTypeIcon = (fileType) => {
  const iconMap = {
    // 文档类型
    'doc': 'https://cdn-icons-png.flaticon.com/512/337/337932.png',  // Word文档
    'docx': 'https://cdn-icons-png.flaticon.com/512/337/337932.png', // Word文档
    'pdf': 'https://cdn-icons-png.flaticon.com/512/337/337946.png',  // PDF文档
    'txt': 'https://cdn-icons-png.flaticon.com/512/337/337956.png',  // 文本文件
    'html': 'https://cdn-icons-png.flaticon.com/512/337/337937.png', // html
    'js': 'https://cdn-icons-png.flaticon.com/512/337/337941.png', // js
    'mp3': 'https://cdn-icons-png.flaticon.com/512/337/337944.png', // mp3
    'php': 'https://cdn-icons-png.flaticon.com/512/337/337947.png', // php
    'sql': 'https://cdn-icons-png.flaticon.com/512/337/337953.png', // sql
    'xml': 'https://cdn-icons-png.flaticon.com/512/337/337959.png', // xml
    'zip': 'https://cdn-icons-png.flaticon.com/512/337/337960.png', // zip
    // 图片类型
    'jpg': 'https://cdn-icons-png.flaticon.com/512/337/337940.png', // jpg
    'png': 'https://cdn-icons-png.flaticon.com/512/337/337948.png',  // 图片
    'gif': 'https://cdn-icons-png.flaticon.com/512/337/337936.png', // gif
    // 表格类型
    'xls': 'https://cdn-icons-png.flaticon.com/512/337/337932.png',  // Excel表格
    'xlsx': 'https://cdn-icons-png.flaticon.com/512/337/337932.png', // Excel表格
    // 演示文稿
    'ppt': 'https://cdn-icons-png.flaticon.com/512/337/337949.png',  // PowerPoint
    'pptx': 'https://cdn-icons-png.flaticon.com/512/337/337932.337949', // PowerPoint
  }
  return iconMap[fileType.toLowerCase()] || 'https://cdn-icons-png.flaticon.com/512/337/337932.png' // 默认图标
}

//点击文件进入详情
const openFile = async (file) => {
  try {
    const res  = await fetch(file.filePath, { credentials: 'include' }) 
    if (!res.ok) throw new Error('网络请求失败 ' + res.status)
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = file.fileName || file.filePath.split('/').pop()
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('下载失败', err)
  }
}


const fetchFiles = async () => {
  try {
    const userId = userInfo.value.id
    const response = await getFilesByUserId(userId) // 默认用户ID为1
    docs.value = response.data
  } catch (error) {
    console.error('获取文件列表失败:', error)
  }
}

onMounted(() => {
  fetchFiles()
})

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleDeleteFile = async (fileId) => {
  try {
    await ElMessageBox.confirm('确定要删除该文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteFile(fileId)
    ElMessage.success('删除成功')
    await fetchFiles() // 删除后刷新
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.page-content {
  width: 100%;
  padding: 32px 0;
  background-color: #fff;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #1890ff;
}

.doc-list {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.doc-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  width: 260px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}

.doc-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
}

.scope-label {
  position: absolute;
  top: 10px;
  right: -30px;
  background: #1890ff;
  color: white;
  padding: 4px 30px;
  font-size: 12px;
  transform: rotate(45deg);
  z-index: 1;
}

.scope-label.team {
  background: #40a9ff;
}

.doc-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 16px;
  position: relative;
  z-index: 0;
}

.doc-info h3 {
  font-size: 18px;
  color: #1890ff;
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
  color: #8c8c8c;
}

.delete-btn {
  margin-top: 10px;
  background: #ff4d4f;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 6px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}
.delete-btn:hover {
  background: #d9363e;
}

.delete-link {
  position: absolute;
  right: 16px;
  bottom: 12px;
  color: #ff4d4f;
  font-size: 15px;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  transition: color 0.2s;
}
.delete-link:hover {
  color: #d9363e;
  text-decoration: underline;
}
</style>