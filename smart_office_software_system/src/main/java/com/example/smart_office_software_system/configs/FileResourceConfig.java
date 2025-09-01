package com.example.smart_office_software_system.configs;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class FileResourceConfig implements WebMvcConfigurer {

    @Value("${file.upload-dir1}")
    private String uploadDir1;  // Windows系统上传目录

    @Value("${file.upload-dir2}")
    private String uploadDir2;  // Linux系统上传目录

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 根据操作系统选择上传目录
        String baseUploadDir = System.getProperty("os.name").toLowerCase().contains("win")
                ? uploadDir1 : uploadDir2;

        // 统一路径分隔符为斜杠(/)
        baseUploadDir = baseUploadDir.replace("\\", "/");
        if (!baseUploadDir.endsWith("/")) {
            baseUploadDir += "/";
        }

        // 添加资源处理器
        registry
                .addResourceHandler("/files/**") // 请求路径前缀
                .addResourceLocations("file:" + baseUploadDir); // 动态本地路径
    }
}