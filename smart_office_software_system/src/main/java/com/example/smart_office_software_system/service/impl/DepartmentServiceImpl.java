package com.example.smart_office_software_system.service.impl;

import com.example.smart_office_software_system.domain.Department;
import com.example.smart_office_software_system.dto.DepartmentDTO;
import com.example.smart_office_software_system.domain.User;
import com.example.smart_office_software_system.mapper.DepartmentMapper;
import com.example.smart_office_software_system.mapper.UserMapper;
import com.example.smart_office_software_system.service.DepartmentService;
import com.example.smart_office_software_system.utils.MD5Utils;
import com.example.smart_office_software_system.utils.SaltUtil;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @program: smart_office_software_system
 * @description: 部门实现类
 * @create: 2025-07-07 18:20
 **/

@Service
public class DepartmentServiceImpl implements DepartmentService {

    @Autowired
    private DepartmentMapper departmentMapper;

    @Autowired
    private UserMapper userMapper;


    @Override
    public List<DepartmentDTO> getDepartmentListByUserId() {
        return departmentMapper.getDepartmentListByUserId();
    }

    @Override
    public DepartmentDTO getDepartmentById(Integer id) {
        return departmentMapper.getDepartmentById(id);
    }

    @Override
    public Integer getDepartmentByUserId(Integer id) {
        return departmentMapper.getDepartmentByUserId(id);
    }

    @Override
    public Integer insertUser(Integer deptId, User user) {

        User userInfo = new User();
        BeanUtils.copyProperties(user , userInfo);

        userInfo.setRole(1);
        String rawPwd = "123456";
        String salt = SaltUtil.generateSalt();
        String hashedPwd = MD5Utils.MD5Upper(rawPwd, salt);
        userInfo.setPassword(hashedPwd);
        userInfo.setSalt(salt);
        userMapper.insertUser(userInfo);                       // user.id 得到自增值
        Integer result = departmentMapper.insertDeptUser(deptId, userInfo.getId());

        return result;

    }

    @Override
    public Integer updateUser(Integer userId, User user) {
        return userMapper.update(user , userId);

    }

    @Override
    public Integer deleteUser(Integer userId) {
        return userMapper.delete(userId);
    }

    @Override
    public Department getDepartment(Integer id) {
        return departmentMapper.getDepartment(id);
    }

    @Override
    public Integer deleteDepartment(Integer id) {
        Integer res = departmentMapper.deleteDepartment(id);
        userMapper.deleteUserByDepartmentId(id);
        return res;
    }

    @Override
    public Integer updateDepartment(Department department) {
        return departmentMapper.updateDepartment(department);
    }

    @Override
    public Integer addDepartment(Department department) {
        return departmentMapper.addDepartment(department);
    }
}
