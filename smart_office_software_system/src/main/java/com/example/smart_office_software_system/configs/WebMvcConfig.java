package com.example.smart_office_software_system.configs;
import com.example.smart_office_software_system.security.AuthInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.*;

@Configuration
@RequiredArgsConstructor
public class WebMvcConfig implements WebMvcConfigurer {

    private final AuthInterceptor authInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(authInterceptor)
                .addPathPatterns("/**"); // 白名单在拦截器内部处理
    }

//    @Override
//    public void addCorsMappings(CorsRegistry registry) {
//        registry.addMapping("/**")
//                .allowedOrigins("http://localhost:8081","http://localhost:90","http://localhost:80")
//                .allowedMethods("GET","POST","PUT","DELETE","OPTIONS")
//                .allowedHeaders("*")
//                .exposedHeaders("*")
//                .allowCredentials(true)      // 允许携带 Cookie
//                .maxAge(3600);
//    }
    @Override
    public void addCorsMappings(CorsRegistry registry) {

        registry.addMapping("/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET","POST","PUT","DELETE","OPTIONS")
                .allowedHeaders("*")              // 或至少包含 Authorization
                .exposedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }

}
