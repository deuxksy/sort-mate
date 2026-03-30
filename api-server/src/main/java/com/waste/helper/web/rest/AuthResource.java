package com.waste.helper.web.rest;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.waste.helper.security.DeviceIdValidator;
import com.waste.helper.security.GuestTokenProvider;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 게스트 인증 엔드포인트.
 * 인증 없이 접근 가능하며, 유효한 deviceId를 제공하면 JWT 토큰을 발급한다.
 */
@RestController
@RequestMapping("/api/v1/auth")
public class AuthResource {

    private final GuestTokenProvider guestTokenProvider;
    private final DeviceIdValidator deviceIdValidator;

    public AuthResource(GuestTokenProvider guestTokenProvider, DeviceIdValidator deviceIdValidator) {
        this.guestTokenProvider = guestTokenProvider;
        this.deviceIdValidator = deviceIdValidator;
    }

    @PostMapping("/guest")
    public ResponseEntity<GuestTokenResponse> createGuestToken(@RequestBody GuestTokenRequest request) {
        if (!deviceIdValidator.isValid(request.deviceId())) {
            return ResponseEntity.badRequest().build();
        }

        String token = guestTokenProvider.createToken(request.deviceId());
        return ResponseEntity.ok(new GuestTokenResponse(token));
    }

    public record GuestTokenRequest(String deviceId) {}

    public static class GuestTokenResponse {

        private String token;

        public GuestTokenResponse(String token) {
            this.token = token;
        }

        @JsonProperty("token")
        public String getToken() {
            return token;
        }

        public void setToken(String token) {
            this.token = token;
        }
    }
}
