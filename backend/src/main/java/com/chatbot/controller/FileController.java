package com.chatbot.controller;

import com.chatbot.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {
    
    private final WebClient pythonAgentWebClient;
    
    /**
     * 上传文件
     */
    @PostMapping("/upload")
    public ResponseEntity<ApiResponse<Map<String, Object>>> uploadFile(
            @RequestParam("file") MultipartFile file,
            Authentication authentication
    ) {
        String username = authentication.getName();
        log.info("User {} uploading file: {}, size: {} bytes", 
                username, file.getOriginalFilename(), file.getSize());
        
        try {
            // 构建 multipart 请求发送到 Python Agent
            MultipartBodyBuilder builder = new MultipartBodyBuilder();
            builder.part("file", new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            }).contentType(MediaType.APPLICATION_OCTET_STREAM);
            
            Map<String, Object> response = pythonAgentWebClient.post()
                    .uri("/api/upload")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(builder.build()))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            if (response != null && Boolean.TRUE.equals(response.get("success"))) {
                log.info("File uploaded successfully: {}", response.get("filename"));
                return ResponseEntity.ok(ApiResponse.success(response));
            } else {
                String error = response != null ? (String) response.get("error") : "Upload failed";
                return ResponseEntity.ok(ApiResponse.error(error));
            }
            
        } catch (Exception e) {
            log.error("Error uploading file", e);
            return ResponseEntity.ok(ApiResponse.error("文件上传失败: " + e.getMessage()));
        }
    }
    
    /**
     * 分析已上传的文件
     */
    @PostMapping("/analyze")
    public ResponseEntity<ApiResponse<Map<String, Object>>> analyzeFile(
            @RequestBody Map<String, String> request,
            Authentication authentication
    ) {
        String username = authentication.getName();
        String filepath = request.get("filepath");
        String question = request.getOrDefault("question", "请分析这个文件的内容");
        
        log.info("User {} analyzing file: {}", username, filepath);
        
        try {
            Map<String, Object> response = pythonAgentWebClient.post()
                    .uri("/api/analyze-file")
                    .bodyValue(Map.of(
                            "filepath", filepath,
                            "question", question
                    ))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            if (response != null && Boolean.TRUE.equals(response.get("success"))) {
                return ResponseEntity.ok(ApiResponse.success(response));
            } else {
                String error = response != null ? (String) response.get("error") : "Analysis failed";
                return ResponseEntity.ok(ApiResponse.error(error));
            }
            
        } catch (Exception e) {
            log.error("Error analyzing file", e);
            return ResponseEntity.ok(ApiResponse.error("文件分析失败: " + e.getMessage()));
        }
    }
    
    /**
     * 列出已上传的文件
     */
    @GetMapping("/list")
    public ResponseEntity<ApiResponse<Map<String, Object>>> listFiles(
            Authentication authentication
    ) {
        String username = authentication.getName();
        log.info("User {} listing uploaded files", username);
        
        try {
            Map<String, Object> response = pythonAgentWebClient.get()
                    .uri("/api/files")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            if (response != null && Boolean.TRUE.equals(response.get("success"))) {
                return ResponseEntity.ok(ApiResponse.success(response));
            } else {
                String error = response != null ? (String) response.get("error") : "Failed to list files";
                return ResponseEntity.ok(ApiResponse.error(error));
            }
            
        } catch (Exception e) {
            log.error("Error listing files", e);
            return ResponseEntity.ok(ApiResponse.error("获取文件列表失败: " + e.getMessage()));
        }
    }
}
