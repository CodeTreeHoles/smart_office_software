package com.example.smart_office_software_system.controller;

import com.example.smart_office_software_system.domain.Schedule;
import com.example.smart_office_software_system.pojo.Result;
import com.example.smart_office_software_system.service.ScheduledService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RequestMapping("/scheduled")
@RestController
public class ScheduledController {

    @Autowired
    private ScheduledService scheduledService;
    @PostMapping("/add")
    public Result<String> addSchedule(@RequestBody Schedule schedule) {
            // 添加新的日程
            scheduledService.addSchedule(schedule);
            // 返回成功结果，包含任务ID
            return Result.success();
    }
    @PutMapping("/update")
    public Result updateSchedule(@RequestBody Schedule schedule){
        scheduledService.update(schedule);
        return Result.success();
    }
    @GetMapping("/list/{userId}")
    public Result<List<Schedule>> findByUserId(@PathVariable Long userId){
        return Result.success(scheduledService.findByUserId(userId));
    }
    @DeleteMapping("/cancel/{taskId}")
    public Result<String> cancelSchedule(@PathVariable String taskId){
        scheduledService.deleteByTaskId(taskId);
        return Result.success("删除成功");
    }
    @DeleteMapping("/cancel/by/{id}")
    public Result cancelScheduleById(@PathVariable Long id){
        scheduledService.deleteById(id);
        return Result.success();
    }
    @GetMapping("/list/date")
    public Result<List<Schedule>> findByUserIdAndDate(@RequestParam Long userId,@RequestParam String date){
        log.info("请求{}的日程信息，userId:{}",date,userId);
        List<Schedule> list = scheduledService.findByUserIdAndDate(userId,date);
        return Result.success(list);
    }
}