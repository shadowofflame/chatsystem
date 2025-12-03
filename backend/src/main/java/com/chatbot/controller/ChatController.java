package com.chatbot.controller;

import com.chatbot.dto.ApiResponse;
import com.chatbot.dto.ChatHistoryDTO;
import com.chatbot.dto.ChatRequest;
import com.chatbot.dto.ChatResponse;
import com.chatbot.dto.MemoryStats;
import com.chatbot.service.ChatHistoryService;
import com.chatbot.service.ChatSessionService;
import com.chatbot.service.PythonAgentService;
import com.chatbot.service.RechargeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;

@Slf4j
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {
    
    private final PythonAgentService pythonAgentService;
    private final ChatHistoryService chatHistoryService;
    private final ChatSessionService chatSessionService;
    private final RechargeService rechargeService;
    
    /**
     * 发送聊天消息（带扣费功能）
     */
    @PostMapping
    public ResponseEntity<ApiResponse<ChatResponse>> chat(
            @Valid @RequestBody ChatRequest request,
            Authentication authentication
    ) {
        String username = authentication.getName();
        log.info("Received chat request from user {}: {}", username, request.getMessage());
        
        // 检查用户余额
        BigDecimal balance = rechargeService.getUserBalance(username);
        if (balance.compareTo(BigDecimal.ZERO) <= 0) {
            return ResponseEntity.ok(ApiResponse.error("余额不足，请先充值"));
        }
        
        String sessionId = request.getSessionId() != null ? request.getSessionId() : "default";
        
        // 确保会话存在，如果不存在则创建（验证用户所有权）
        if (chatSessionService.getUserSession(username, sessionId) == null) {
            var newSession = chatSessionService.createSession(username, sessionId);
            sessionId = newSession.getSessionId(); // 使用可能更新后的 sessionId
        }
        
        // 更新 request 中的 sessionId（如果有变化）
        request.setSessionId(sessionId);
        
        ChatResponse response = pythonAgentService.chat(request);
        
        if (response.isSuccess()) {
            try {
                // 保存对话历史并扣除余额
                ChatHistoryDTO chatHistory = chatHistoryService.saveChatAndDeductBalance(
                        username,
                        sessionId,
                        request.getMessage(),
                        response.getMessage()
                );
                
                // 将费用信息添加到响应中
                response.setCost(chatHistory.getCost());
                response.setInputCharCount(chatHistory.getInputCharCount());
                response.setOutputCharCount(chatHistory.getOutputCharCount());
                response.setTotalCharCount(chatHistory.getTotalCharCount());
                response.setNewBalance(rechargeService.getUserBalance(username));
                
                log.info("Chat completed with cost: {} yuan, new balance: {}", 
                        chatHistory.getCost(), response.getNewBalance());
                
            } catch (RuntimeException e) {
                // 余额不足
                log.warn("余额扣除失败: {}", e.getMessage());
                return ResponseEntity.ok(ApiResponse.error(e.getMessage()));
            }
            
            // 增加会话消息计数
            chatSessionService.incrementMessageCount(sessionId);
            
            // 在第一条消息后更新会话标题
            chatSessionService.updateSessionTitle(sessionId, request.getMessage());
            
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
