package com.chatbot.service;

import com.chatbot.dto.ChatHistoryDTO;
import com.chatbot.dto.SessionStatsDTO;
import com.chatbot.entity.ChatHistory;
import com.chatbot.entity.User;
import com.chatbot.repository.ChatHistoryRepository;
import com.chatbot.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatHistoryService {
    
    private final ChatHistoryRepository chatHistoryRepository;
    private final UserRepository userRepository;
    
    /**
     * 保存对话记录并计算费用
     * @return ChatHistoryDTO 包含费用信息
     */
    @Transactional
    public ChatHistoryDTO saveChat(String username, String sessionId, String userMessage, String assistantResponse) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        ChatHistory chatHistory = ChatHistory.builder()
                .user(user)
                .sessionId(sessionId)
                .userMessage(userMessage)
                .assistantResponse(assistantResponse)
                .build();
        
        // 计算字数和费用
        chatHistory.calculateCost();
        
        chatHistory = chatHistoryRepository.save(chatHistory);
        
        log.debug("保存对话记录: user={}, sessionId={}, inputChars={}, outputChars={}, cost={}", 
                username, sessionId, chatHistory.getInputCharCount(), 
                chatHistory.getOutputCharCount(), chatHistory.getCost());
        
        return convertToDTO(chatHistory);
    }
    
    /**
     * 保存对话记录并扣除余额
     * @return ChatHistoryDTO 包含费用信息
     * @throws RuntimeException 如果余额不足
     */
    @Transactional
    public ChatHistoryDTO saveChatAndDeductBalance(String username, String sessionId, 
            String userMessage, String assistantResponse) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        ChatHistory chatHistory = ChatHistory.builder()
                .user(user)
                .sessionId(sessionId)
                .userMessage(userMessage)
                .assistantResponse(assistantResponse)
                .build();
        
        // 计算字数和费用
        chatHistory.calculateCost();
        BigDecimal cost = chatHistory.getCost();
        
        // 检查余额是否足够
        if (user.getBalance().compareTo(cost) < 0) {
            throw new RuntimeException("余额不足，当前余额: " + user.getBalance() + " 元，需要: " + cost + " 元");
        }
        
        // 扣除余额
        user.setBalance(user.getBalance().subtract(cost));
        userRepository.save(user);
        
        chatHistory = chatHistoryRepository.save(chatHistory);
        
        log.info("对话扣费成功: user={}, sessionId={}, cost={}, newBalance={}", 
                username, sessionId, cost, user.getBalance());
        
        return convertToDTO(chatHistory);
    }
    
    /**
     * 预估对话费用（仅根据输入字数预估）
     */
    public BigDecimal estimateCost(String message) {
        int charCount = message != null ? message.length() : 0;
        // 假设回复字数与输入字数相当，预估总字数
        int estimatedTotal = charCount * 2;
        return BigDecimal.valueOf(estimatedTotal)
                .divide(BigDecimal.valueOf(10000), 2, java.math.RoundingMode.HALF_UP);
    }
    
    /**
     * 获取用户的所有对话历史
     */
    public List<ChatHistoryDTO> getUserChatHistory(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return chatHistoryRepository.findByUserOrderByCreatedAtDesc(user)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * 分页获取用户的对话历史
     */
    public Page<ChatHistoryDTO> getUserChatHistoryPaged(String username, int page, int size) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        Pageable pageable = PageRequest.of(page, size);
        
        return chatHistoryRepository.findByUserOrderByCreatedAtDesc(user, pageable)
                .map(this::convertToDTO);
    }
    
    /**
     * 获取指定会话的对话历史
     */
    public List<ChatHistoryDTO> getSessionHistory(String username, String sessionId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return chatHistoryRepository.findByUserAndSessionIdOrderByCreatedAtAsc(user, sessionId)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * 获取指定会话的统计信息
     */
    public SessionStatsDTO getSessionStats(String username, String sessionId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        List<ChatHistory> histories = chatHistoryRepository.findByUserAndSessionIdOrderByCreatedAtAsc(user, sessionId);
        
        int inputCharCount = 0;
        int outputCharCount = 0;
        int totalCharCount = 0;
        BigDecimal totalCost = BigDecimal.ZERO;
        
        for (ChatHistory history : histories) {
            inputCharCount += history.getInputCharCount() != null ? history.getInputCharCount() : 0;
            outputCharCount += history.getOutputCharCount() != null ? history.getOutputCharCount() : 0;
            totalCharCount += history.getTotalCharCount() != null ? history.getTotalCharCount() : 0;
            totalCost = totalCost.add(history.getCost() != null ? history.getCost() : BigDecimal.ZERO);
        }
        
        return SessionStatsDTO.builder()
                .model("deepseek-chat")  // 当前使用的模型
                .inputCharCount(inputCharCount)
                .outputCharCount(outputCharCount)
                .totalCharCount(totalCharCount)
                .messageCount(histories.size())
                .totalCost(totalCost)
                .build();
    }
    
    /**
     * 获取用户的所有会话ID
     */
    public List<String> getUserSessions(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return chatHistoryRepository.findDistinctSessionIdsByUser(user);
    }
    
    /**
     * 删除指定会话的对话历史
     */
    @Transactional
    public void deleteSession(String username, String sessionId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        chatHistoryRepository.deleteByUserAndSessionId(user, sessionId);
        log.info("删除会话历史: user={}, sessionId={}", username, sessionId);
    }
    
    /**
     * 删除用户的所有对话历史
     */
    @Transactional
    public void deleteAllHistory(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        chatHistoryRepository.deleteByUser(user);
        log.info("删除所有对话历史: user={}", username);
    }
    
    /**
     * 获取用户对话数量
     */
    public long getChatCount(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return chatHistoryRepository.countByUser(user);
    }
    
    /**
     * 获取用户总消费金额
     */
    public BigDecimal getUserTotalCost(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        BigDecimal total = chatHistoryRepository.sumCostByUser(user);
        return total != null ? total : BigDecimal.ZERO;
    }
    
    /**
     * 获取指定会话的总消费金额
     */
    public BigDecimal getSessionTotalCost(String username, String sessionId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        BigDecimal total = chatHistoryRepository.sumCostByUserAndSessionId(user, sessionId);
        return total != null ? total : BigDecimal.ZERO;
    }
    
    private ChatHistoryDTO convertToDTO(ChatHistory chatHistory) {
        return ChatHistoryDTO.builder()
                .id(chatHistory.getId())
                .sessionId(chatHistory.getSessionId())
                .userMessage(chatHistory.getUserMessage())
                .assistantResponse(chatHistory.getAssistantResponse())
                .createdAt(chatHistory.getCreatedAt())
                .inputCharCount(chatHistory.getInputCharCount())
                .outputCharCount(chatHistory.getOutputCharCount())
                .totalCharCount(chatHistory.getTotalCharCount())
                .cost(chatHistory.getCost())
                .build();
    }
}
