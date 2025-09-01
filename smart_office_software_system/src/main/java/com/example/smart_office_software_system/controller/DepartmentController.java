package com.example.smart_office_software_system.controller;

import com.example.smart_office_software_system.domain.Department;
import com.example.smart_office_software_system.dto.DepartmentDTO;
import com.example.smart_office_software_system.domain.User;
import com.example.smart_office_software_system.pojo.Result;
import com.example.smart_office_software_system.service.DepartmentService;
import org.apache.ibatis.annotations.Delete;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * @program: smart_office_software_system
 * @description: 部门控制
 * @create: 2025-07-07 18:02
 **/


@RestController
@RequestMapping("/document")
public class DepartmentController {

    @Autowired
    private DepartmentService departmentService;


    /**
     * @Description: 查询部门列表
     * @return: com.example.smart_office_software_system.pojo.Result<java.util.List>
     * @params: [userId]
     * @paramsType: [java.lang.Integer]
     * @Author: 黄胜
     * @Date: 2025/7/7 18:28
     */
    @GetMapping("/list")
    public Result<List> getDepartmentListByUserId() {
        return Result.success(departmentService.getDepartmentListByUserId());
    }


    @GetMapping("/{id}")
    public Result<DepartmentDTO> getDepartmentById(@PathVariable Integer id) {

        return Result.success(departmentService.getDepartmentById(id));
    }
    @GetMapping("/fromUser/{id}")
    public Result<Integer> getDepartmentByUserId(@PathVariable Integer id) {
        return Result.success(departmentService.getDepartmentByUserId(id));
    }

    @PostMapping("/{deptId}/user")
    public Result<Void> addTeamUser(@PathVariable Integer deptId,
                                    @RequestBody @Validated User user) {


        Integer result = departmentService.insertUser(deptId, user);
        if (result > 0) {
            return Result.success();
        } else {
            return Result.error("新增失败");
        }
    }


    /** 4) PUT /document/{deptId}/user/{userId} —— 修改成员职位等信息 */
    @PutMapping("/{deptId}/user/{userId}")
    public Result<Void> updateTeamUser(@PathVariable Integer deptId,
                                       @PathVariable Integer userId,
                                       @RequestBody @Validated User user) {
        Integer result = departmentService.updateUser(userId, user);

        if (result > 0) {
            return Result.success();
        } else {
            return Result.error("修改失败");
        }
    }

    /** 5) DELETE /document/{deptId}/user/{userId} —— 删除成员 */
    @DeleteMapping("/{deptId}/user/{userId}")
    public Result<Void> deleteTeamUser(@PathVariable Integer deptId,
                                       @PathVariable Integer userId) {
        Integer result = departmentService.deleteUser(userId);
        if (result > 0) {
            return Result.success();
        } else {
            return Result.error("删除失败");
        }
    }

    /**
     * 根据id删除部门
     * @param deptId
     * @return
     */
    @DeleteMapping("/{deptId}")
    public Result<Void> deleteDepartment(@PathVariable Integer deptId){
        Integer result = departmentService.deleteDepartment(deptId);
        if (result > 0) {
            return Result.success();
        } else {
            return Result.error("删除失败");
        }
    }

    /**
     * 更新部门信息
     * @param department
     * @return
     */
    @PutMapping("/update")
    public Result<Void> updateDepartment(@RequestBody @Validated Department department){
        Integer result = departmentService.updateDepartment(department);
        if (result > 0) {
            return Result.success();
        } else {
            return Result.error("删除失败");
        }
    }

    /**
     * 添加新的部门
     * @param department
     * @return
     */
    @PostMapping("/add")
    public Result<Void> add(@RequestBody @Validated Department department){
        Integer result = departmentService.addDepartment(department);
        if (result > 0) {
            return Result.success();
        } else {
            return Result.error("删除失败");
        }
    }
}
