package com.example.smart_office_software_system.domain;

import lombok.Data;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;


/**
 * @program: smart_office_software_system
 * @description: 用户实体类
 * @create: 2025-05-29 14:11
 **/

@Data
public class User {
    private Integer id;
    private String account;
    private String password;
    private String email;
    private Integer role;
    private String salt;


}
