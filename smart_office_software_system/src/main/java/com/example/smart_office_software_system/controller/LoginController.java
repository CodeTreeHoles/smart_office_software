package com.example.smart_office_software_system.controller;

import com.example.smart_office_software_system.domain.User;
import com.example.smart_office_software_system.dto.LoginReq;
import com.example.smart_office_software_system.pojo.Result;
import com.example.smart_office_software_system.service.AuthService;
import com.example.smart_office_software_system.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletResponse;
import javax.validation.Valid;


import java.util.HashMap;
import java.util.Map;

import static com.example.smart_office_software_system.pojo.Result.error;
import static com.example.smart_office_software_system.pojo.Result.success;

/**
 * @program: smart_office_software_system
 * @description: 登录、注册控制类
 * @create: 2025-05-29 14:15
 **/

/**
 * 登录、登出控制器
 */
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class LoginController {

    private final AuthService authService;

    @Autowired
    private UserService userService;

    /**
     * 登录：成功返回 token（前端存起来，每次请求放到 Authorization: Bearer <token>）
     */
    @PostMapping("/login")
    public Result<?> login(@Valid @RequestBody LoginReq req , HttpServletResponse resp) {
        try {
            String token = authService.login(req.getAccount(), req.getPassword());

            Cookie c = new Cookie("LOGIN_TOKEN", token);
            c.setPath("/");                    // 整站有效
            c.setHttpOnly(true);               // 防 XSS
            c.setMaxAge(7 * 24 * 60 * 60); // 7天


            User u = userService.findByAccount(req.getAccount()); // 你已有的方法
            String account = u.getAccount();
            int role = (u.getRole() == null) ? 1 : u.getRole();
            int id = u.getId();
            Map<String, Object> obj = new HashMap<>();
            obj.put("id", id);
            obj.put("token", token);
            obj.put("account", account);
            obj.put("password",req.getPassword());
            obj.put("role", role);
            obj.put("email", u.getEmail());

            resp.addCookie(c);

            return success(obj);

        } catch (RuntimeException e) {
            return error(e.getMessage());
        }
    }


    /**
     * 登出：删除 Redis 中的 token
     */
    @PostMapping("/logout")
    public Result<?> logout(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            @org.springframework.web.bind.annotation.CookieValue(value = "LOGIN_TOKEN", required = false) String cookieToken,
            javax.servlet.http.HttpServletResponse response) {

        // ① 提取 token（优先 Header，其次 Cookie）
        String token = null;
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            token = authHeader.substring(7).trim();
        }
        if (token == null && cookieToken != null && !cookieToken.trim().isEmpty()) {
            token = cookieToken.trim();
        }

        // ② 删 Redis
        if (token != null) {
            authService.logout(token);
        }

        // ③ 覆盖删除浏览器 Cookie（name/path/domain 必须一致）
        javax.servlet.http.Cookie c = new javax.servlet.http.Cookie("LOGIN_TOKEN", "");
        c.setPath("/");
        c.setHttpOnly(true);
        c.setMaxAge(0);  // 立即过期
        // 如果你登录时设置了 domain/secure，这里也要对应设置：
        // c.setDomain(".example.com");
        // c.setSecure(true);
        response.addCookie(c);

        return success();
    }


    /**
     * 可选：查看是否登录 / 或返回当前用户基础信息
     * 这里仅示例：如果拦截器通过，说明已登录
     */
    @GetMapping("/ping")
    public Result<?> ping() {
        return success("ok");
    }

    private String extractToken(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return null;
        }
        return authHeader.substring(7);
    }
}
