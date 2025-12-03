package com.chatbot.repository;

import com.chatbot.entity.ChatSession;
import com.chatbot.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChatSessionRepository extends JpaRepository<ChatSession, Long> {
    
    Optional<ChatSession> findBySessionId(String sessionId);
    
    Optional<ChatSession> findByUserAndSessionId(User user, String sessionId);
    
    List<ChatSession> findByUserOrderByUpdatedAtDesc(User user);
    
    void deleteByUserAndSessionId(User user, String sessionId);
    
    void deleteByUser(User user);
    
    boolean existsBySessionId(String sessionId);
}
