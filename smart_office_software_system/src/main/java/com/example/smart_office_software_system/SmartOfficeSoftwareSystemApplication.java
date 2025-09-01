package com.example.smart_office_software_system;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
//@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SmartOfficeSoftwareSystemApplication {

    public static void main(String[] args) {
        SpringApplication.run(SmartOfficeSoftwareSystemApplication.class, args);
        System.out.println("项目启动成功················································");
    }

}
