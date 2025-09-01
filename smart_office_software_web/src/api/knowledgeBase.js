import {aiRequest} from '@/utils/request'
export function getKnowledgeBaseById(id) {
  return aiRequest({
    url: '/knowledge_base',
    method:"get",
    params: { kb_id: id }
  })
}

export const getKnowledgeBaseListByUserId = (userId) => {
  return aiRequest({
    url: '/knowledge_base/dept_id/list',
    method: 'get',
    params: { user_id: userId }
  })
}
export function createKnowledgeBase(data){
  return aiRequest({
    url: '/knowledge_base',
    method: 'post',
    data
  })
}
export function updateKnowledgeBase(data){
  return aiRequest({
    url: '/knowledge_base',
    method: 'put',
    data
  })
}
export function deleteKnowledgeBase(data){
  return aiRequest({
    url: `/knowledge_base`,
    method: 'delete',
    data
  })
}
// 获取知识库文档列表
export function getDocumentListFromKnowledgeBase(kbId){
  return aiRequest({
    url: `/knowledge_base/doc`,
    method: 'get',
    params: { kb_id: kbId }  // 使用 params 而非 data
  })
}
// 删除知识库文档
export function deleteDocumentFromKnowledgeBase(data){
  return aiRequest({
    url: `/knowledge_base/doc`,
    method: 'delete',
    data
  })
}
// 上传知识库文档
export function uploadDocumentToKnowledgeBase(data){
  return aiRequest({
    url: `/knowledge_base/doc`,
    method: 'post',
    data
  })
}

export function getPublicKnowledgeBase(code){
  return aiRequest({
    url: `/knowledge_base/public`,
    method: 'get',
    params: { code:code }
  })
}