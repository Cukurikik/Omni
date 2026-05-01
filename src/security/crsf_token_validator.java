// OMNI Engine — CSRF Token Validator
// Layer: Security
// Implements: Cross-Site Request Forgery token generation and validation

package omni.security;

import java.security.SecureRandom;
import java.util.Base64;
import java.security.MessageDigest;

public class OmniResult<T> {
    public final T value;
    public final String error;
    public final boolean isOk;

    private OmniResult(T value, String error, boolean isOk) {
        this.value = value;
        this.error = error;
        this.isOk = isOk;
    }

    public static <T> OmniResult<T> ok(T value) {
        return new OmniResult<>(value, null, true);
    }

    public static <T> OmniResult<T> fail(String error) {
        return new OmniResult<>(null, error, false);
    }
}

public class CsrfTokenManager {
    private static final SecureRandom secureRandom = new SecureRandom();

    public OmniResult<String> generateToken() {
        byte[] tokenBytes = new byte[32];
        secureRandom.nextBytes(tokenBytes);
        String token = Base64.getUrlEncoder().withoutPadding().encodeToString(tokenBytes);
        return OmniResult.ok(token);
    }

    public OmniResult<Boolean> validateToken(String sessionToken, String requestToken) {
        if (sessionToken == null || requestToken == null) {
            return OmniResult.fail("Tokens cannot be null");
        }

        if (sessionToken.length() < 32 || requestToken.length() < 32) {
            return OmniResult.fail("Tokens are too short");
        }

        // Constant-time comparison
        boolean isValid = MessageDigest.isEqual(
            sessionToken.getBytes(java.nio.charset.StandardCharsets.UTF_8), 
            requestToken.getBytes(java.nio.charset.StandardCharsets.UTF_8)
        );

        if (isValid) {
            return OmniResult.ok(true);
        } else {
            return OmniResult.fail("CSRF Token mismatch");
        }
    }
}
