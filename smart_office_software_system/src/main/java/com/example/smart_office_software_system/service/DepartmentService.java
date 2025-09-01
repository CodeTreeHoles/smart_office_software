package com.example.smart_office_software_system.service;

import com.example.smart_office_software_system.domain.Department;
import com.example.smart_office_software_system.dto.DepartmentDTO;
import com.example.smart_office_software_system.domain.User;

import java.util.List;

public interface DepartmentService {
    List<DepartmentDTO> getDepartmentListByUserId();

    DepartmentDTO getDepartmentById(Integer id);

    Integer getDepartmentByUserId(Integer id);
    Integer insertUser(Integer deptId, User user);

    Integer updateUser(Integer userId, User user);

    Integer deleteUser(Integer userId);
    Department getDepartment(Integer id);
    Integer deleteDepartment(Integer id);
    Integer updateDepartment(Department department);
    Integer addDepartment(Department department);
}
