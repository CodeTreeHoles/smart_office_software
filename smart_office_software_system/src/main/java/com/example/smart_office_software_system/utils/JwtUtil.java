package com.example.smart_office_software_system.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
@ConfigurationProperties(prefix = "auth.jwt")
@Data
@Slf4j
public class JwtUtil {
    private String secret;
    private long expireMinutes;

    public String generateToken(Integer userId, String username, Integer role) {
        Date now = new Date();
        Date exp = new Date(now.getTime() + expireMinutes * 60 * 1000);
        return Jwts.builder()
                .setSubject(String.valueOf(userId))
                .claim("username", username)
                .claim("role", role)
                .setIssuedAt(now)
                .setExpiration(exp)
                .signWith(SignatureAlgorithm.HS256, secret.getBytes(StandardCharsets.UTF_8))
                .compact();
    }


    public Jws<Claims> parse(String jwt) {
        return Jwts.parser()
                .setSigningKey(secret.getBytes(StandardCharsets.UTF_8))
                .parseClaimsJws(jwt);
    }
}
