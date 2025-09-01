<template>
  <div class="page-content">
    <div class="chat-sidebar">
      <div class="chat-history">
        <div class="history-header">
          <span>对话记录</span>
          <el-button type="primary" link @click="handleCreateNewChat">
            <i class="fas fa-plus"></i> 新建会话
          </el-button>
        </div>
        <div class="history-list">
          <div v-for="(chat, index) in chatHistory" 
            :key="index"
            :class="['history-item', { active: currentChatId === chat.id }]"
            @click="switchChat(chat.id)">
            <div class="history-title" v-if="!chat.isEditing">{{ chat.name }}</div>
            <el-input v-else
              v-model="chat.name"
              size="small"
              @blur="handleRename(chat)"
              @keyup.enter="handleRename(chat)"
            />
            <div class="history-meta">
              <div class="history-time">{{ chat.time }}</div>
              <el-dropdown trigger="click">
                <i class="fas fa-ellipsis-v"></i>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="startRename(chat)">
                      <i class="fas fa-edit"></i> 重命名
                    </el-dropdown-item>
                    <el-dropdown-item @click="deleteChat(chat.id)">
                      <i class="fas fa-trash"></i> 删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-main">
      <div class="chat-header">
        <h2>智能对话</h2>
        <div class="knowledge-base-list">
          <span class="label">选择知识库:</span>
          <el-select
            v-model="selectedKnowledgeBase"
            placeholder="请选择知识库"
            style="width: 200px"
            @change="handleKnowledgeBaseChange"
            multiple
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.kb_name"
              :value="kb.id"
            />
          </el-select>
        </div>
      </div>
      <div class="chat-container">
        <div class="chat-messages" v-loading="isSending" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <i class="fas fa-robot empty-icon"></i>
            <div class="empty-text">Hi，我是您的智能助手</div>
            <div class="empty-desc">请选择知识库开始对话</div>
          </div>
          <div v-else class="message-list">
            <div v-for="(msg, index) in messages" :key="index">
              <div
                v-if="msg.role === 'system'"
                class="message-system"
                v-html="formatMessage(msg.content)"
              ></div>
              <div
                v-else
                :class="['message-item', msg.role === 'user' ? 'user-message' : 'assistant-message']"
              >
                <div class="avatar">
                  <i :class="msg.role === 'user' ? 'fas fa-user' : 'fas fa-robot'"></i>
                </div>
                <!-- 修正 message-content 的布局影响：限制最大宽度，防止撑开父容器 -->
                <div class="message-content" v-html="formatMessage(msg.content)"></div>
              </div>
            </div>
          </div>
        </div>
        <!-- 单独的文件上传功能区域 -->
        <div class="chat-upload">
          <div class="upload-header">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleFileUpload"
              :before-upload="() => !isUploading"
            >
              <el-button class="icon-btn" :disabled="isUploading">
                <i class="fas fa-upload"></i> 上传文件
              </el-button>
            </el-upload>
          </div>
          <div class="upload-list" v-if="fileList.length > 0">
            <div v-for="file in fileList" :key="file.doc_id" class="upload-item">
              <span class="file-name">{{ file.name }}</span>
              <i class="fas fa-times" @click="handleFileDelete(file)"></i>
            </div>
          </div>
        </div>
        <!-- 聊天输入区域 -->
        <div class="chat-input">
          <div class="input-bar">
            <textarea
              v-model="inputMessage"
              class="input-textarea"
              placeholder="请输入您的问题..."
              :rows="1"
              @keydown="handleInputKeydown"
              :disabled="isSending"
              ref="autoTextarea"
              style="resize: none; max-height: 120px; overflow-y: auto;"
            ></textarea>
            <div class="input-actions-right">
              <button class="send-btn" @click="handleSend" :disabled="!inputMessage || isSending">
                <i class="fas fa-arrow-up"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getKnowledgeBaseListByUserId } from '@/api/knowledgeBase'
import { marked } from 'marked'
import { createSession, getSessionList, getSessionRecord, deleteSession, updateSession, uploadSessionRecord } from '@/api/session'
import { chat, loadChatAttachedFile, deleteChatAttachedFile } from '@/api/chat'

const selectedKnowledgeBase = ref([])
const temp_file_list = ref([]) // 仍然用于发送时传递
const knowledgeBases = ref([])
const messages = ref([])
const inputMessage = ref('')
const messagesContainer = ref(null)
const currentChatId = ref(null)
const chatHistory = ref([])
const isSending = ref(false)
const isUploading = ref(false)
const fileList = ref([])
const autoTextarea = ref(null)
const userInfo = ref(null)

const fetchChatHistory = async () => {
  try {
    const response = await getSessionList(userInfo.value.id)
    chatHistory.value = response.data.map(chat => ({
      ...chat,
      isPinned: false,
      isEditing: false
    }))
    if (chatHistory.value.length > 0) {
      currentChatId.value = chatHistory.value[chatHistory.value.length - 1].id
      await fetchChatMessages(currentChatId.value)
    } else {
      currentChatId.value = null
      messages.value = []
    }
  } catch (error) {
    ElMessage.error('获取会话列表失败')
  }
}

const fetchChatMessages = async (sessionId) => {
  try {
    const response = await getSessionRecord(sessionId)
    messages.value = response.data
  } catch (error) {
    ElMessage.error('获取会话记录失败')
  }
}

const fetchKnowledgeBases = async () => {
  try {
    const response = await getKnowledgeBaseListByUserId(userInfo.value.id)
    knowledgeBases.value = response.data
  } catch (error) {
    ElMessage.error('获取知识库列表失败')
  }
}

const handleKnowledgeBaseChange = (value) => {
  selectedKnowledgeBase.value = value
}

const formatMessage = (content) => {
  return marked.parse(content || '')
}

// 文件上传后页面聊天模块重新加载，因为每次上传文件之后都会在聊天记录当中添加记录。
const handleFileUpload = async (file) => {
  try {
    isUploading.value = true
    const actualFile = file.raw
    const formData = new FormData()
    formData.append('file', actualFile)
    formData.append('session_id', currentChatId.value)
    // 上传文件
    const response = await loadChatAttachedFile(formData)
    // 只在本地维护 fileList 和 temp_file_list
    temp_file_list.value.push(response.data.doc_id)
    fileList.value.push({
      name: actualFile.name,
      doc_id: response.data.doc_id
    })
    ElMessage.success('文件上传成功')
    // 上传后重新加载聊天记录
    if (currentChatId.value) {
      await fetchChatMessages(currentChatId.value)
    }
  } catch (error) {
    ElMessage.error('文件上传失败')
  } finally {
    isUploading.value = false
  }
}

const handleFileDelete = async (file) => {
  try {
    await deleteChatAttachedFile({ doc_id: file.doc_id, session_id: currentChatId.value })
    temp_file_list.value = temp_file_list.value.filter(id => id !== file.doc_id)
    fileList.value = fileList.value.filter(f => f.doc_id !== file.doc_id)
    ElMessage.success('文件删除成功')
    if (currentChatId.value) {
      await fetchChatMessages(currentChatId.value)
    }
  } catch (error) {
    ElMessage.error('文件删除失败')
  }
}

// 发送后清空上传文件列表
const cleanupTempFiles = async () => {
  temp_file_list.value = []
  fileList.value = []
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || isSending.value) return
  isSending.value = true
  const userMessage = {
    role: 'user',
    content: inputMessage.value
  }
  messages.value.push(userMessage)
  try {
    if(currentChatId.value == null){
      currentChatId.value = chatHistory.value[chatHistory.value.length - 1]?.id
    }
    const response = await chat({
      input: inputMessage.value,
      session_id: currentChatId.value,
      user_info: userInfo.value,
      kb_id: selectedKnowledgeBase.value,
      temp_file_list: temp_file_list.value
    })
    const assistantMessage = {
      role: 'assistant',
      content: response.data.output
    }
    messages.value.push(assistantMessage)
    await uploadSessionRecord(currentChatId.value, {
      session_id: currentChatId.value,
      role: 'user',
      content: inputMessage.value
    })
    await uploadSessionRecord(currentChatId.value, {
      session_id: currentChatId.value,
      role: 'assistant',
      content: response.data.output
    })
    await cleanupTempFiles()
  } catch (error) {
    ElMessage.error('发送消息失败')
  } finally {
    isSending.value = false
    inputMessage.value = ''
  }
}

const switchChat = async (chatId) => {
  currentChatId.value = chatId
  await fetchChatMessages(chatId)
  // 切换会话时清空上传文件列表
  temp_file_list.value = []
  fileList.value = []
}

const handleCreateNewChat = async () => {
  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo'))
    const response = await createSession({
      session_name: '新会话',
      user_id: userInfo.id
    })
    const newChat = response.data
    chatHistory.value.unshift({
      ...newChat,
      isPinned: false,
      isEditing: false
    })
    currentChatId.value = newChat.id
    messages.value = []
    await fetchChatHistory()
    // 新建会话时清空上传文件列表
    temp_file_list.value = []
    fileList.value = []
  } catch (error) {
    ElMessage.error('创建会话失败')
  }
}

const pinChat = (chatId) => {
  const chat = chatHistory.value.find(c => c.id === chatId)
  if (chat) {
    chat.isPinned = !chat.isPinned
    chatHistory.value.sort((a, b) => {
      if (a.isPinned === b.isPinned) {
        return 0
      }
      return a.isPinned ? -1 : 1
    })
  }
}

const startRename = (chat) => {
  chat.isEditing = true
}

const handleRename = async (chat) => {
  try {
    await updateSession({
      session_id: chat.id,
      name: chat.name
    })
    chat.isEditing = false
    await fetchChatHistory()
    ElMessage.success('重命名成功')
  } catch (error) {
    ElMessage.error('重命名失败')
  }
}

const deleteChat = async (sessionId) => {
  try {
    await deleteSession(sessionId)
    await fetchChatHistory()
    if (currentChatId.value === sessionId) {
      if (chatHistory.value.length > 0) {
        currentChatId.value = chatHistory.value[chatHistory.value.length - 1]?.id
        await fetchChatMessages(currentChatId.value)
      } else {
        currentChatId.value = null
        messages.value = []
      }
    }
    ElMessage.success('删除成功')
    // 删除会话时清空上传文件列表
    temp_file_list.value = []
    fileList.value = []
  } catch (error) {
    ElMessage.error('删除会话失败')
  }
}

const adjustTextareaHeight = () => {
  const el = autoTextarea.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 24 * 5) + 'px'
  }
}

const handleInputKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  } else {
    nextTick(() => adjustTextareaHeight())
  }
}

watch(inputMessage, () => {
  nextTick(() => adjustTextareaHeight())
})

onMounted(() => {
  userInfo.value = JSON.parse(localStorage.getItem('userInfo'))
  fetchKnowledgeBases()
  fetchChatHistory()
})
</script>

<style lang="scss" scoped>
.page-content {
  width: 98%;
  height: 97%;
  display: flex;
  padding: 1%;
  background: #f7f9fb;
  overflow: hidden;
  gap: 16px;

  .chat-sidebar {
    width: 240px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    
    .chat-history {
      .history-header {
        padding: 16px;
        font-size: 16px;
        font-weight: 500;
        color: #1f2937;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .history-list {
        padding: 8px;
        height: calc(80vh - 120px);
        overflow-y: auto;
        
        .history-item {
          padding: 12px;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
          
          &:hover {
            background: #f3f4f6;
          }
          
          &.active {
            background: #e5e7eb;
          }
          
          .history-title {
            font-size: 14px;
            color: #1f2937;
            margin-bottom: 4px;
          }
          
          .history-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .history-time {
              font-size: 12px;
              color: #9ca3af;
            }
            
            .fa-ellipsis-v {
              color: #9ca3af;
              cursor: pointer;
              padding: 4px;
              
              &:hover {
                color: #4b5563;
              }
            }
          }
        }
      }
    }
  }

  .chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;

    .chat-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;

      h2 {
        margin: 0;
        font-size: 20px;
        color: #1f2937;
      }

      .knowledge-base-list {
        display: flex;
        align-items: center;
        gap: 8px;

        .label {
          color: #4b5563;
          font-size: 14px;
        }
      }
    }

    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      max-height: 80vh;
      
      .chat-messages {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        max-height: calc(100vh - 10em);

        .message-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
          height: 100%;
          overflow-y: auto;
        }

        .message-item {
          display: flex;
          gap: 12px;
          justify-content: flex-start;

          .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            
            i {
              font-size: 16px;
              color: #fff;
            }
          }

          .message-content {
            /* 修正：限制最大宽度，防止撑开父容器 */
            max-width: 50vw;
            min-width: 0;
            word-break: break-word;
            box-sizing: border-box;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.5;
            overflow-x: auto;
            overflow-y: visible;
            background: transparent;

            :deep(p) {
              margin: 0 0 8px 0;
            }

            :deep(ul), :deep(ol) {
              margin: 8px 0;
              padding-left: 20px;
            }

            :deep(pre) {
              background: #f6f8fa;
              border-radius: 4px;
              padding: 8px 12px;
              font-size: 13px;
              overflow-x: auto;
              margin: 8px 0;
            }

            :deep(code) {
              background: #f6f8fa;
              border-radius: 3px;
              padding: 2px 4px;
              font-size: 13px;
              color: #c7254e;
            }

            :deep(blockquote) {
              border-left: 4px solid #d0d7de;
              background: #f6f8fa;
              margin: 8px 0;
              padding: 8px 12px;
              color: #6a737d;
            }

            :deep(a) {
              color: #1890ff;
              text-decoration: underline;
              word-break: break-all;
            }

            :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
              margin: 8px 0 4px 0;
              font-weight: bold;
            }

            :deep(table) {
              border-collapse: collapse;
              margin: 8px 0;
              width: 100%;
            }
            :deep(th), :deep(td) {
              border: 1px solid #e5e7eb;
              padding: 4px 8px;
            }
          }

          &.user-message {
            align-self: flex-end;
            margin-right: 0;
            flex-direction: row-reverse;
            
            .avatar {
              background: #1890ff;
            }
            
            .message-content {
              background: #1890ff;
              color: #fff;
            }
          }

          &.assistant-message {
            align-self: flex-start;
            justify-content: flex-start;
            flex-direction: row;
            
            .avatar {
              background: #52c41a;
            }
            
            .message-content {
              background: #f3f4f6;
              color: #1f2937;
            }
          }
        }
      }

      .chat-upload {
        border-top: 1px solid #e5e7eb;
        background: #f9fafb;
        border-radius: 0 0 8px 8px;
        padding: 0.5em 0.8em 0.5em 0.8em;
        .upload-header {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 15px;
          font-weight: 500;
          color: #4b5563;
          margin-bottom: 6px;
        }
        .upload-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          padding: 8px 0 4px 0;
          border-bottom: 1px solid #e5e7eb;
          margin-bottom: 8px;
        }
        .upload-item {
          display: flex;
          align-items: center;
          background: #f3f4f6;
          border-radius: 4px;
          padding: 2px 8px;
          font-size: 13px;
          color: #333;
          .file-name {
            margin-right: 6px;
          }
          .fa-times {
            color: #b91c1c;
            cursor: pointer;
            margin-left: 2px;
            &:hover {
              color: #ef4444;
            }
          }
        }
      }

      .chat-input {
        border-top: 1px solid #e5e7eb;
        background: #fff;
        border-radius: 0 0 8px 8px;
        padding: 0.5em 0.8em 0.7em 0.8em;
        .input-bar {
          display: flex;
          align-items: center;
          gap: 10px;
          width: 100%;
          background: #f7f9fb;
          border-radius: 24px;
          padding: 0.2em 0.6em;
          box-sizing: border-box;
        }
        .input-actions-right {
          display: flex;
          align-items: center;
          margin-left: 4px;
        }
        .icon-btn {
          background: none;
          border: none;
          box-shadow: none;
          padding: 0 6px;
          min-width: 0;
          height: 32px;
          display: flex;
          align-items: center;
          font-size: 15px;
          color: #666;
          border-radius: 6px;
          transition: background 0.2s;
          &:hover:not(:disabled) {
            background: #e5e7eb;
            color: #1890ff;
          }
        }
        .input-textarea {
          flex: 1;
          border: none;
          background: transparent;
          resize: none;
          font-size: 1.1em;
          padding: 0.6em 0.2em;
          margin: 0 2px;
          outline: none;
          min-height: 24px;
          max-height: 120px;
          line-height: 1.5;
          color: #222;
        }
        .send-btn {
          background: #1890ff;
          color: #fff;
          border: none;
          border-radius: 50%;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          margin-left: 2px;
          transition: background 0.2s;
          &:hover:not(:disabled) {
            background: #40a9ff;
          }
          &:disabled {
            background: #d9d9d9;
            color: #fff;
            cursor: not-allowed;
          }
        }
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
    color: #1890ff;
  }
  
  .empty-text {
    color: #4b5563;
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 6px;
  }

  .empty-desc {
    color: #9ca3af;
    font-size: 14px;
  }
}

.loading-message {
  .loading-dots {
    display: flex;
    gap: 4px;
    padding: 8px 0;
    
    span {
      width: 8px;
      height: 8px;
      background: #1890ff;
      border-radius: 50%;
      animation: loading 1.4s infinite ease-in-out both;
      
      &:nth-child(1) {
        animation-delay: -0.32s;
      }
      
      &:nth-child(2) {
        animation-delay: -0.16s;
      }
    }
  }
}

@keyframes loading {
  0%, 80%, 100% { 
    transform: scale(0);
  } 
  40% { 
    transform: scale(1.0);
  }
}

.chat-messages {
  height: calc(100vh - 300px);
  overflow-y: auto;
  padding: 20px;
  position: relative;
  
  :deep(.ant-spin-nested-loading) {
    height: 100%;
  }
  
  :deep(.ant-spin-container) {
    height: 100%;
  }
}

.message-item {
  &.assistant-message {
    .message-content {
      :deep(.el-skeleton) {
        padding: 8px;
        .el-skeleton__item {
          height: 20px;
        }
      }
    }
  }
}

.message-system {
  text-align: center;
  color: #b0b0b0;
  font-size: 12px;
  font-style: italic;
  margin: 12px 0;
  line-height: 1.6;
}
</style>
