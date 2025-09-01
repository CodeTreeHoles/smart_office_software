import request from '@/utils/request'

// 文件上传API
export function uploadFile(formData) {
  return request({
    url: '/file/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      Authorization: "Bearer " + localStorage.getItem("token")
    }
  })
}

//根据用户id获取文件列表
export function getFilesByUserId(userId) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url : `/file/getFile/user/${userId}`,
    method: 'get'
  })
}

export function deleteFile(fileId){
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url : `/file/delete/${fileId}`,
    method: 'delete'
  })
}