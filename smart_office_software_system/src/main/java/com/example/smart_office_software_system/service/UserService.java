package com.example.smart_office_software_system.service;

import com.example.smart_office_software_system.domain.User;

public interface UserService {
    User login(String account, String password);

    Integer updateUser(Integer id, User user);
    Integer verificationRole(User user);

    User findByAccount(String account);
}
