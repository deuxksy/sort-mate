package com.waste.helper.security;

import static com.waste.helper.security.SecurityUtils.JWT_ALGORITHM;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.stereotype.Component;

/**
 * 게스트 사용자를 위한 JWT 토큰 발급.
 * 기존 JHipster JWT 인프라(JwtEncoder, base64-secret)를 재사용하여
 * 일반 사용자 토큰과 동일한 서명 및 검증 체인을 따른다.
 */
@Component
public class GuestTokenProvider {

    private final JwtEncoder jwtEncoder;
    private final long tokenValiditySeconds;

    public GuestTokenProvider(
        JwtEncoder jwtEncoder,
        @Value("${jhipster.security.authentication.jwt.token-validity-in-seconds:86400}") long tokenValiditySeconds
    ) {
        this.jwtEncoder = jwtEncoder;
        this.tokenValiditySeconds = tokenValiditySeconds;
    }

    public String createToken(String deviceId) {
        Instant now = Instant.now();
        Instant expiry = now.plus(tokenValiditySeconds, ChronoUnit.SECONDS);

        JwtClaimsSet claims = JwtClaimsSet.builder()
            .issuedAt(now)
            .expiresAt(expiry)
            .subject(deviceId)
            .claim(SecurityUtils.AUTHORITIES_CLAIM, AuthoritiesConstants.GUEST)
            .claim("role", "GUEST")
            .build();

        JwsHeader header = JwsHeader.with(JWT_ALGORITHM).build();
        return jwtEncoder.encode(JwtEncoderParameters.from(header, claims)).getTokenValue();
    }
}
