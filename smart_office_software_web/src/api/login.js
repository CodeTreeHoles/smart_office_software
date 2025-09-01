import request from '@/utils/request'

// Login API
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

// Logout API
export function logout() {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: '/auth/logout',
    method: 'post'
  })
}

// Get user info API
export function getUserInfo() {
  return request({
    url: '/auth/user-info',
    method: 'get'
  })
}

// 修改用户信息 API
export function updateUser(id, data) {
  return request({
    url: `/user/${id}`,
    method: 'put',
    data
  })
} 