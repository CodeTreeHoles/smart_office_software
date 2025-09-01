import request from '@/utils/request'

export function verificationRole(data){
    return request({
        url: '/user/verification/role',
        method: 'post',
        data
    })
}