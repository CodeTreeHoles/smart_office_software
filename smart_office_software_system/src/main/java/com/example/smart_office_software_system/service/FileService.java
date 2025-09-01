package com.example.smart_office_software_system.service;

import com.example.smart_office_software_system.domain.File;

import java.util.List;

public interface FileService {
    void saveFile(File file);
    void deleteFileById(Integer fileId);

    List<File> getFilesByUserId(Integer userId);
}
