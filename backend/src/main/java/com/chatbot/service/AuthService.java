package com.chatbot.service;

import com.chatbot.dto.*;
import com.chatbot.entity.User;
import com.chatbot.repository.UserRepository;
import com.chatbot.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    
    @Transactional
    public AuthResponse register(RegisterRequest request) {
        // 检查用户名是否已存在
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }
        
        // 检查邮箱是否已存在
        if (request.getEmail() != null && userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("邮箱已被使用");
        }
        
        // 创建用户
        User user = User.builder()
                .username(request.getUsername())
                .password(passwordEncoder.encode(request.getPassword()))
                .email(request.getEmail())
                .nickname(request.getNickname() != null ? request.getNickname() : request.getUsername())
                .enabled(true)
                .build();
        
        userRepository.save(user);
        
        // 生成 JWT
        String token = jwtTokenProvider.generateToken(user);
        
        log.info("用户注册成功: {}", user.getUsername());
        
        return AuthResponse.builder()
                .token(token)
                .username(user.getUsername())
                .nickname(user.getNickname())
                .message("注册成功")
                .build();
    }
    
    @Transactional
    public AuthResponse login(LoginRequest request, AuthenticationManager authenticationManager) {
        log.info("尝试登录用户: {}", request.getUsername());
        
        // 先检查用户是否存在
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> {
                    log.error("用户不存在: {}", request.getUsername());
                    return new RuntimeException("用户不存在");
                });
        
        log.info("找到用户: {}, 密码哈希: {}", user.getUsername(), user.getPassword().substring(0, 10) + "...");
        
        try {
            // 验证用户名密码
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
            );
        } catch (Exception e) {
            log.error("认证失败: {}", e.getMessage());
            throw e;
        }
        
        // 更新最后登录时间
        user.setLastLogin(LocalDateTime.now());
        userRepository.save(user);
        
        // 生成 JWT
        String token = jwtTokenProvider.generateToken(user);
        
        log.info("用户登录成功: {}", user.getUsername());
        
        return AuthResponse.builder()
                .token(token)
                .username(user.getUsername())
                .nickname(user.getNickname())
                .message("登录成功")
                .build();
    }
    
    public UserDTO getCurrentUser(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return UserDTO.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .createdAt(user.getCreatedAt())
                .lastLogin(user.getLastLogin())
                .build();
    }
}
