// OMNI Engine — JWT RSA Verifier
// Layer: Security
// Implements: RSA asymmetric signature validation for JSON Web Tokens

package omni.security;

import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;

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

public class JwtRsaVerifier {
    
    public OmniResult<Boolean> verifyRs256(String token, String publicKeyBase64) {
        if (token == null || publicKeyBase64 == null) {
            return OmniResult.fail("Token and public key required");
        }

        String[] parts = token.split("\\.");
        if (parts.length != 3) {
            return OmniResult.fail("Invalid JWT format. Must have 3 parts.");
        }

        try {
            // Reconstruct Public Key
            byte[] keyBytes = Base64.getDecoder().decode(publicKeyBase64);
            X509EncodedKeySpec spec = new X509EncodedKeySpec(keyBytes);
            KeyFactory kf = KeyFactory.getInstance("RSA");
            PublicKey publicKey = kf.generatePublic(spec);

            // Payload to verify
            String headerAndPayload = parts[0] + "." + parts[1];
            byte[] signatureBytes = Base64.getUrlDecoder().decode(parts[2]);

            // Verify RSA Signature
            Signature sig = Signature.getInstance("SHA256withRSA");
            sig.initVerify(publicKey);
            sig.update(headerAndPayload.getBytes("UTF-8"));

            boolean isValid = sig.verify(signatureBytes);
            if (isValid) {
                return OmniResult.ok(true);
            } else {
                return OmniResult.fail("Invalid RSA signature");
            }

        } catch (Exception e) {
            return OmniResult.fail("Verification exception: " + e.getMessage());
        }
    }
}
