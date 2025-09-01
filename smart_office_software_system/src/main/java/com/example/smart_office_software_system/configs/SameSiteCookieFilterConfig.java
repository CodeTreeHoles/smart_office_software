package com.example.smart_office_software_system.configs;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.servlet.http.HttpServletResponse;
@Configuration
public class SameSiteCookieFilterConfig {

    @Bean
    public org.springframework.boot.web.servlet.FilterRegistrationBean<org.springframework.web.filter.OncePerRequestFilter> sameSiteCookieFilter() {
        return new org.springframework.boot.web.servlet.FilterRegistrationBean<>(
                new org.springframework.web.filter.OncePerRequestFilter() {
                    @Override
                    protected void doFilterInternal(javax.servlet.http.HttpServletRequest req,
                                                    javax.servlet.http.HttpServletResponse resp,
                                                    javax.servlet.FilterChain chain)
                            throws javax.servlet.ServletException, java.io.IOException {
                        chain.doFilter(req, new javax.servlet.http.HttpServletResponseWrapper(resp) {
                            @Override
                            public void addCookie(javax.servlet.http.Cookie cookie) {
                                String name = cookie.getName();
                                String value = cookie.getValue();
                                String path = cookie.getPath() == null ? "/" : cookie.getPath();
                                StringBuilder sb = new StringBuilder();
                                sb.append(name).append("=").append(value)
                                        .append("; Path=").append(path)
                                        .append("; HttpOnly")
                                        .append("; SameSite=None; Secure"); // 关键：跨站需要
                                if (cookie.getMaxAge() > 0) {
                                    sb.append("; Max-Age=").append(cookie.getMaxAge());
                                }
                                // 如需跨子域：sb.append("; Domain=.example.com");
                                ((HttpServletResponse) getResponse()).addHeader("Set-Cookie", sb.toString());
                            }
                        });
                    }
                }
        );
    }
}
