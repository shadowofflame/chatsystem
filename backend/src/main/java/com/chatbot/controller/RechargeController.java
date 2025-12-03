package com.chatbot.controller;

import com.chatbot.dto.ApiResponse;
import com.chatbot.dto.RechargeOrderDTO;
import com.chatbot.dto.RechargeRequest;
import com.chatbot.service.RechargeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/recharge")
@RequiredArgsConstructor
public class RechargeController {
    
    private final RechargeService rechargeService;
    
    /**
     * 创建充值订单
     */
    @PostMapping("/create")
    public ResponseEntity<ApiResponse<RechargeOrderDTO>> createOrder(
            @Valid @RequestBody RechargeRequest request,
            Authentication authentication
    ) {
        try {
            String username = authentication.getName();
            RechargeOrderDTO order = rechargeService.createOrder(username, request.getAmount());
            return ResponseEntity.ok(ApiResponse.success(order));
        } catch (Exception e) {
            log.error("创建订单失败", e);
            return ResponseEntity.ok(ApiResponse.error(e.getMessage()));
        }
    }
    
    /**
     * 确认支付
     */
    @PostMapping("/confirm/{orderNo}")
    public ResponseEntity<ApiResponse<RechargeOrderDTO>> confirmPayment(
            @PathVariable String orderNo,
            Authentication authentication
    ) {
        try {
            String username = authentication.getName();
            RechargeOrderDTO order = rechargeService.confirmPayment(username, orderNo);
            return ResponseEntity.ok(ApiResponse.success("充值成功", order));
        } catch (Exception e) {
            log.error("确认支付失败", e);
            return ResponseEntity.ok(ApiResponse.error(e.getMessage()));
        }
    }
    
    /**
     * 取消订单
     */
    @PostMapping("/cancel/{orderNo}")
    public ResponseEntity<ApiResponse<RechargeOrderDTO>> cancelOrder(
            @PathVariable String orderNo,
            Authentication authentication
    ) {
        try {
            String username = authentication.getName();
            RechargeOrderDTO order = rechargeService.cancelOrder(username, orderNo);
            return ResponseEntity.ok(ApiResponse.success("订单已取消", order));
        } catch (Exception e) {
            log.error("取消订单失败", e);
            return ResponseEntity.ok(ApiResponse.error(e.getMessage()));
        }
    }
    
    /**
     * 获取用户余额
     */
    @GetMapping("/balance")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getBalance(Authentication authentication) {
        String username = authentication.getName();
        BigDecimal balance = rechargeService.getUserBalance(username);
        return ResponseEntity.ok(ApiResponse.success(Map.of("balance", balance)));
    }
    
    /**
     * 获取充值订单列表
     */
    @GetMapping("/orders")
    public ResponseEntity<ApiResponse<List<RechargeOrderDTO>>> getOrders(Authentication authentication) {
        String username = authentication.getName();
        List<RechargeOrderDTO> orders = rechargeService.getUserOrders(username);
        return ResponseEntity.ok(ApiResponse.success(orders));
    }
    
    /**
     * 获取当前待支付订单
     */
    @GetMapping("/pending")
    public ResponseEntity<ApiResponse<RechargeOrderDTO>> getPendingOrder(Authentication authentication) {
        String username = authentication.getName();
        RechargeOrderDTO order = rechargeService.getPendingOrder(username);
        return ResponseEntity.ok(ApiResponse.success(order));
    }
    
    /**
     * 获取过期订单通知（轮询接口）
     */
    @GetMapping("/expired-notifications")
    public ResponseEntity<ApiResponse<List<RechargeOrderDTO>>> getExpiredNotifications(Authentication authentication) {
        String username = authentication.getName();
        List<RechargeOrderDTO> expired = rechargeService.getAndClearExpiredNotifications(username);
        return ResponseEntity.ok(ApiResponse.success(expired));
    }
}
