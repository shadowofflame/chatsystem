package com.chatbot.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {
    
    private String message;
    private String sessionId;
    private LocalDateTime timestamp;
    private boolean success;
    private String error;
    
    public static ChatResponse success(String message, String sessionId) {
        return ChatResponse.builder()
                .message(message)
                .sessionId(sessionId)
                .timestamp(LocalDateTime.now())
                .success(true)
                .build();
    }
    
    public static ChatResponse error(String error) {
        return ChatResponse.builder()
                .error(error)
                .timestamp(LocalDateTime.now())
                .success(false)
                .build();
    }
}
