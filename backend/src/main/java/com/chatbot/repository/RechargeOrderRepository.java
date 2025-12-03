package com.chatbot.repository;

import com.chatbot.entity.RechargeOrder;
import com.chatbot.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface RechargeOrderRepository extends JpaRepository<RechargeOrder, Long> {
    
    Optional<RechargeOrder> findByOrderNo(String orderNo);
    
    Optional<RechargeOrder> findByOrderNoAndUser(String orderNo, User user);
    
    List<RechargeOrder> findByUserOrderByCreatedAtDesc(User user);
    
    List<RechargeOrder> findByUserAndStatusOrderByCreatedAtDesc(User user, RechargeOrder.OrderStatus status);
    
    /**
     * 查找所有待支付且已过期的订单
     */
    @Query("SELECT o FROM RechargeOrder o WHERE o.status = 'PENDING' AND o.expireTime < :now")
    List<RechargeOrder> findExpiredPendingOrders(@Param("now") LocalDateTime now);
    
    /**
     * 查找用户当前待支付的订单
     */
    Optional<RechargeOrder> findByUserAndStatus(User user, RechargeOrder.OrderStatus status);
    
    /**
     * 统计用户成功充值的总金额
     */
    @Query("SELECT COALESCE(SUM(o.amount), 0) FROM RechargeOrder o WHERE o.user = :user AND o.status = 'PAID'")
    java.math.BigDecimal getTotalRechargedAmount(@Param("user") User user);
}
