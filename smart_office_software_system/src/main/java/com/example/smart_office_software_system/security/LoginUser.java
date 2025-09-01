package com.example.smart_office_software_system.security;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

// security/LoginUser.java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class LoginUser {
    private Long userId;
    private String username;
    private Integer role;
}

