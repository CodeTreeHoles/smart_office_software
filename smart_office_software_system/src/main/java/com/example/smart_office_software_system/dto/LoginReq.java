package com.example.smart_office_software_system.dto;
import javax.validation.constraints.NotBlank;

import lombok.Data;

@Data
public class LoginReq {
    @NotBlank(message = "工号不能为空")
    private String account;

    @NotBlank(message = "密码不能为空")
    private String password;
}
