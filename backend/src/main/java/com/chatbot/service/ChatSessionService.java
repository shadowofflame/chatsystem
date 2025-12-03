package com.chatbot.service;

import com.chatbot.dto.SessionDTO;
import com.chatbot.entity.ChatSession;
import com.chatbot.entity.User;
import com.chatbot.repository.ChatSessionRepository;
import com.chatbot.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatSessionService {
    
    private final ChatSessionRepository chatSessionRepository;
    private final UserRepository userRepository;
    private final PythonAgentService pythonAgentService;
    
    /**
     * 创建新会话
     */
    @Transactional
    public ChatSession createSession(String username, String sessionId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        // 检查会话是否已存在（只检查当前用户的会话）
        Optional<ChatSession> existingSession = chatSessionRepository.findByUserAndSessionId(user, sessionId);
        if (existingSession.isPresent()) {
            return existingSession.get();
        }
        
        // 如果 sessionId 被其他用户使用，为当前用户生成新的 sessionId
        if (chatSessionRepository.existsBySessionId(sessionId)) {
            sessionId = java.util.UUID.randomUUID().toString();
        }
        
        ChatSession session = ChatSession.builder()
                .user(user)
                .sessionId(sessionId)
                .title("新对话")
                .messageCount(0)
                .build();
        
        session = chatSessionRepository.save(session);
        log.info("创建新会话: user={}, sessionId={}", username, sessionId);
        
        return session;
    }
    
    /**
     * 更新会话标题（在第一条消息后调用）
     */
    @Transactional
    public void updateSessionTitle(String sessionId, String firstMessage) {
        ChatSession session = chatSessionRepository.findBySessionId(sessionId)
                .orElseThrow(() -> new RuntimeException("会话不存在"));
        
        // 只在消息数为1且标题还是"新对话"时更新标题
        if (session.getMessageCount() == 1 && "新对话".equals(session.getTitle())) {
            String title = pythonAgentService.summarizeText(firstMessage, 15);
            session.setTitle(title);
            chatSessionRepository.save(session);
            log.info("更新会话标题: sessionId={}, title={}", sessionId, title);
        }
    }
    
    /**
     * 增加会话消息计数
     */
    @Transactional
    public void incrementMessageCount(String sessionId) {
        ChatSession session = chatSessionRepository.findBySessionId(sessionId)
                .orElseThrow(() -> new RuntimeException("会话不存在"));
        
        session.setMessageCount(session.getMessageCount() + 1);
        chatSessionRepository.save(session);
    }
    
    /**
     * 获取用户的所有会话
     */
    public List<SessionDTO> getUserSessions(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return chatSessionRepository.findByUserOrderByUpdatedAtDesc(user)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * 获取会话信息（不验证用户）
     */
    public ChatSession getSession(String sessionId) {
        return chatSessionRepository.findBySessionId(sessionId)
                .orElse(null);
    }
    
    /**
     * 获取用户的指定会话
     */
    public ChatSession getUserSession(String username, String sessionId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return chatSessionRepository.findByUserAndSessionId(user, sessionId)
                .orElse(null);
    }
    
    /**
     * 删除会话
     */
    @Transactional
    public void deleteSession(String username, String sessionId) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        chatSessionRepository.deleteByUserAndSessionId(user, sessionId);
        log.info("删除会话: user={}, sessionId={}", username, sessionId);
    }
    
    /**
     * 删除用户的所有会话
     */
    @Transactional
    public void deleteAllSessions(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        chatSessionRepository.deleteByUser(user);
        log.info("删除所有会话: user={}", username);
    }
    
    private SessionDTO convertToDTO(ChatSession session) {
        return SessionDTO.builder()
                .sessionId(session.getSessionId())
                .title(session.getTitle())
                .lastMessageTime(session.getUpdatedAt())
                .build();
    }
}
