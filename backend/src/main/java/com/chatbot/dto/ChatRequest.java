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
    
    /**
     * 是否启用深度思考(TOT - Tree of Thoughts)
     */
    @Builder.Default
    private Boolean deepThink = false;
    
    /**
     * 思考分支数量 (TOT参数)
     */
    @Builder.Default
    private Integer thoughtBranches = 3;
    
    /**
     * 思考深度 (TOT参数)
     */
    @Builder.Default
    private Integer thoughtDepth = 2;
}
