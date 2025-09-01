<template>
  <div class="page-content">
    <div class="header-actions">
      <h1>知识库管理</h1>
      <el-button type="primary" @click="showAddModal">
        <i class="fas fa-plus"></i> 添加
      </el-button>
    </div>
    <div class="kb-list">
      <div v-for="kb in knowledgeBases" :key="kb.id" class="kb-card">
        <img :src="kb.img || 'https://rag-temp.oss-cn-hangzhou.aliyuncs.com/%E4%BC%98%E5%8C%96%E7%A4%BA%E6%84%8F%E5%9B%BE%20%281%29.png'" class="kb-icon" />
        <div class="kb-info">
          <h3 class="kb-name">{{ kb.kb_name }}</h3>
          <p class="kb-desc">{{ kb.description }}</p>
          <div class="kb-meta">
            <span class="kb-date">创建时间: {{ formatDate(kb.created_at) }}</span>
            <span class="kb-date">更新时间: {{ formatDate(kb.updated_at) }}</span>
          </div>
          <div class="kb-actions">
            <el-button type="primary" link @click="openKnowledgeBase(kb)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个知识库吗?"
              @confirm="handleDelete(kb)"
              confirm-button-text="确定"
              cancel-button-text="取消"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑知识库的模态框 -->
    <el-dialog
      v-model="modalVisible"
      :title="modalMode === 'add' ? '新建知识库' : '编辑知识库'"
      width="500px"
    >
      <el-form :model="formState" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="formState.kb_name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="图标">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleImageChange"
          >
            <img v-if="formState.img" :src="formState.img" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formState.description"
            type="textarea"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleModalCancel">取消</el-button>
          <el-button type="primary" @click="handleModalOk">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { createKnowledgeBase, updateKnowledgeBase, deleteKnowledgeBase,getKnowledgeBaseListByUserId,getPublicKnowledgeBase } from '@/api/knowledgeBase'
import { useRouter } from 'vue-router'
import {verificationRole} from '@/api/verification'

const knowledgeBases = ref([])
const modalVisible = ref(false)
const modalMode = ref('add') // 'add' 或 'edit'
const formState = reactive({
  id: null,
  kb_name: '',
  description: '',
  img: '',
  dept_id: null
})
const router = useRouter()

// 处理图片上传
const handleImageChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    formState.img = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

// 获取知识库列表
const fetchKnowledgeBases = async () => {
  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo'))
    const userId = userInfo.id
    const response = await getKnowledgeBaseListByUserId(userId)
    knowledgeBases.value = response.data
    const res2 = await verificationRole(userInfo)
    const code = res2.data.data
    if(code != null){
      const kb = await (await getPublicKnowledgeBase(code)).data
      knowledgeBases.value.push(kb)
    }

  } catch (error) {
    console.error('获取知识库列表失败:', error)
    ElMessage.error('获取知识库列表失败')
  }
}

// 打开知识库详情
const openKnowledgeBase = (kb) => {
  router.push(`/smart-assistant/knowledge-base/${kb.id}`)
}

// 显示添加模态框
const showAddModal = () => {
  modalMode.value = 'add'
  formState.id = null
  formState.kb_name = ''
  formState.description = ''
  formState.img = ''
  modalVisible.value = true
}

// 显示编辑模态框
const showEditModal = (kb) => {
  modalMode.value = 'edit'
  formState.id = kb.id
  formState.kb_name = kb.kb_name
  formState.description = kb.description
  formState.img = kb.img
  modalVisible.value = true
}

// 处理模态框确认
const handleModalOk = async () => {
  try {
    if (modalMode.value === 'add') {
      const dept_id = JSON.parse(localStorage.getItem('departmentId'))
      formState.dept_id = dept_id
      await createKnowledgeBase(formState)
      ElMessage.success('创建成功')
    } else {
      await updateKnowledgeBase(formState)
      ElMessage.success('更新成功')
    }
    modalVisible.value = false
    fetchKnowledgeBases()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

// 处理模态框取消
const handleModalCancel = () => {
  modalVisible.value = false
}

// 处理删除
const handleDelete = async (kb) => {
  try {
    console.log(kb.id)
    const data = await deleteKnowledgeBase({ kb_id: kb.id })
    console.log(data.data);
    
    ElMessage.success(data.data.message)
    fetchKnowledgeBases()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
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

onMounted(() => {
  fetchKnowledgeBases()
})
</script>

<style scoped>
.page-content {
  width: 98%;
  padding: 1%;
}

.header-actions {
  margin-bottom: 24px;
}

.kb-list {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.kb-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  width: 300px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kb-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.kb-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
}

.kb-info {
  width: 100%;
}

.kb-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
  color: #333;
}

.kb-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.kb-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.kb-date {
  font-size: 12px;
  color: #999;
}

.kb-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid #eee;
  padding-top: 12px;
  margin-top: 12px;
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
