package com.chatbot.service;

import com.chatbot.dto.ChatRequest;
import com.chatbot.dto.ChatResponse;
import com.chatbot.dto.MemoryStats;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class PythonAgentService {
    
    private final WebClient pythonAgentWebClient;
    
    /**
     * 发送消息到 Python Agent 进行对话
     */
    public ChatResponse chat(ChatRequest request) {
        try {
            log.debug("Sending chat request to Python Agent: {}", request.getMessage());
            
            Map<String, Object> response = pythonAgentWebClient.post()
                    .uri("/api/chat")
                    .bodyValue(Map.of(
                            "message", request.getMessage(),
                            "session_id", request.getSessionId() != null ? request.getSessionId() : "default"
                    ))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            if (response != null && response.containsKey("response")) {
                String message = (String) response.get("response");
                String sessionId = (String) response.get("session_id");
                
                log.debug("Received response from Python Agent: {}", message);
                return ChatResponse.success(message, sessionId);
            }
            
            return ChatResponse.error("Empty response from agent");
            
        } catch (WebClientResponseException e) {
            log.error("Python Agent error: {} - {}", e.getStatusCode(), e.getResponseBodyAsString());
            return ChatResponse.error("Agent error: " + e.getMessage());
        } catch (Exception e) {
            log.error("Error communicating with Python Agent", e);
            return ChatResponse.error("Communication error: " + e.getMessage());
        }
    }
    
    /**
     * 获取记忆统计信息
     */
    public MemoryStats getMemoryStats() {
        try {
            Map<String, Object> response = pythonAgentWebClient.get()
                    .uri("/api/stats")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            if (response != null) {
                return MemoryStats.builder()
                        .longTermMemories(((Number) response.getOrDefault("long_term_memories", 0)).intValue())
                        .shortTermMessages(((Number) response.getOrDefault("short_term_messages", 0)).intValue())
                        .build();
            }
            
            return MemoryStats.builder().build();
            
        } catch (Exception e) {
            log.error("Error getting memory stats", e);
            return MemoryStats.builder().build();
        }
    }
    
    /**
     * 清除短期记忆
     */
    public boolean clearShortTermMemory() {
        try {
            pythonAgentWebClient.post()
                    .uri("/api/memory/clear-short-term")
                    .retrieve()
                    .bodyToMono(Void.class)
                    .block();
            return true;
        } catch (Exception e) {
            log.error("Error clearing short-term memory", e);
            return false;
        }
    }
    
    /**
     * 清除所有记忆
     */
    public boolean clearAllMemory() {
        try {
            pythonAgentWebClient.post()
                    .uri("/api/memory/clear-all")
                    .retrieve()
                    .bodyToMono(Void.class)
                    .block();
            return true;
        } catch (Exception e) {
            log.error("Error clearing all memory", e);
            return false;
        }
    }
    
    /**
     * 检查 Python Agent 健康状态
     */
    public boolean isHealthy() {
        try {
            pythonAgentWebClient.get()
                    .uri("/health")
                    .retrieve()
                    .bodyToMono(Void.class)
                    .block();
            return true;
        } catch (Exception e) {
            log.warn("Python Agent is not healthy: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 调用 Python Agent 总结文本
     */
    public String summarizeText(String text, Integer maxLength) {
        try {
            log.debug("Sending summarize request to Python Agent, text length: {}", text.length());
            
            Map<String, Object> requestBody = Map.of(
                    "text", text,
                    "max_length", maxLength != null ? maxLength : 15
            );
            
            Map<String, Object> response = pythonAgentWebClient.post()
                    .uri("/api/summarize")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            if (response != null && response.containsKey("summary")) {
                String summary = (String) response.get("summary");
                log.debug("Received summary from Python Agent: {}", summary);
                return summary;
            }
            
            return text.length() > 20 ? text.substring(0, 20) + "..." : text;
            
        } catch (WebClientResponseException e) {
            log.error("Python Agent summarize error: {} - {}", e.getStatusCode(), e.getResponseBodyAsString());
            return text.length() > 20 ? text.substring(0, 20) + "..." : text;
        } catch (Exception e) {
            log.error("Error calling summarize API", e);
            return text.length() > 20 ? text.substring(0, 20) + "..." : text;
        }
    }
}
