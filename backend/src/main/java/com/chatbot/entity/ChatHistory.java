package com.chatbot.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "chat_history")
public class ChatHistory {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "session_id", length = 100)
    private String sessionId;
    
    @Column(name = "user_message", columnDefinition = "TEXT", nullable = false)
    private String userMessage;
    
    @Column(name = "assistant_response", columnDefinition = "TEXT")
    private String assistantResponse;
    
    // 字数统计字段
    @Column(name = "input_char_count")
    @Builder.Default
    private Integer inputCharCount = 0;
    
    @Column(name = "output_char_count")
    @Builder.Default
    private Integer outputCharCount = 0;
    
    @Column(name = "total_char_count")
    @Builder.Default
    private Integer totalCharCount = 0;
    
    // 费用字段（精确到小数点后两位）
    @Column(name = "cost", precision = 10, scale = 2)
    @Builder.Default
    private BigDecimal cost = BigDecimal.ZERO;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
    
    /**
     * 计算字数和费用
     * 规则：每10000字扣费1元
     */
    public void calculateCost() {
        this.inputCharCount = userMessage != null ? userMessage.length() : 0;
        this.outputCharCount = assistantResponse != null ? assistantResponse.length() : 0;
        this.totalCharCount = this.inputCharCount + this.outputCharCount;
        
        // 计算费用：每10000字1元，精确到小数点后两位
        this.cost = BigDecimal.valueOf(this.totalCharCount)
                .divide(BigDecimal.valueOf(10000), 2, java.math.RoundingMode.HALF_UP);
    }
}
