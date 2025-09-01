package com.example.smart_office_software_system.service.impl;
import com.example.smart_office_software_system.domain.User;
import com.example.smart_office_software_system.mapper.UserMapper;
import com.example.smart_office_software_system.service.AuthService;
import com.example.smart_office_software_system.utils.JwtUtil;
import com.example.smart_office_software_system.utils.MD5Utils;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthServiceImpl.class);
    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;
    private final StringRedisTemplate redisTemplate;

    @Value("${auth.token.prefix:LOGIN:TOKEN:}")
    private String tokenPrefix;

    @Value("${auth.token.expire-minutes:120}")
    private long tokenExpireMinutes;

    @Override
    public String login(String username, String passwordPlain) {
        User u = userMapper.findByUsername(username);
        if (u == null) {
            throw new RuntimeException("账号不存在");
        }

        // 使用你现有的 MD5Utils（优先：大写 + 加盐；若库里没盐字段则退化为无盐）
        String calc;
        log.info("getSalt:{}" , StringUtils.hasText(u.getSalt()));
        if (StringUtils.hasText(u.getSalt())) {
            calc = MD5Utils.MD5Upper(passwordPlain, u.getSalt());
        } else {
            calc = MD5Utils.MD5Upper(passwordPlain);
        }

        if (calc == null || !calc.equalsIgnoreCase(u.getPassword())) {
            throw new RuntimeException("密码错误");
        }

        // role 字段是 int，0=管理员，1=普通用户
        int role = (u.getRole() != null) ? u.getRole() : 1; // 默认普通用户

        // 生成 JWT 时把 int 存进去
        String jwt = jwtUtil.generateToken(u.getId(), u.getAccount(), role);


        // 生成随机 token，Redis 保存：token -> jwt
        String token = UUID.randomUUID().toString().replace("-", "");
        String key = tokenPrefix + token;
        redisTemplate.opsForValue().set(key, jwt, tokenExpireMinutes, TimeUnit.MINUTES);

        return token; // 返回给前端，之后放到 Authorization: Bearer <token>
    }

    @Override
    public void logout(String token) {
        String key = tokenPrefix + token;
        redisTemplate.delete(key);
    }

    @Override
    public void renewIfNecessary(String token) {
        String key = tokenPrefix + token;
        Long ttlSeconds = redisTemplate.getExpire(key, TimeUnit.SECONDS);
        // 剩余 < 30 分钟则续期
        if (ttlSeconds != null && ttlSeconds > 0 && ttlSeconds < 30 * 60) {
            redisTemplate.expire(key, tokenExpireMinutes, TimeUnit.MINUTES);
        }
    }
}
