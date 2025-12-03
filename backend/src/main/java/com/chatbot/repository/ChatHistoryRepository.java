package com.chatbot.repository;

import com.chatbot.entity.ChatHistory;
import com.chatbot.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface ChatHistoryRepository extends JpaRepository<ChatHistory, Long> {
    
    List<ChatHistory> findByUserOrderByCreatedAtDesc(User user);
    
    Page<ChatHistory> findByUserOrderByCreatedAtDesc(User user, Pageable pageable);
    
    List<ChatHistory> findByUserAndSessionIdOrderByCreatedAtAsc(User user, String sessionId);
    
    @Query("SELECT DISTINCT c.sessionId FROM ChatHistory c WHERE c.user = :user ORDER BY MAX(c.createdAt) DESC")
    List<String> findDistinctSessionIdsByUser(@Param("user") User user);
    
    @Query("SELECT c FROM ChatHistory c WHERE c.user = :user AND c.id IN " +
           "(SELECT MIN(ch.id) FROM ChatHistory ch WHERE ch.user = :user GROUP BY ch.sessionId) " +
           "ORDER BY c.createdAt DESC")
    List<ChatHistory> findFirstMessageBySessionForUser(@Param("user") User user);
    
    void deleteByUserAndSessionId(User user, String sessionId);
    
    void deleteByUser(User user);
    
    long countByUser(User user);
    
    /**
     * 计算用户的总消费金额
     */
    @Query("SELECT SUM(c.cost) FROM ChatHistory c WHERE c.user = :user")
    BigDecimal sumCostByUser(@Param("user") User user);
    
    /**
     * 计算指定会话的总消费金额
     */
    @Query("SELECT SUM(c.cost) FROM ChatHistory c WHERE c.user = :user AND c.sessionId = :sessionId")
    BigDecimal sumCostByUserAndSessionId(@Param("user") User user, @Param("sessionId") String sessionId);
}
