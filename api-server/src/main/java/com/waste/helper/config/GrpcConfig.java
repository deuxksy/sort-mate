package com.waste.helper.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

@Configuration
public class GrpcConfig {

    @Bean
    public CircuitBreaker vlmCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .waitDurationInOpenState(Duration.ofSeconds(30))
            .permittedNumberOfCallsInHalfOpenState(3)
            .slidingWindowSize(10)
            .build();

        return CircuitBreaker.of("vlm-service", config);
    }

    @Bean
    public Retry vlmRetry() {
        RetryConfig config = RetryConfig.custom()
            .maxAttempts(2)
            .waitDuration(Duration.ofSeconds(1))
            .build();

        return Retry.of("vlm-service", config);
    }
}