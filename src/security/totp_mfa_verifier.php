<?php

declare(strict_types=1);

namespace Omni\Security\Auth;

final class TotpResult {
    private function __construct(
        public readonly bool $isValid,
        public readonly ?string $error
    ) {}

    public static function valid(): self {
        return new self(true, null);
    }

    public static function invalid(string $reason): self {
        return new self(false, $reason);
    }
}

/**
 * Omni Mother System - Security Layer
 * Time-based One-Time Password (TOTP) MFA Validator (RFC 6238).
 * Enforces strict temporal drift windows and constant-time comparisons.
 */
final class TotpMfaVerifier {
    private const WINDOW_SECONDS = 30;
    
    // Allows 1 window before and 1 window after to account for clock drift
    private const ALLOWED_DRIFT_WINDOWS = 1; 

    /**
     * Verifies the provided 6-digit code against the Base32 secret.
     */
    public function verify(string $base32Secret, string $code): TotpResult {
        if (!preg_match('/^[0-9]{6}$/', $code)) {
            return TotpResult::invalid("Code must be strictly 6 digits");
        }

        if (empty(trim($base32Secret))) {
             return TotpResult::invalid("Secret cannot be empty");
        }

        try {
            $secretBytes = $this->decodeBase32($base32Secret);
        } catch (\Exception $e) {
            return TotpResult::invalid("Invalid Base32 secret encoding");
        }

        $currentTime = time();
        $currentWindow = (int) floor($currentTime / self::WINDOW_SECONDS);

        // Check current window and drift windows securely
        for ($i = -self::ALLOWED_DRIFT_WINDOWS; $i <= self::ALLOWED_DRIFT_WINDOWS; $i++) {
            $computedCode = $this->generateTotpCode($secretBytes, $currentWindow + $i);
            
            if (hash_equals($computedCode, $code)) {
                return TotpResult::valid();
            }
        }

        return TotpResult::invalid("Code invalid or expired");
    }

    private function generateTotpCode(string $secretBytes, int $timeWindow): string {
        // Convert time window to 8-byte big-endian binary string
        $timeBytes = pack('J', $timeWindow);

        // HMAC-SHA1 as per RFC
        $hmac = hash_hmac('sha1', $timeBytes, $secretBytes, true);

        // Dynamic Truncation
        $offset = ord($hmac[19]) & 0x0F;
        
        $value = (
            ((ord($hmac[$offset + 0]) & 0x7F) << 24) |
            ((ord($hmac[$offset + 1]) & 0xFF) << 16) |
            ((ord($hmac[$offset + 2]) & 0xFF) << 8) |
            (ord($hmac[$offset + 3]) & 0xFF)
        );

        // Reduce to 6 digits
        $otp = $value % 1000000;
        
        return str_pad((string)$otp, 6, '0', STR_PAD_LEFT);
    }

    private function decodeBase32(string $base32): string {
        $base32chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        $base32charsFlipped = array_flip(str_split($base32chars));
        
        $base32 = strtoupper(str_replace('=', '', $base32));
        $output = '';
        $v = 0;
        $vbits = 0;
        
        for ($i = 0, $j = strlen($base32); $i < $j; $i++) {
            if (!isset($base32charsFlipped[$base32[$i]])) {
                throw new \Exception("Invalid Base32 character");
            }
            $v = ($v << 5) | $base32charsFlipped[$base32[$i]];
            $vbits += 5;
            if ($vbits >= 8) {
                $vbits -= 8;
                $output .= chr(($v >> $vbits) & 0xFF);
            }
        }
        return $output;
    }
}
