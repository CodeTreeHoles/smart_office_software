package com.example.smart_office_software_system.service.impl;

import com.example.smart_office_software_system.domain.User;
import com.example.smart_office_software_system.mapper.UserMapper;
import com.example.smart_office_software_system.service.UserService;
import com.example.smart_office_software_system.utils.MD5Utils;
import com.example.smart_office_software_system.utils.SaltUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.Objects;

/**
 * @program: smart_office_software_system
 * @description: 用户实现类
 * @create: 2025-05-29 14:14
 **/


@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserMapper userMapper;

    @Override
    public User login(String account, String password) {
        User user = userMapper.findByUsername(account);
        if (user != null && user.getPassword().equals(password)) {
            return user;
        }
        return null;
    }

    @Override
    public Integer updateUser(Integer id, User user) {
        String rawPwd = user.getPassword();
        String salt = SaltUtil.generateSalt();
        String hashedPwd = MD5Utils.MD5Upper(rawPwd, salt);
        user.setPassword(hashedPwd);
        user.setSalt(salt);
        return userMapper.update(user , id);

    }

    @Override
    public Integer verificationRole(User user) {
        User u = userMapper.findByUsername(user.getAccount());
        String calc;
        if (StringUtils.hasText(u.getSalt())) {
            System.out.println(user.getPassword());
            System.out.println(u.getSalt());
            calc = MD5Utils.MD5Upper(user.getPassword(), u.getSalt());
        } else {
            calc = MD5Utils.MD5Upper(user.getPassword());
        }
        if(Objects.equals(calc, u.getPassword())){
            return u.getRole();
        }
        return 1;
    }

    @Override
    public User findByAccount(String account) {
        return userMapper.findByUsername(account);
    }
}
