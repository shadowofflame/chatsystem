package com.chatbot.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiModelDTO {
    
    private Long id;
    
    // 模型名称
    private String modelName;
    
    // 显示名称
    private String displayName;
    
    // 每10000字收费（元）
    private BigDecimal pricePer10kChars;
    
    // 服务数量
    private Long serviceCount;
    
    // 服务描述
    private String serviceDescription;
    
    // 能力标签列表
    private List<String> capabilities;
    
    // 提供商
    private String provider;
    
    // 最大上下文长度
    private Integer maxContextLength;
    
    // 是否启用
    private Boolean enabled;
}
