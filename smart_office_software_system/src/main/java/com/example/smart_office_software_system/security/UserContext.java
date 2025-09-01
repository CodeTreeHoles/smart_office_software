package com.example.smart_office_software_system.security;

import com.example.smart_office_software_system.domain.User;

/**
* @program: smart_office_software_system
*
* @description:
*
* @author: 黄胜
*
* @create: 2025-08-15 07:33
**/


import com.example.smart_office_software_system.domain.User;

/** 保存当前请求用户的上下文信息 */
public class UserContext {
    private static final ThreadLocal<LoginUser> TL = new ThreadLocal<>();
    public static void set(LoginUser u) { TL.set(u); }
    public static LoginUser get() { return TL.get(); }
    public static void clear() { TL.remove(); }
}
