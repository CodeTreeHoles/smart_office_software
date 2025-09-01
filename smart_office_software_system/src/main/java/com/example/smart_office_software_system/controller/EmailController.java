package com.example.smart_office_software_system.controller;
import com.example.smart_office_software_system.pojo.Result;
import com.example.smart_office_software_system.service.EmailService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;

@RestController
@Slf4j
@RequestMapping("/email")
public class EmailController {
    @Autowired
    private EmailService emailService;
    @PostMapping("/send")
    public Result<String> sendEmail(
            @RequestParam  String message,
            @RequestParam  String subject,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime sendTime,
            @RequestParam  String email){
        String res =emailService.sendEmail(message,subject,sendTime,email);
        log.info("content:{},subject:{},sendTime:{},email:{}",message,subject,sendTime,email);
        return Result.success(res);
    }
    @DeleteMapping("/cancel")
    public Result<String> cancelEmail(String taskId){
        emailService.cancelEmail(taskId);
        return Result.success();
    }
}
