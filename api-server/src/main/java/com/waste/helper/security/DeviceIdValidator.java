package com.waste.helper.security;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.regex.Pattern;
import org.springframework.stereotype.Component;

/**
 * 디바이스 ID 검증 및 브라우저 핑거프린트 해시 생성.
 * 외부 라이브러리 없이 JDK 표준 라이브러리만 사용한다.
 */
@Component
public class DeviceIdValidator {

    // UUID v4 형식 (버전 니블이 '4'로 고정)
    private static final Pattern UUID_V4_PATTERN = Pattern.compile(
        "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    );

    public boolean isValid(String deviceId) {
        if (deviceId == null) {
            return false;
        }
        return UUID_V4_PATTERN.matcher(deviceId.toLowerCase()).matches();
    }

    /**
     * User-Agent + 해상도 + 타임존을 결합하여 SHA-256 핑거프린트 해시를 생성한다.
     * 동일 브라우저 환경에서의 재방문 식별에 활용한다.
     */
    public String generateFingerprintHash(String userAgent, String screenResolution, String timezone) {
        String data = userAgent + "|" + screenResolution + "|" + timezone;
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(data.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hash);
        } catch (NoSuchAlgorithmException e) {
            // SHA-256은 모든 JDK에서 사용 가능하므로 발생하지 않아야 함
            throw new IllegalStateException("SHA-256 algorithm not available", e);
        }
    }
}
