package com.chatbot.repository;

import com.chatbot.entity.AiModel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AiModelRepository extends JpaRepository<AiModel, Long> {
    
    /**
     * 根据模型名称查找
     */
    Optional<AiModel> findByModelName(String modelName);
    
    /**
     * 查找所有启用的模型，按排序权重排序
     */
    List<AiModel> findByEnabledTrueOrderBySortOrderAsc();
    
    /**
     * 查找所有模型，按排序权重排序
     */
    List<AiModel> findAllByOrderBySortOrderAsc();
    
    /**
     * 增加模型服务计数
     */
    @Modifying
    @Query("UPDATE AiModel m SET m.serviceCount = m.serviceCount + 1 WHERE m.modelName = :modelName")
    void incrementServiceCount(@Param("modelName") String modelName);
}
