package com.chatbot.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {
    
    @NotBlank(message = "消息内容不能为空")
    private String message;
    
    private String sessionId;
    
    /**
     * 是否启用联网搜索
     */
    @Builder.Default
    private Boolean enableWebSearch = false;
}
