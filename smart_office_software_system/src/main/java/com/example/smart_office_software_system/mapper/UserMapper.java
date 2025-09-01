package com.example.smart_office_software_system.mapper;

import com.example.smart_office_software_system.domain.User;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserMapper {
    User findByUsername(@Param("account") String account);

    Integer insertUser(@Param("user") User user);

    Integer update(@Param("user") User user , @Param("id") Integer id);

    Integer delete(@Param("id") Integer userId);

    Integer getUserById(@Param("id") Integer id);

    @Delete("DELETE u FROM user u " +
            "INNER JOIN department_user du ON u.id = du.user_id " +
            "WHERE du.dept_id = #{id}")
    int deleteUserByDepartmentId(@Param("id") Integer id);
}
