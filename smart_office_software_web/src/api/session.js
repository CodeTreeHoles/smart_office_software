import {aiRequest} from '@/utils/request'
export function getSessionList(userId){
  return aiRequest({
    url:  `/session/list/${userId} `,
    method: 'get'
  })
}
export function createSession(data){
  return aiRequest({
    url: '/session',
    method: 'post',
    data
  })
}
export function updateSession(data){
    // 重命名
  return aiRequest({
    url: '/session',
    method: 'put',
    data
  })
}
export function deleteSession(sessionId){
  return aiRequest({
    url: `/session/${sessionId}`,
    method: 'delete',
  })
}
export function getSession(data){
    // 提供session_id即可,获取某个会话的指定信息
  return aiRequest({
    url: `/session`,
    method: 'get',
    data
  })
}
export function getSessionRecord(sessionId){
    return aiRequest({
        url: `/session/record/${sessionId}`,
        method: 'get',
    })
}
export function uploadSessionRecord(sessionId,data){
  return aiRequest({
    url: `/session/record/${sessionId}`,
    method: 'post',
    data
  })
}
