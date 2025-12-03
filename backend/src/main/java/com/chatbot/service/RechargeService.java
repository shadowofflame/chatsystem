package com.chatbot.service;

import com.chatbot.dto.RechargeOrderDTO;
import com.chatbot.entity.RechargeOrder;
import com.chatbot.entity.User;
import com.chatbot.repository.RechargeOrderRepository;
import com.chatbot.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class RechargeService {
    
    private final RechargeOrderRepository rechargeOrderRepository;
    private final UserRepository userRepository;
    
    // 存储订单过期回调（用于通知前端）
    private final ConcurrentHashMap<String, Consumer<RechargeOrder>> expirationCallbacks = new ConcurrentHashMap<>();
    
    // 存储已过期需要通知的订单
    private final ConcurrentHashMap<String, RechargeOrder> expiredOrders = new ConcurrentHashMap<>();
    
    /**
     * 创建充值订单
     */
    @Transactional
    public RechargeOrderDTO createOrder(String username, BigDecimal amount) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        // 检查是否有未完成的订单
        Optional<RechargeOrder> pendingOrder = rechargeOrderRepository.findByUserAndStatus(user, RechargeOrder.OrderStatus.PENDING);
        if (pendingOrder.isPresent()) {
            RechargeOrder order = pendingOrder.get();
            // 如果已过期，标记为过期
            if (order.getExpireTime().isBefore(LocalDateTime.now())) {
                order.setStatus(RechargeOrder.OrderStatus.EXPIRED);
                order.setExpiredAt(LocalDateTime.now());
                rechargeOrderRepository.save(order);
            } else {
                throw new RuntimeException("您有一个待支付的订单，请先完成或等待过期");
            }
        }
        
        // 生成订单号
        String orderNo = generateOrderNo();
        
        RechargeOrder order = RechargeOrder.builder()
                .orderNo(orderNo)
                .user(user)
                .amount(amount)
                .status(RechargeOrder.OrderStatus.PENDING)
                .build();
        
        order = rechargeOrderRepository.save(order);
        log.info("创建充值订单: user={}, orderNo={}, amount={}", username, orderNo, amount);
        
        return convertToDTO(order);
    }
    
    /**
     * 确认支付（模拟支付成功）
     */
    @Transactional
    public RechargeOrderDTO confirmPayment(String username, String orderNo) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        RechargeOrder order = rechargeOrderRepository.findByOrderNoAndUser(orderNo, user)
                .orElseThrow(() -> new RuntimeException("订单不存在"));
        
        if (order.getStatus() != RechargeOrder.OrderStatus.PENDING) {
            throw new RuntimeException("订单状态不正确: " + getStatusText(order.getStatus()));
        }
        
        // 检查是否过期
        if (order.getExpireTime().isBefore(LocalDateTime.now())) {
            order.setStatus(RechargeOrder.OrderStatus.EXPIRED);
            order.setExpiredAt(LocalDateTime.now());
            rechargeOrderRepository.save(order);
            throw new RuntimeException("订单已过期");
        }
        
        // 更新订单状态
        order.setStatus(RechargeOrder.OrderStatus.PAID);
        order.setPaidAt(LocalDateTime.now());
        rechargeOrderRepository.save(order);
        
        // 更新用户余额
        user.setBalance(user.getBalance().add(order.getAmount()));
        userRepository.save(user);
        
        log.info("充值成功: user={}, orderNo={}, amount={}, newBalance={}", 
                username, orderNo, order.getAmount(), user.getBalance());
        
        return convertToDTO(order);
    }
    
    /**
     * 取消订单
     */
    @Transactional
    public RechargeOrderDTO cancelOrder(String username, String orderNo) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        RechargeOrder order = rechargeOrderRepository.findByOrderNoAndUser(orderNo, user)
                .orElseThrow(() -> new RuntimeException("订单不存在"));
        
        if (order.getStatus() != RechargeOrder.OrderStatus.PENDING) {
            throw new RuntimeException("只能取消待支付的订单");
        }
        
        order.setStatus(RechargeOrder.OrderStatus.CANCELLED);
        rechargeOrderRepository.save(order);
        
        log.info("订单已取消: user={}, orderNo={}", username, orderNo);
        
        return convertToDTO(order);
    }
    
    /**
     * 获取用户余额
     */
    public BigDecimal getUserBalance(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        return user.getBalance();
    }
    
    /**
     * 获取用户的充值订单列表
     */
    public List<RechargeOrderDTO> getUserOrders(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return rechargeOrderRepository.findByUserOrderByCreatedAtDesc(user)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * 获取用户当前待支付的订单
     */
    public RechargeOrderDTO getPendingOrder(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        return rechargeOrderRepository.findByUserAndStatus(user, RechargeOrder.OrderStatus.PENDING)
                .map(order -> {
                    // 检查是否过期
                    if (order.getExpireTime().isBefore(LocalDateTime.now())) {
                        order.setStatus(RechargeOrder.OrderStatus.EXPIRED);
                        order.setExpiredAt(LocalDateTime.now());
                        rechargeOrderRepository.save(order);
                        return null;
                    }
                    return convertToDTO(order);
                })
                .orElse(null);
    }
    
    /**
     * 获取并清除已过期的订单通知
     */
    public List<RechargeOrderDTO> getAndClearExpiredNotifications(String username) {
        List<RechargeOrderDTO> expired = new ArrayList<>();
        expiredOrders.entrySet().removeIf(entry -> {
            RechargeOrder order = entry.getValue();
            if (order.getUser().getUsername().equals(username)) {
                expired.add(convertToDTO(order));
                return true;
            }
            return false;
        });
        return expired;
    }
    
    /**
     * 定时任务：检查过期订单（每30秒执行一次）
     */
    @Scheduled(fixedRate = 30000)
    @Transactional
    public void checkExpiredOrders() {
        LocalDateTime now = LocalDateTime.now();
        List<RechargeOrder> expiredOrdersList = rechargeOrderRepository.findExpiredPendingOrders(now);
        
        for (RechargeOrder order : expiredOrdersList) {
            order.setStatus(RechargeOrder.OrderStatus.EXPIRED);
            order.setExpiredAt(now);
            rechargeOrderRepository.save(order);
            
            // 添加到过期通知列表
            expiredOrders.put(order.getOrderNo(), order);
            
            log.info("订单已过期: orderNo={}, user={}", order.getOrderNo(), order.getUser().getUsername());
        }
    }
    
    /**
     * 生成订单号
     */
    private String generateOrderNo() {
        return "RC" + System.currentTimeMillis() + UUID.randomUUID().toString().substring(0, 6).toUpperCase();
    }
    
    /**
     * 转换为DTO
     */
    private RechargeOrderDTO convertToDTO(RechargeOrder order) {
        long remainingSeconds = 0;
        if (order.getStatus() == RechargeOrder.OrderStatus.PENDING) {
            remainingSeconds = ChronoUnit.SECONDS.between(LocalDateTime.now(), order.getExpireTime());
            if (remainingSeconds < 0) remainingSeconds = 0;
        }
        
        return RechargeOrderDTO.builder()
                .id(order.getId())
                .orderNo(order.getOrderNo())
                .amount(order.getAmount())
                .status(order.getStatus().name())
                .statusText(getStatusText(order.getStatus()))
                .createdAt(order.getCreatedAt())
                .paidAt(order.getPaidAt())
                .expireTime(order.getExpireTime())
                .remainingSeconds(remainingSeconds)
                .build();
    }
    
    private String getStatusText(RechargeOrder.OrderStatus status) {
        return switch (status) {
            case PENDING -> "待支付";
            case PAID -> "已支付";
            case EXPIRED -> "已过期";
            case CANCELLED -> "已取消";
        };
    }
}
