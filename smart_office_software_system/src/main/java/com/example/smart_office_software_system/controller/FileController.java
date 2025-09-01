package com.example.smart_office_software_system.controller;

import com.example.smart_office_software_system.domain.File;
import com.example.smart_office_software_system.pojo.Result;
import com.example.smart_office_software_system.service.FileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Date;
import java.util.List;
import java.util.UUID;

import static com.example.smart_office_software_system.pojo.Result.success;

/**
 * 文件控制类
 */
@RestController
@RequestMapping("/file")
public class FileController {

    @Value("${file.upload-dir1}")
    private String uploadDir1;  // Windows系统上传目录

    @Value("${file.upload-dir2}")
    private String uploadDir2;  // Linux系统上传目录

    @Autowired
    private FileService fileService;

    /**
     * 文件上传接口
     */
    @PostMapping("/upload")
    public Result<Object> uploadFile(
            @RequestParam("file") MultipartFile multipartFile,
            @RequestParam("userId") Integer userId,
            @RequestParam("scope") Integer scope,
            @RequestParam(value = "desc", required = false) String fileDescription,
            @RequestParam(value = "teamId", required = false) Integer teamId
    ) throws IOException {

        // 根据操作系统选择上传目录
        String baseUploadDir = System.getProperty("os.name").toLowerCase().contains("win") ? uploadDir1 : uploadDir2;

        // 统一路径分隔符为斜杠(/)
        baseUploadDir = baseUploadDir.replace("\\", "/");
        if (!baseUploadDir.endsWith("/")) {
            baseUploadDir += "/";
        }

        // 获取当前日期并格式化为目录结构
        LocalDate now = LocalDate.now();
        String datePath = now.format(DateTimeFormatter.ofPattern("yyyy/MM/dd"));

        // 构建完整用户文件路径
        String userPath = baseUploadDir + userId + "/" + datePath + "/";

        // 创建目录（如果不存在）
        Path dirPath = Paths.get(userPath);
        if (!Files.exists(dirPath)) {
            Files.createDirectories(dirPath);
        }

        // 处理文件名和扩展名
        String originalFilename = multipartFile.getOriginalFilename();
        String fileType = originalFilename.substring(originalFilename.lastIndexOf('.') + 1);
        String newFileName = UUID.randomUUID().toString() + "." + fileType;

        // 保存文件到指定路径
        Path filePath = dirPath.resolve(newFileName);
        multipartFile.transferTo(filePath.toFile());

        // 构建文件信息并保存到数据库
        File file = new File();
        file.setFileName(originalFilename);  // 原始文件名
        file.setFileType(fileType);        // 文件类型
        file.setUserId(userId);            // 用户ID
        file.setScope(scope);              // 文件范围
        file.setDesc(fileDescription);     // 文件描述
        file.setTeamId(teamId);            // 团队ID
        file.setCreatedAt(new Date());     // 创建时间
        file.setUpdatedAt(new Date());     // 更新时间

        // 构建相对路径和访问URL（统一使用斜杠）
        String relativePath = "files/" + userId + "/" + datePath + "/" + newFileName;
        String urlPath = "http://localhost:8080/" + relativePath;
        file.setFilePath(urlPath);         // 文件访问URL
        file.setFileSize(multipartFile.getSize());  // 文件大小

        fileService.saveFile(file);

        return success(filePath.toAbsolutePath().toString());
    }

    /**
     * 删除文件接口
     */
    @DeleteMapping("/delete/{fileId}")
    public Result<Object> deleteFile(@PathVariable Integer fileId) {
        fileService.deleteFileById(fileId);
        return Result.success("删除成功");
    }

    /**
     * 获取用户文件列表接口
     */
    @GetMapping("/getFile/user/{userId}")
    public List<File> getFilesByUserId(@PathVariable Integer userId) {
        return fileService.getFilesByUserId(userId);
    }
}