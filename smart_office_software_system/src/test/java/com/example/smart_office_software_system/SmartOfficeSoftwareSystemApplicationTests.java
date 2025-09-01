package com.example.smart_office_software_system;
import com.example.smart_office_software_system.domain.Department;
import com.example.smart_office_software_system.mapper.DepartmentMapper;
import com.example.smart_office_software_system.service.EmailService;
import com.example.smart_office_software_system.utils.MD5Utils;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.redis.core.RedisTemplate;

import java.time.LocalDateTime;

@SpringBootTest
class SmartOfficeSoftwareSystemApplicationTests {

    @Autowired
    private EmailService emailService;
    @Autowired
    private RedisTemplate<String,Object> redisTemplate;
    @Autowired
    private DepartmentMapper departmentMapper;

    @Test
    void test3(){
        Department department = new Department();
//        department.setId(1);
        department.setLeaderId(2);
        department.setDeptName("技术部2");
        department.setDeptIntro("负责公司所有技术开发与维护工作");
        departmentMapper.addDepartment(department);
    }
    @Test
    void contextLoads() {
    }

    @Test
    void test() throws InterruptedException {
        LocalDateTime specificDateTime = LocalDateTime.of(2025, 6, 8, 11, 55);
        emailService.sendEmail("你好","demo",specificDateTime,"h18395303098@163.com");
        Thread.sleep(130000);
    }

    @Test
    void test2(){
        System.out.println(redisTemplate.opsForValue().get("task_123456"));
    }


    @Test
    void password() {
        String rawPassword = "123456";
        String encrypted = MD5Utils.MD5Lower(rawPassword);
        System.out.println(encrypted);

    }
}
