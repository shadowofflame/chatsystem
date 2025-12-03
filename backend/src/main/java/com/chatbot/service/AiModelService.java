package com.chatbot.service;

import com.chatbot.dto.AiModelDTO;
import com.chatbot.entity.AiModel;
import com.chatbot.repository.AiModelRepository;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class AiModelService {
    
    private final AiModelRepository aiModelRepository;
    
    /**
     * 应用启动时初始化默认模型数据
     */
    @PostConstruct
    @Transactional
    public void initDefaultModels() {
        if (aiModelRepository.count() == 0) {
            log.info("初始化默认AI模型数据...");
            
            // DeepSeek Chat
            aiModelRepository.save(AiModel.builder()
                    .modelName("deepseek-chat")
                    .displayName("DeepSeek Chat")
                    .pricePer10kChars(new BigDecimal("0.50"))
                    .serviceCount(0L)
                    .serviceDescription("DeepSeek官方对话模型，性价比极高，支持中英文对话")
                    .capabilities("对话,中文,英文,代码生成,文本理解")
                    .provider("DeepSeek")
                    .maxContextLength(32768)
                    .sortOrder(1)
                    .enabled(true)
                    .build());
            
            // DeepSeek Reasoner
            aiModelRepository.save(AiModel.builder()
                    .modelName("deepseek-reasoner")
                    .displayName("DeepSeek Reasoner")
                    .pricePer10kChars(new BigDecimal("2.00"))
                    .serviceCount(0L)
                    .serviceDescription("DeepSeek推理模型，擅长复杂逻辑推理和数学问题")
                    .capabilities("推理,数学,逻辑分析,复杂问题")
                    .provider("DeepSeek")
                    .maxContextLength(32768)
                    .sortOrder(2)
                    .enabled(true)
                    .build());
            
            // GPT-4o
            aiModelRepository.save(AiModel.builder()
                    .modelName("gpt-4o")
                    .displayName("GPT-4o")
                    .pricePer10kChars(new BigDecimal("3.00"))
                    .serviceCount(0L)
                    .serviceDescription("OpenAI最新旗舰模型，支持多模态输入，能力全面")
                    .capabilities("对话,多模态,代码,创意写作,分析")
                    .provider("OpenAI")
                    .maxContextLength(128000)
                    .sortOrder(3)
                    .enabled(true)
                    .build());
            
            // GPT-4o Mini
            aiModelRepository.save(AiModel.builder()
                    .modelName("gpt-4o-mini")
                    .displayName("GPT-4o Mini")
                    .pricePer10kChars(new BigDecimal("0.30"))
                    .serviceCount(0L)
                    .serviceDescription("GPT-4o的轻量版本，速度快，成本低")
                    .capabilities("对话,快速响应,日常任务")
                    .provider("OpenAI")
                    .maxContextLength(128000)
                    .sortOrder(4)
                    .enabled(true)
                    .build());
            
            // Claude 3.5 Sonnet
            aiModelRepository.save(AiModel.builder()
                    .modelName("claude-3.5-sonnet")
                    .displayName("Claude 3.5 Sonnet")
                    .pricePer10kChars(new BigDecimal("1.50"))
                    .serviceCount(0L)
                    .serviceDescription("Anthropic出品，擅长长文本处理和代码编写")
                    .capabilities("对话,长文本,代码,分析,创作")
                    .provider("Anthropic")
                    .maxContextLength(200000)
                    .sortOrder(5)
                    .enabled(true)
                    .build());
            
            // Claude 3 Opus
            aiModelRepository.save(AiModel.builder()
                    .modelName("claude-3-opus")
                    .displayName("Claude 3 Opus")
                    .pricePer10kChars(new BigDecimal("4.00"))
                    .serviceCount(0L)
                    .serviceDescription("Anthropic最强模型，适合复杂任务和深度分析")
                    .capabilities("深度分析,复杂推理,专业写作,研究")
                    .provider("Anthropic")
                    .maxContextLength(200000)
                    .sortOrder(6)
                    .enabled(true)
                    .build());
            
            // Qwen Max
            aiModelRepository.save(AiModel.builder()
                    .modelName("qwen-max")
                    .displayName("通义千问 Max")
                    .pricePer10kChars(new BigDecimal("1.20"))
                    .serviceCount(0L)
                    .serviceDescription("阿里云通义千问大模型，中文能力突出")
                    .capabilities("中文,对话,知识问答,文本生成")
                    .provider("阿里云")
                    .maxContextLength(32000)
                    .sortOrder(7)
                    .enabled(true)
                    .build());
            
            // Gemini Pro
            aiModelRepository.save(AiModel.builder()
                    .modelName("gemini-pro")
                    .displayName("Gemini Pro")
                    .pricePer10kChars(new BigDecimal("1.00"))
                    .serviceCount(0L)
                    .serviceDescription("Google最新AI模型，多模态能力强")
                    .capabilities("多模态,代码,推理,创意")
                    .provider("Google")
                    .maxContextLength(128000)
                    .sortOrder(8)
                    .enabled(true)
                    .build());
            
            log.info("成功初始化 {} 个AI模型", aiModelRepository.count());
        }
    }
    
    /**
     * 获取所有启用的模型
     */
    public List<AiModelDTO> getEnabledModels() {
        return aiModelRepository.findByEnabledTrueOrderBySortOrderAsc()
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * 获取所有模型（包括禁用的）
     */
    public List<AiModelDTO> getAllModels() {
        return aiModelRepository.findAllByOrderBySortOrderAsc()
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * 根据模型名称获取模型
     */
    public AiModelDTO getModelByName(String modelName) {
        return aiModelRepository.findByModelName(modelName)
                .map(this::convertToDTO)
                .orElse(null);
    }
    
    /**
     * 根据模型名称获取价格
     */
    public BigDecimal getModelPrice(String modelName) {
        return aiModelRepository.findByModelName(modelName)
                .map(AiModel::getPricePer10kChars)
                .orElse(BigDecimal.ONE); // 默认每10000字1元
    }
    
    /**
     * 增加模型使用计数
     */
    @Transactional
    public void incrementServiceCount(String modelName) {
        aiModelRepository.incrementServiceCount(modelName);
    }
    
    /**
     * 转换为DTO
     */
    private AiModelDTO convertToDTO(AiModel model) {
        List<String> capabilityList = Collections.emptyList();
        if (model.getCapabilities() != null && !model.getCapabilities().isEmpty()) {
            capabilityList = Arrays.asList(model.getCapabilities().split(","));
        }
        
        return AiModelDTO.builder()
                .id(model.getId())
                .modelName(model.getModelName())
                .displayName(model.getDisplayName())
                .pricePer10kChars(model.getPricePer10kChars())
                .serviceCount(model.getServiceCount())
                .serviceDescription(model.getServiceDescription())
                .capabilities(capabilityList)
                .provider(model.getProvider())
                .maxContextLength(model.getMaxContextLength())
                .enabled(model.getEnabled())
                .build();
    }
}
