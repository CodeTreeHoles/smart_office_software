import {aiRequest} from '@/utils/request'
export function chat(data){
  return aiRequest({
    url:  `/chat`,
    method: 'post',
    data
  })
}
// 加载聊天附件
// 加载聊天附件 - 修改后的版本
export function loadChatAttachedFile(formData) {
  return aiRequest({
    url: `/chat/attached`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

export function deleteChatAttachedFile(data){
  return aiRequest({
    url:  `/chat/attached`,
    method: 'delete',
    data //通过doc_id字段删除
  })
}
