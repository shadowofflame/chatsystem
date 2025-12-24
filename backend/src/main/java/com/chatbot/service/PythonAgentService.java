package com.chatbot.service;

import com.chatbot.dto.ChatRequest;
import com.chatbot.dto.ChatResponse;
import com.chatbot.dto.MemoryStats;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Flux;
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
            log.debug("Sending chat request to Python Agent: {}, enableWebSearch: {}, deepThink: {}", 
                    request.getMessage(), request.getEnableWebSearch(), request.getDeepThink());
            
            Map<String, Object> requestBody = new java.util.HashMap<>();
            requestBody.put("message", request.getMessage());
            requestBody.put("session_id", request.getSessionId() != null ? request.getSessionId() : "default");
            requestBody.put("enable_web_search", request.getEnableWebSearch() != null && request.getEnableWebSearch());
            requestBody.put("deep_think", request.getDeepThink() != null && request.getDeepThink());
            requestBody.put("thought_branches", request.getThoughtBranches() != null ? request.getThoughtBranches() : 5);
            requestBody.put("thought_depth", request.getThoughtDepth() != null ? request.getThoughtDepth() : 3);
            
            Map<String, Object> response = pythonAgentWebClient.post()
                    .uri("/api/chat")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            if (response != null && response.containsKey("response")) {
                String message = (String) response.get("response");
                String sessionId = (String) response.get("session_id");
                
                // 获取 TOT 思考过程相关字段
                String thinkingProcess = (String) response.getOrDefault("thinking_process", "");
                Double totScore = response.get("tot_score") != null ? 
                        ((Number) response.get("tot_score")).doubleValue() : 0.0;
                Boolean deepThink = (Boolean) response.getOrDefault("deep_think", false);
                
                log.debug("Received response from Python Agent: {}, deepThink: {}, totScore: {}", 
                        message, deepThink, totScore);
                
                return ChatResponse.successWithThinking(message, sessionId, thinkingProcess, totScore, deepThink);
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
    
    /**
     * 流式对话 - 返回 SSE 事件流
     * 使用 DataBuffer 逐块转发，保持原始格式
     */
    public Flux<String> chatStream(ChatRequest request) {
        log.info("Starting streaming chat request: {}, enableWebSearch: {}, deepThink: {}", 
                request.getMessage(), request.getEnableWebSearch(), request.getDeepThink());
        
        Map<String, Object> requestBody = new java.util.HashMap<>();
        requestBody.put("message", request.getMessage());
        requestBody.put("session_id", request.getSessionId() != null ? request.getSessionId() : "default");
        requestBody.put("enable_web_search", request.getEnableWebSearch() != null && request.getEnableWebSearch());
        requestBody.put("deep_think", request.getDeepThink() != null && request.getDeepThink());
        requestBody.put("thought_branches", request.getThoughtBranches() != null ? request.getThoughtBranches() : 5);
        requestBody.put("thought_depth", request.getThoughtDepth() != null ? request.getThoughtDepth() : 3);
        
        return pythonAgentWebClient.post()
                .uri("/api/chat/stream")
                .contentType(org.springframework.http.MediaType.APPLICATION_JSON)
                .accept(org.springframework.http.MediaType.TEXT_EVENT_STREAM)
                .bodyValue(requestBody)
                .exchangeToFlux(response -> {
                    if (response.statusCode().is2xxSuccessful()) {
                        // 使用 DataBuffer 直接读取原始字节流
                        return response.bodyToFlux(org.springframework.core.io.buffer.DataBuffer.class)
                                .map(dataBuffer -> {
                                    byte[] bytes = new byte[dataBuffer.readableByteCount()];
                                    dataBuffer.read(bytes);
                                    org.springframework.core.io.buffer.DataBufferUtils.release(dataBuffer);
                                    String chunk = new String(bytes, java.nio.charset.StandardCharsets.UTF_8);
                                    log.debug("Received chunk from Agent: {} bytes", bytes.length);
                                    return chunk;
                                });
                    } else {
                        log.error("Python Agent error: {}", response.statusCode());
                        return Flux.just("data: {\"type\":\"error\",\"content\":\"Agent error\"}\n\n");
                    }
                })
                .onErrorResume(error -> {
                    log.error("Stream error: {}", error.getMessage());
                    return Flux.just("data: {\"type\":\"error\",\"content\":\"" + error.getMessage().replace("\"", "'") + "\"}\n\n");
                })
                .doOnComplete(() -> log.info("Stream completed"));
    }
}
