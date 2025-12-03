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
@Table(name = "recharge_order")
public class RechargeOrder {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "order_no", nullable = false, unique = true, length = 64)
    private String orderNo;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;
    
    /**
     * 订单状态: PENDING-待支付, PAID-已支付, EXPIRED-已过期, CANCELLED-已取消
     */
    @Column(name = "status", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    @Builder.Default
    private OrderStatus status = OrderStatus.PENDING;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "paid_at")
    private LocalDateTime paidAt;
    
    @Column(name = "expired_at")
    private LocalDateTime expiredAt;
    
    /**
     * 过期时间（创建后5分钟）
     */
    @Column(name = "expire_time", nullable = false)
    private LocalDateTime expireTime;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (expireTime == null) {
            expireTime = createdAt.plusMinutes(5);
        }
    }
    
    public enum OrderStatus {
        PENDING,    // 待支付
        PAID,       // 已支付
        EXPIRED,    // 已过期
        CANCELLED   // 已取消
    }
}
