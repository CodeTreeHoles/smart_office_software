package com.example.smart_office_software_system.mapper;


import com.example.smart_office_software_system.domain.File;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface FileMapper {
    int insertFile(File file);
    int deleteFileById(Integer fileId);
    List<File> getFilesByUserId(Integer userId);
    File getFileById(Integer fileId);
}
