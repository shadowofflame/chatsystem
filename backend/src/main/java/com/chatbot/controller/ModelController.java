package com.chatbot.controller;

import com.chatbot.dto.AiModelDTO;
import com.chatbot.dto.ApiResponse;
import com.chatbot.service.AiModelService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/models")
@RequiredArgsConstructor
public class ModelController {
    
    private final AiModelService aiModelService;
    
    /**
     * 获取所有模型（包括禁用的）
     */
    @GetMapping
    public ResponseEntity<ApiResponse<List<AiModelDTO>>> getAllModels() {
        List<AiModelDTO> models = aiModelService.getAllModels();
        return ResponseEntity.ok(ApiResponse.success(models));
    }
    
    /**
     * 获取所有启用的模型
     */
    @GetMapping("/enabled")
    public ResponseEntity<ApiResponse<List<AiModelDTO>>> getEnabledModels() {
        List<AiModelDTO> models = aiModelService.getEnabledModels();
        return ResponseEntity.ok(ApiResponse.success(models));
    }
    
    /**
     * 获取指定模型详情
     */
    @GetMapping("/{modelName}")
    public ResponseEntity<ApiResponse<AiModelDTO>> getModelByName(@PathVariable String modelName) {
        AiModelDTO model = aiModelService.getModelByName(modelName);
        if (model == null) {
            return ResponseEntity.ok(ApiResponse.error("模型不存在"));
        }
        return ResponseEntity.ok(ApiResponse.success(model));
    }
}
