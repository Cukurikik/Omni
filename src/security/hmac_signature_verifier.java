// OMNI Engine — HMAC Signature Verifier
// Layer: Security
// Implements: Validation of webhook signatures

package omni.security;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.util.Formatter;

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

public class HmacSignatureVerifier {
    
    private static final String HMAC_SHA256 = "HmacSHA256";

    public OmniResult<Boolean> verifySignature(String payload, String secret, String expectedSignature) {
        if (payload == null || secret == null || expectedSignature == null) {
            return OmniResult.fail("Parameters cannot be null");
        }

        try {
            SecretKeySpec secretKeySpec = new SecretKeySpec(secret.getBytes("UTF-8"), HMAC_SHA256);
            Mac mac = Mac.getInstance(HMAC_SHA256);
            mac.init(secretKeySpec);
            
            byte[] hmacBytes = mac.doFinal(payload.getBytes("UTF-8"));
            String computedSignature = bytesToHex(hmacBytes);
            
            // Constant-time comparison to prevent timing attacks
            boolean isValid = MessageDigest.isEqual(
                computedSignature.getBytes("UTF-8"), 
                expectedSignature.getBytes("UTF-8")
            );

            if (isValid) {
                return OmniResult.ok(true);
            } else {
                return OmniResult.fail("Signature mismatch");
            }

        } catch (Exception e) {
            return OmniResult.fail("Cryptography error: " + e.getMessage());
        }
    }

    private String bytesToHex(byte[] bytes) {
        Formatter formatter = new Formatter();
        for (byte b : bytes) {
            formatter.format("%02x", b);
        }
        String hex = formatter.toString();
        formatter.close();
        return hex;
    }
}
