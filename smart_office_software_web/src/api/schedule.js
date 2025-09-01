import request from '@/utils/request'

export function getScheduleByUserId(userId) {
    return request({
        url: `/scheduled/list/${userId}`,
        method: 'get',
    })
}
export function addSchedule(data) {
    return request({
        url: '/scheduled/add',
        method: 'post',
        data: data,
    })
}
export function cancelScheduleById(id) {
    return request({
        url: `/scheduled/cancel/by/${id}`,
        method: 'delete',
    })
}
export function cancelScheduleByTaskId(taskId) {
    return request({
        url: `/scheduled/cancel/${taskId}`,
        method: 'delete',
    })
}
export function updateSchedule(data) {
    return request({
        url: '/scheduled/update',
        method: 'put',
        data: data,
    })
}
export function getScheduleBydate(userId, date) {
    return request({
        url: '/scheduled/list/date',
        method: 'get',
        params: {
            userId,
            date
        }
    })
}