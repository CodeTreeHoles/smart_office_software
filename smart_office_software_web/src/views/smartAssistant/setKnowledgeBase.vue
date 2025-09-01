<template>
  <div class="page-content">
    <div class="header">
      <div class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
        返回
      </div>
      <h1>知识库设置</h1>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane label="基本信息" name="basic">
        <div class="tab-content">
          <el-form :model="kbInfo" label-width="100px">
            <el-form-item label="知识库名称">
              <el-input v-model="kbInfo.kb_name" placeholder="请输入知识库名称" />
            </el-form-item>
            <el-form-item label="知识库图标">
              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
                :auto-upload="false"
                :on-change="handleImageChange"
              >
                <img v-if="kbInfo.img" :src="kbInfo.img" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item label="知识库描述">
              <el-input
                v-model="kbInfo.description"
                type="textarea"
                rows="4"
                placeholder="请输入知识库描述"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasicInfo">保存修改</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <el-tab-pane label="文档管理" name="documents">
        <div class="tab-content">
          <div class="doc-header">
            <el-button type="primary" @click="showUploadDialog">
              <i class="fas fa-upload"></i> 添加文档
            </el-button>
          </div>

          <el-table :data="documents" style="width: 100%">
            <el-table-column prop="file_name" label="文档名称" />
            <el-table-column prop="file_type" label="类型" width="120" />
            <el-table-column prop="file_size" label="大小" width="120" />
            <el-table-column prop="created_at" label="上传时间" width="180" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <!-- <el-button type="primary" link @click="previewDocument(scope.row)">
                  预览
                </el-button> -->
                <el-button type="danger" link @click="deleteDocument(scope.row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加文档对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="添加文档到知识库"
      width="60%"
    >
      <el-table
        :data="userDocuments"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="fileName" label="文档名称" />
        <el-table-column prop="fileType" label="类型" width="120" />
        <el-table-column prop="fileSize" label="大小" width="120" />
        <el-table-column prop="updatedAt" label="上传时间" width="180" />
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddDocuments">
            确认添加
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  updateKnowledgeBase,
  getDocumentListFromKnowledgeBase,
  deleteDocumentFromKnowledgeBase,
  uploadDocumentToKnowledgeBase,
  getKnowledgeBaseById
} from '@/api/knowledgeBase'
import { getFilesByUserId } from '@/api/file'

const router = useRouter()
const activeTab = ref('basic')

// 知识库基本信息
const kbInfo = ref({
  id: null,
  kb_name: '',
  description: '',
  img: ''
})

// 文档列表
const documents = ref([])
// 用户文档列表
const userDocuments = ref([])
// 选中的文档
const selectedDocuments = ref([])
// 上传对话框可见性
const uploadDialogVisible = ref(false)

// 获取知识库信息
const fetchKnowledgeBaseInfo = async () => {
  try {
    const kb= await getKnowledgeBaseById(useRouter().currentRoute.value.params.id)
    if (kb) {
      kbInfo.value = kb.data[0]
      // 获取文档列表
      await fetchDocuments()
    }
  } catch (error) {
    ElMessage.error('获取知识库信息失败')
  }
}

// 获取文档列表
const fetchDocuments = async () => {
  try {
    const response = await getDocumentListFromKnowledgeBase(kbInfo.value.id)
    documents.value = response.data
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  }
}

// 获取用户文档列表
const fetchUserDocuments = async () => {
  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo'))
    const response = await getFilesByUserId(userInfo.id)
    userDocuments.value = response.data
  } catch (error) {
    ElMessage.error('获取用户文档列表失败')
  }
}

// 显示上传对话框
const showUploadDialog = async () => {
  await fetchUserDocuments()
  uploadDialogVisible.value = true
}

// 处理文档选择变化
const handleSelectionChange = (selection) => {
  selectedDocuments.value = selection
}

// 处理添加文档
const handleAddDocuments = async () => {
  try {
    for (const doc of selectedDocuments.value) {
      await uploadDocumentToKnowledgeBase({
        kb_id: kbInfo.value.id,
        doc_id: doc.id
      })
    }
    ElMessage.success('添加成功')
    uploadDialogVisible.value = false
    await fetchDocuments() // 刷新文档列表
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 保存基本信息
const saveBasicInfo = async () => {
  try {
    await updateKnowledgeBase(kbInfo.value)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 处理图片上传
const handleImageChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    kbInfo.value.img = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

// 预览文档
const previewDocument = (doc) => {
  window.open(doc.url, '_blank')
}

// 删除文档
const deleteDocument = async (doc) => {
  console.log(kbInfo.value.id)
  console.log(doc)
  try {
    await deleteDocumentFromKnowledgeBase({
      kb_id: kbInfo.value.id,
      doc_id: doc.id
    })
    ElMessage.success('删除成功')
    await fetchDocuments() // 刷新文档列表
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchKnowledgeBaseInfo()
})
</script>

<style scoped>
.page-content {
  padding: 24px;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #666;
  margin-right: 24px;
}

.back-button:hover {
  color: #409eff;
}

.settings-tabs {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 24px 0;
}

.doc-header {
  margin-bottom: 24px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
  object-fit: cover;
}
</style>
