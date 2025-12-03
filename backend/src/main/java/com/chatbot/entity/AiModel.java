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
@Table(name = "ai_model")
public class AiModel {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    // 模型名称（如 deepseek-chat, gpt-4, claude-3 等）
    @Column(name = "model_name", nullable = false, unique = true, length = 100)
    private String modelName;
    
    // 模型显示名称
    @Column(name = "display_name", length = 100)
    private String displayName;
    
    // 每10000字收费（元）
    @Column(name = "price_per_10k_chars", precision = 10, scale = 4, nullable = false)
    private BigDecimal pricePer10kChars;
    
    // 服务数量（当前使用该模型的用户数或请求数）
    @Column(name = "service_count")
    @Builder.Default
    private Long serviceCount = 0L;
    
    // 提供的服务内容描述
    @Column(name = "service_description", columnDefinition = "TEXT")
    private String serviceDescription;
    
    // 模型能力标签（如：对话、代码、写作等，逗号分隔）
    @Column(name = "capabilities", length = 500)
    private String capabilities;
    
    // 模型提供商
    @Column(name = "provider", length = 50)
    private String provider;
    
    // 最大上下文长度（tokens）
    @Column(name = "max_context_length")
    private Integer maxContextLength;
    
    // 是否启用
    @Column(name = "enabled")
    @Builder.Default
    private Boolean enabled = true;
    
    // 排序权重（越小越靠前）
    @Column(name = "sort_order")
    @Builder.Default
    private Integer sortOrder = 100;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
