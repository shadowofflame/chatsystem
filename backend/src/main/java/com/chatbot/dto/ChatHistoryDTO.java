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
public class ChatHistoryDTO {
    
    private Long id;
    private String sessionId;
    private String userMessage;
    private String assistantResponse;
    private LocalDateTime createdAt;
}
