package com.chatbot.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RechargeRequest {
    
    @NotNull(message = "充值金额不能为空")
    @DecimalMin(value = "1.00", message = "充值金额不能小于1元")
    private BigDecimal amount;
}
