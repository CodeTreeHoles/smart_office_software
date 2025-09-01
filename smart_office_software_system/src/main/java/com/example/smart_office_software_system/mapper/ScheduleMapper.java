package com.example.smart_office_software_system.mapper;
import com.example.smart_office_software_system.domain.Schedule;
import org.apache.ibatis.annotations.*;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface ScheduleMapper {
    @Select("SELECT * FROM schedule WHERE user_id = #{userId}")
    List<Schedule> findByUserId(Long userId);
    @Select("SELECT * FROM schedule " +
            "WHERE user_id = #{userId} " +
            "AND start_time >= #{startTime} " + // 当天开始时间
            "AND start_time < #{endTime}")     // 当天结束时间
    List<Schedule> findByUserIdAndDate(
            @Param("userId") Long userId,
            @Param("startTime") LocalDateTime startTime,
            @Param("endTime") LocalDateTime endTime
    );
    @Delete("DELETE FROM schedule WHERE id = #{id}")
    void deleteById(Long id);

    @Insert("INSERT INTO schedule " +
            "(event_name,start_time,end_time,description,user_id) values " +
            "(#{eventName},#{startTime},#{endTime},#{description},#{userId})")
    void addSchedule(Schedule schedule);
    @Select("SELECT * FROM schedule WHERE task_id = #{taskId}")
    Schedule findByTaskId(String taskId);
    @Delete("DELETE FROM schedule WHERE task_id = #{taskId}")
    void deleteByTaskId(String taskId);


    void updateSchedule(Schedule schedule);
}
