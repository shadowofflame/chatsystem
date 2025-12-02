package com.chatbot.service;

import com.chatbot.dto.ChatHistoryDTO;
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

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatHistoryService {
    
    private final ChatHistoryRepository chatHistoryRepository;
    private final UserRepository userRepository;
    
    /**
     * 保存对话记录
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
        
        chatHistory = chatHistoryRepository.save(chatHistory);
        
        log.debug("保存对话记录: user={}, sessionId={}", username, sessionId);
        
        return convertToDTO(chatHistory);
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
    
    private ChatHistoryDTO convertToDTO(ChatHistory chatHistory) {
        return ChatHistoryDTO.builder()
                .id(chatHistory.getId())
                .sessionId(chatHistory.getSessionId())
                .userMessage(chatHistory.getUserMessage())
                .assistantResponse(chatHistory.getAssistantResponse())
                .createdAt(chatHistory.getCreatedAt())
                .build();
    }
}
