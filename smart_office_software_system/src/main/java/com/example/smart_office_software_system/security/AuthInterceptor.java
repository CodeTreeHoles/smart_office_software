package com.example.smart_office_software_system.security;

import com.example.smart_office_software_system.service.AuthService;
import com.example.smart_office_software_system.utils.JwtUtil;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@Component
@RequiredArgsConstructor
public class AuthInterceptor implements HandlerInterceptor {

    private final StringRedisTemplate redisTemplate;
    private final JwtUtil jwtUtil;
    private final AuthService authService;

    @Value("${auth.token.prefix:LOGIN:TOKEN:}")
    private String tokenPrefix;

    private static final AntPathMatcher PATH_MATCHER = new AntPathMatcher();

    /** 放行清单：按需补充你的公开接口 */
    private static final String[] WHITELIST = new String[]{
            "/", "/index.html", "/error",
            "/auth/login", "/auth/logout", "/auth/ping", "/auth/me",
            "/swagger-ui/**", "/v3/**", "/swagger-resources/**", "/doc.html", "/webjars/**",
            "/favicon.ico",
            "/static/**", "/assets/**", "/css/**", "/js/**", "/images/**"
    };

    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse resp, Object handler) throws Exception {
        String method = req.getMethod();

        // 1) CORS 预检放行
        if ("OPTIONS".equalsIgnoreCase(method)) {
            resp.setStatus(HttpServletResponse.SC_OK);
            return true;
        }

        // 2) 白名单放行 —— 先去掉 contextPath 再匹配
        String uri = req.getRequestURI();
        String ctx = req.getContextPath();
        String path = (ctx != null && !ctx.isEmpty() && uri.startsWith(ctx)) ? uri.substring(ctx.length()) : uri;
        System.out.println("[AUTH] ctx=" + ctx + ", uri=" + uri + ", path=" + path);

        for (String p : WHITELIST) {
            if (PATH_MATCHER.match(p, path)) {
                return true; // 放行登录、文档、静态等
            }
        }

        // 3) 非控制器方法不拦
        if (!(handler instanceof HandlerMethod)) return true;

        // 4) 先从 Header 再从 Cookie 提取 token（替换你原来的 Authorization 读取）
        String token = resolveToken(req);
        if (token == null) {
            return write401(resp, "未登录（缺少 token）");
        }

        // 5) 用 token 去 Redis 换 jwt
        String key = tokenPrefix + token;
        String jwt = redisTemplate.opsForValue().get(key);
        if (jwt == null || jwt.isEmpty()) {
            return write401(resp, "登录已过期或无效（Redis未命中）");
        }

        // 6) 解析 JWT
        try {
            Claims c = jwtUtil.parse(jwt).getBody();
            Long userId = Long.valueOf(c.getSubject());
            String username = c.get("username", String.class);
            if (username == null) username = "";

            Object roleObj = c.get("role");
            int role = 1; // 默认普通用户
            if (roleObj instanceof Number) {
                role = ((Number) roleObj).intValue();
            } else if (roleObj instanceof String) {
                try { role = Integer.parseInt((String) roleObj); } catch (Exception ignore) {}
            }

            UserContext.set(new LoginUser(userId, username, role));

            authService.renewIfNecessary(token);  // 滑动续期
            return true;
        } catch (Exception e) {
            e.printStackTrace();
            return write401(resp, "令牌无效（JWT解析失败）");
        }
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        UserContext.clear();
    }

    private boolean write401(HttpServletResponse resp, String msg) throws Exception {
        resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        resp.setContentType("application/json;charset=UTF-8");
        resp.getWriter().write("{\"code\":401,\"msg\":\"" + msg + "\"}");
        return false;
    }

    /** 统一从 Header 或 Cookie 提取 token */
    private String resolveToken(HttpServletRequest req) {
        // 1) Header: Authorization: Bearer <token>
        String auth = req.getHeader("Authorization");
        if (auth != null && auth.length() >= 8) {
            String prefix = auth.substring(0, 7);
            if ("Bearer ".equals(prefix) || "bearer ".equals(prefix)) {
                String t = auth.substring(7).trim();
                if (!t.isEmpty()) return t;
            }
        }
        // 2) Cookie: LOGIN_TOKEN
        javax.servlet.http.Cookie[] cookies = req.getCookies();
        if (cookies != null) {
            for (javax.servlet.http.Cookie c : cookies) {
                if ("LOGIN_TOKEN".equals(c.getName())) {
                    String v = c.getValue();
                    if (v != null && !v.trim().isEmpty()) return v.trim();
                }
            }
        }
        return null;
    }
}
