package com.example.smart_office_software_system.service.impl;

import com.example.smart_office_software_system.domain.File;
import com.example.smart_office_software_system.mapper.FileMapper;
import com.example.smart_office_software_system.service.FileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;


/**
 * @program: smart_office_software_system
 * @description: 文件实现类
 * @create: 2025-05-29 18:15
 **/




@Service
public class FileServiceImpl implements FileService {

    @Autowired
    private FileMapper fileMapper;

    @Override
    public void saveFile(File file) {
        fileMapper.insertFile(file);
    }
    @Override
    public void deleteFileById(Integer fileId) {
        // 1. 查询文件信息
        File file = fileMapper.getFileById(fileId);
        if (file != null) {
            // 2. 删除物理文件
            String urlPath = file.getFilePath(); // 例如 http://localhost:8080/files/1/2024/06/03/xxx.pdf
            // 只保留 /files/ 后面的部分
            String relativePath = urlPath.substring(urlPath.indexOf("/files/") + 7);
            // 拼接本地路径（根据你的 FileResourceConfig 配置）
            String localPath = "E:/smart_office_software/" + relativePath.replace("/", java.io.File.separator);
            java.io.File diskFile = new java.io.File(localPath);
            if (diskFile.exists()) {
                diskFile.delete();
            }
        }
        // 3. 删除数据库记录
        fileMapper.deleteFileById(fileId);
    }
    @Override
    public List<File> getFilesByUserId(Integer userId) {
        return fileMapper.getFilesByUserId(userId);
    }
}
