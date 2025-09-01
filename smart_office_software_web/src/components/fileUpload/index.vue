<template>
  <div>
    <button class="upload-btn" @click="show = true">上传文件</button>
    <div v-if="show" class="modal-mask">
      <div class="modal-container">
        <div class="modal-header">
          <span>上传文件</span>
          <span class="modal-close" @click="close">&times;</span>
        </div>
        <div
          class="drop-area"
          @dragover.prevent
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input type="file" ref="fileInput" style="display:none" @change="handleFileChange" />
          <div v-if="!fileName">点击或拖拽文件到此处上传</div>
          <div v-else>已选择：{{ fileName }}</div>
        </div>
        <div class="modal-form">
          <input v-model="form.fileName" placeholder="文件名称" class="input" />
          <select v-model="form.scope" class="input">
            <option :value="0">个人</option>
            <option :value="1">团队</option>
          </select>
          <input v-if="form.scope == 1" v-model="form.teamId" placeholder="团队编号" class="input" />
          <input v-model="form.desc" placeholder="文件描述(可选)" class="input" />
        </div>
        <div class="modal-footer">
          <button class="modal-btn" @click="submit">确定</button>
          <button class="modal-btn cancel" @click="close">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { uploadFile , getFilesByUserId } from '@/api/file'
// 新增一个事件用于通知父组件刷新
const emit = defineEmits(['uploaded'])

const show = ref(false)
const fileInput = ref(null)
const fileName = ref('')
const file = ref(null)
const form = reactive({
  fileName: '',
  scope: 0,
  desc: '',
  teamId: null
})

onMounted(async () => {
  try {
    const res = await getFilesByUserId(1)
    console.log('getFilesByUserId(1) 返回:', res)
  } catch (err) {
    console.error('获取文件列表失败:', err)
  }
})

function triggerFileInput() {
  fileInput.value.click()
}

function handleFileChange(e) {
  const f = e.target.files[0]
  if (f) {
    file.value = f
    fileName.value = f.name
    form.fileName = f.name
  }
}

function handleDrop(e) {
  const f = e.dataTransfer.files[0]
  if (f) {
    file.value = f
    fileName.value = f.name
    form.fileName = f.name
  }
}

function close() {
  show.value = false
  file.value = null
  fileName.value = ''
  form.fileName = ''
  form.desc = ''
  form.teamId = ''
}

async function submit() {
  if (!file.value) {
    alert('请选择文件')
    return
  }
  if (!form.fileName) {
    alert('请填写文件名称')
    return
  }
  if (form.scope == 1 && !form.teamId) {
    alert('请填写团队编号')
    return
  }
  const userInfo = JSON.parse(localStorage.getItem('userInfo'))
  const userId = userInfo && userInfo.id ? userInfo.id : ''
  if (!userId) {
    alert('未获取到当前用户ID')
    return
  }
  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('fileName', form.fileName)
  formData.append('userId', userId)
  formData.append('scope', form.scope)
  formData.append('desc', form.desc)
  if (form.scope == 1) {
    formData.append('teamId', form.teamId)
  }
  try {
    const res = await uploadFile(formData)
    alert('上传成功！')
    emit('uploaded') // 通知父组件刷新
    close()
  } catch (err) {
    alert('上传失败！')
    console.error(err)
  }
}
</script>

<style scoped>
.upload-btn {
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 20px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s;
}
.upload-btn:hover {
  background: #1890ff;
}
.modal-mask {
  position: fixed;
  z-index: 9999;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-container {
  background: #fff;
  border-radius: 8px;
  width: 400px;
  max-width: 90vw;
  padding: 24px 24px 16px 24px;
  box-shadow: 0 4px 32px rgba(0,0,0,0.12);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}
.modal-close {
  font-size: 22px;
  color: #888;
  cursor: pointer;
}
.drop-area {
  border: 2px dashed #1890ff;
  border-radius: 6px;
  padding: 24px;
  text-align: center;
  color: #888;
  margin-bottom: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}
.drop-area:hover {
  border-color: #1890ff;
}
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.input, select {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 14px;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
.modal-btn {
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 6px 18px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s;
}
.modal-btn.cancel {
  background: #eee;
  color: #333;
}
.modal-btn:hover:not(.cancel) {
  background: #1890ff;
}
</style> 