package com.chatbot.controller;

import com.chatbot.dto.ApiResponse;
import com.chatbot.dto.ChatHistoryDTO;
import com.chatbot.service.ChatHistoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/history")
@RequiredArgsConstructor
public class ChatHistoryController {
    
    private final ChatHistoryService chatHistoryService;
    
    /**
     * 获取用户的所有对话历史
     */
    @GetMapping
    public ResponseEntity<ApiResponse<List<ChatHistoryDTO>>> getChatHistory(Authentication authentication) {
        List<ChatHistoryDTO> history = chatHistoryService.getUserChatHistory(authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(history));
    }
    
    /**
     * 分页获取对话历史
     */
    @GetMapping("/paged")
    public ResponseEntity<ApiResponse<Page<ChatHistoryDTO>>> getChatHistoryPaged(
            Authentication authentication,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        Page<ChatHistoryDTO> history = chatHistoryService.getUserChatHistoryPaged(
                authentication.getName(), page, size
        );
        return ResponseEntity.ok(ApiResponse.success(history));
    }
    
    /**
     * 获取指定会话的对话历史
     */
    @GetMapping("/session/{sessionId}")
    public ResponseEntity<ApiResponse<List<ChatHistoryDTO>>> getSessionHistory(
            Authentication authentication,
            @PathVariable String sessionId
    ) {
        List<ChatHistoryDTO> history = chatHistoryService.getSessionHistory(
                authentication.getName(), sessionId
        );
        return ResponseEntity.ok(ApiResponse.success(history));
    }
    
    /**
     * 获取用户的所有会话列表
     */
    @GetMapping("/sessions")
    public ResponseEntity<ApiResponse<List<String>>> getUserSessions(Authentication authentication) {
        List<String> sessions = chatHistoryService.getUserSessions(authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(sessions));
    }
    
    /**
     * 获取对话统计
     */
    @GetMapping("/count")
    public ResponseEntity<ApiResponse<Map<String, Long>>> getChatCount(Authentication authentication) {
        long count = chatHistoryService.getChatCount(authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(Map.of("count", count)));
    }
    
    /**
     * 删除指定会话
     */
    @DeleteMapping("/session/{sessionId}")
    public ResponseEntity<ApiResponse<Void>> deleteSession(
            Authentication authentication,
            @PathVariable String sessionId
    ) {
        chatHistoryService.deleteSession(authentication.getName(), sessionId);
        return ResponseEntity.ok(ApiResponse.success("会话删除成功", null));
    }
    
    /**
     * 删除所有对话历史
     */
    @DeleteMapping("/all")
    public ResponseEntity<ApiResponse<Void>> deleteAllHistory(Authentication authentication) {
        chatHistoryService.deleteAllHistory(authentication.getName());
        return ResponseEntity.ok(ApiResponse.success("所有对话历史已删除", null));
    }
}
