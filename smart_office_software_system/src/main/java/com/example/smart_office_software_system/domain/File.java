package com.example.smart_office_software_system.domain;

import lombok.Data;

import java.util.Date;

/**
 * @program: smart_office_software_system
 * @description: 文件实体类
 * @create: 2025-05-29 18:12
 **/


@Data
public class File {

    private Integer id;
    private String fileName;
    private String fileType;
    private Integer userId;
    private Integer scope;
    private Date createdAt;
    private Date updatedAt;
    private String filePath;
    private Long fileSize;
    private String desc;
    private Integer teamId;


}
