<template>
  <div class="document-viewer">
    <div class="upload-section">
      <el-upload
        class="upload-demo"
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
        accept=".doc,.docx,.xlsx,.pdf"
      >
        <el-button type="primary">
          <i class="fas fa-upload"></i> 上传文档
        </el-button>
      </el-upload>
    </div>

    <div v-if="currentDoc" class="document-preview">
      <div class="preview-header">
        <div class="doc-info">
          <i :class="getFileIcon(currentDoc.type)" class="doc-icon"></i>
          <span class="doc-name">{{ currentDoc.name }}</span>
        </div>
        <el-button type="primary" link @click="clearDocument">
          <i class="fas fa-times"></i> 关闭
        </el-button>
      </div>
      <div class="preview-content">
        <iframe v-if="previewUrl" :src="previewUrl" frameborder="0"></iframe>
        <div v-else class="no-preview">
          暂不支持该类型文档的预览
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <i class="fas fa-file-upload empty-icon"></i>
      <div class="empty-text">请上传文档</div>
      <div class="empty-desc">支持 .doc、.docx、.xlsx、.pdf 格式</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const currentDoc = ref(null)
const previewUrl = ref('')

// 获取文件图标
const getFileIcon = (fileType) => {
  const iconMap = {
    'doc': 'fas fa-file-word',
    'docx': 'fas fa-file-word',
    'xlsx': 'fas fa-file-excel',
    'pdf': 'fas fa-file-pdf'
  }
  return iconMap[fileType.toLowerCase()] || 'fas fa-file'
}

// 处理文件上传
const handleFileChange = async (file) => {
  try {
    // 这里应该调用后端API上传文件并获取预览URL
    // 暂时使用本地预览
    const fileUrl = URL.createObjectURL(file.raw)
    currentDoc.value = {
      name: file.name,
      type: file.name.split('.').pop(),
      size: file.size
    }
    previewUrl.value = fileUrl
  } catch (error) {
    ElMessage.error('文件处理失败')
  }
}

// 清除当前文档
const clearDocument = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  currentDoc.value = null
  previewUrl.value = ''
}
</script>

<style lang="scss" scoped>
.document-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

  .upload-section {
    padding: 16px;
    border-bottom: 1px solid #eee;
  }

  .document-preview {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .preview-header {
      padding: 16px;
      border-bottom: 1px solid #eee;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .doc-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .doc-icon {
          font-size: 24px;
          color: #409eff;
        }

        .doc-name {
          font-size: 16px;
          color: #333;
        }
      }
    }

    .preview-content {
      flex: 1;
      background: #f5f7fa;
      overflow: hidden;

      iframe {
        width: 100%;
        height: 100%;
        border: none;
      }

      .no-preview {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #999;
        font-size: 16px;
      }
    }
  }

  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #999;
    
    .empty-icon {
      font-size: 48px;
      margin-bottom: 16px;
      color: #dcdfe6;
    }
    
    .empty-text {
      font-size: 16px;
      margin-bottom: 8px;
    }
    
    .empty-desc {
      font-size: 14px;
      color: #909399;
    }
  }
}
</style> 