package com.waste.helper.web.rest;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

/**
 * AuthResource 통합 테스트.
 * 게스트 토큰 발급 API의 정상/비정상 케이스를 검증한다.
 */
@SpringBootTest
@AutoConfigureMockMvc
class AuthResourceTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createGuestToken_withValidDeviceId_returnsToken() throws Exception {
        mockMvc
            .perform(
                post("/api/v1/auth/guest")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("{\"deviceId\":\"550e8400-e29b-41d4-a716-446655440000\"}")
            )
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.token").isNotEmpty());
    }

    @Test
    void createGuestToken_withInvalidDeviceId_returns400() throws Exception {
        mockMvc
            .perform(
                post("/api/v1/auth/guest")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("{\"deviceId\":\"invalid-device-id\"}")
            )
            .andExpect(status().isBadRequest());
    }

    @Test
    void createGuestToken_withNullDeviceId_returns400() throws Exception {
        mockMvc
            .perform(
                post("/api/v1/auth/guest")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("{\"deviceId\":null}")
            )
            .andExpect(status().isBadRequest());
    }

    @Test
    void createGuestToken_withEmptyBody_returns400() throws Exception {
        mockMvc
            .perform(post("/api/v1/auth/guest").contentType(MediaType.APPLICATION_JSON).content("{}"))
            .andExpect(status().isBadRequest());
    }
}
