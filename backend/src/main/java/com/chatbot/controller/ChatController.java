package com.chatbot.controller;

import com.chatbot.dto.ApiResponse;
import com.chatbot.dto.ChatRequest;
import com.chatbot.dto.ChatResponse;
import com.chatbot.dto.MemoryStats;
import com.chatbot.service.ChatHistoryService;
import com.chatbot.service.PythonAgentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {
    
    private final PythonAgentService pythonAgentService;
    private final ChatHistoryService chatHistoryService;
    
    /**
     * 发送聊天消息
     */
    @PostMapping
    public ResponseEntity<ApiResponse<ChatResponse>> chat(
            @Valid @RequestBody ChatRequest request,
            Authentication authentication
    ) {
        String username = authentication.getName();
        log.info("Received chat request from user {}: {}", username, request.getMessage());
        
        ChatResponse response = pythonAgentService.chat(request);
        
        if (response.isSuccess()) {
            // 保存到对话历史
            chatHistoryService.saveChat(
                    username,
                    request.getSessionId() != null ? request.getSessionId() : "default",
                    request.getMessage(),
                    response.getMessage()
            );
            return ResponseEntity.ok(ApiResponse.success(response));
        } else {
            return ResponseEntity.ok(ApiResponse.error(response.getError()));
        }
    }
    
    /**
     * 获取记忆统计
     */
    @GetMapping("/stats")
    public ResponseEntity<ApiResponse<MemoryStats>> getStats() {
        MemoryStats stats = pythonAgentService.getMemoryStats();
        return ResponseEntity.ok(ApiResponse.success(stats));
    }
    
    /**
     * 清除短期记忆
     */
    @PostMapping("/memory/clear-short-term")
    public ResponseEntity<ApiResponse<Void>> clearShortTermMemory() {
        boolean success = pythonAgentService.clearShortTermMemory();
        if (success) {
            return ResponseEntity.ok(ApiResponse.success("Short-term memory cleared", null));
        } else {
            return ResponseEntity.ok(ApiResponse.error("Failed to clear short-term memory"));
        }
    }
    
    /**
     * 清除所有记忆
     */
    @PostMapping("/memory/clear-all")
    public ResponseEntity<ApiResponse<Void>> clearAllMemory() {
        boolean success = pythonAgentService.clearAllMemory();
        if (success) {
            return ResponseEntity.ok(ApiResponse.success("All memory cleared", null));
        } else {
            return ResponseEntity.ok(ApiResponse.error("Failed to clear all memory"));
        }
    }
    
    /**
     * 健康检查
     */
    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        boolean agentHealthy = pythonAgentService.isHealthy();
        String status = agentHealthy ? "All services are healthy" : "Python Agent is not available";
        
        return ResponseEntity.ok(ApiResponse.success("status", status));
    }
}
