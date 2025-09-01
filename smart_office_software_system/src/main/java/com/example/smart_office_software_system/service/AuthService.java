package com.example.smart_office_software_system.service;


public interface AuthService {
    String login(String account, String passwordPlain);
    void logout(String token);
    void renewIfNecessary(String token);
}
