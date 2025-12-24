package com.chatbot.config;

import io.netty.channel.ChannelOption;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.ExchangeStrategies;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;

@Configuration
public class WebClientConfig {
    
    @Value("${python-agent.base-url}")
    private String pythonAgentBaseUrl;
    
    @Value("${python-agent.timeout}")
    private int timeout;
    
    @Bean
    public WebClient pythonAgentWebClient() {
        HttpClient httpClient = HttpClient.create()
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 10000)
                .responseTimeout(Duration.ofMillis(timeout))
                // 禁用响应压缩以支持流式传输
                .compress(false)
                // 禁用连接池的 keep-alive 超时以支持长连接 SSE
                .keepAlive(true);
        
        // 配置编解码器 - 增大内存缓冲区但启用流式处理
        ExchangeStrategies strategies = ExchangeStrategies.builder()
                .codecs(configurer -> {
                    configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024); // 10MB
                })
                .build();
        
        return WebClient.builder()
                .baseUrl(pythonAgentBaseUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .exchangeStrategies(strategies)
                .build();
    }
}
