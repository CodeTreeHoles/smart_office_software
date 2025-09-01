import request from '@/utils/request'

export function getDepartmentList() {
  return request({
    // headers: {
    //   Authorization: "Bearer " + localStorage.getItem("token")
    // },
    url: `/document/list`,
    method: 'get'
  })
}

// 根据部门id查询部门详情
export function getDepartmentDetail(deptId) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/${deptId}`,
    method: 'get'
  })
}

// 根据用户id查询对应部门
export function getDepartmentByUserId(userId) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/fromUser/${userId}`,
    method: 'get'
  })
}
// 新增成员
export function addTeamUser(deptId, data) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/${deptId}/user`,
    method: 'post',
    data
  })
}
// 修改成员
export function updateTeamUser(deptId, userId, data) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/${deptId}/user/${userId}`,
    method: 'put',
    data
  })
}
// 删除成员
export function deleteTeamUser(deptId, userId) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/${deptId}/user/${userId}`,
    method: 'delete'
  })
}
// 删除部门
export function deleteDepartment(deptId) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/${deptId}`,
    method: 'delete'
  })
}

// 更新部门
export function updateDepartment(department) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/update`,
    method: 'put',
    data: department
  })
}

// 新增部门
export function addDepartment(department) {
  return request({
    headers: {
      Authorization: "Bearer " + localStorage.getItem("token")
    },
    url: `/document/add`,
    method: 'post',
    data: department
  })
}