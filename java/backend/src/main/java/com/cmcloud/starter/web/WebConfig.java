package com.cmcloud.starter.web;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * CORS exists only for local development, where Vite serves the UI on :5173 and
 * Spring serves the API on :11001. In production nginx serves both from one
 * origin, so the allowed list is empty and no CORS headers are sent at all.
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${starter.cors.allowed-origins:}")
    private String[] allowedOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        if (allowedOrigins == null || allowedOrigins.length == 0) {
            return;
        }
        registry.addMapping("/api/**")
                .allowedOrigins(allowedOrigins)
                .allowedMethods("GET", "POST", "DELETE");
    }
}
