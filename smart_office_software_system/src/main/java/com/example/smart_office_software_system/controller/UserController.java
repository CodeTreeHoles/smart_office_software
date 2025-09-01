package com.example.smart_office_software_system.controller;

import com.example.smart_office_software_system.domain.User;
import com.example.smart_office_software_system.pojo.Result;
import com.example.smart_office_software_system.service.UserService;
import com.example.smart_office_software_system.utils.MD5Utils;
import com.example.smart_office_software_system.utils.SaltUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * @program: smart_office_software_system
 * @description:
 * @create: 2025-07-12 17:27
 **/

@Slf4j
@RequestMapping("/user")
@RestController
public class UserController {


    @Autowired
    private UserService userService;
    @Autowired
    private RedisTemplate<String,Object> redisTemplate;

    /** PUT /user/{id} —— 修改用户 */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Integer id,
                               @RequestBody User user) {





        Integer result = userService.updateUser(id, user);

        if (result > 0) {
            return Result.success();
        } else {
            return Result.error("修改失败");
        }
    }

    @PostMapping("/verification/role")
    public Result<String> verificationRole(@RequestBody User user) {
        Integer role = userService.verificationRole(user);
        String code = null;
        if (role == 0) {
            code = MD5Utils.MD5Lower(user.getPassword(), user.getAccount());
            if (code != null) {
                redisTemplate.opsForValue().set(code, role);
            }
        }
        return Result.success(code);
    }

}
