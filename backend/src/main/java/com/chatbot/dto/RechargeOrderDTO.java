package com.chatbot.dto;

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
public class RechargeOrderDTO {
    
    private Long id;
    private String orderNo;
    private BigDecimal amount;
    private String status;
    private String statusText;
    private LocalDateTime createdAt;
    private LocalDateTime paidAt;
    private LocalDateTime expireTime;
    private Long remainingSeconds; // 剩余支付时间（秒）
}
