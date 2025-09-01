package com.example.smart_office_software_system.mapper;

import com.example.smart_office_software_system.domain.Department;
import com.example.smart_office_software_system.dto.DepartmentDTO;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface DepartmentMapper {


    List<DepartmentDTO> getDepartmentListByUserId();

    DepartmentDTO getDepartmentById(@Param("id") Integer id);
    @Select("SELECT dept_id FROM department_user WHERE user_id = #{id}")
    Integer getDepartmentByUserId(@Param("id") Integer id);
                  // 返回影响行数即可，id 自动回填到 user 对象
    Integer insertDeptUser(@Param("deptId") Integer deptId,
                           @Param("userId") Integer userId);
    @Select("SELECT * FROM department WHERE id=#{id}")
    Department getDepartment(@Param("id")Integer id);

    @Delete("delete from department where id=#{id}")
    Integer deleteDepartment(@Param("id") Integer id);

    Integer updateDepartment(Department department);
    @Insert("insert into department (dept_name,dept_intro,leader_id,created_at,updated_at) " +
            "values (#{deptName},#{deptIntro},#{leaderId},now(),now());")
    Integer addDepartment(Department department);
}
