<?php
// moe_supermix_licensing.php — Domain
// Layer: Domain — Supermix Studio Licensing
// Inspired by: Supermix (Monorepo desktop app)

namespace Omni\Domain\MoE;

class SupermixLicense {
    private string $licenseKey;
    private string $ownerEmail;
    private bool $isActive;
    private int $expiresAt;

    public function __construct(string $licenseKey, string $email, int $durationDays) {
        $this->licenseKey = $licenseKey;
        $this->ownerEmail = $email;
        $this->isActive = true;
        // Domain Logic: Unix timestamp expiration
        $this->expiresAt = time() + ($durationDays * 86400); 
    }

    public function isValid(): bool {
        if (!$this->isActive) {
            return false;
        }
        if (time() > $this->expiresAt) {
            $this->isActive = false; // Auto-revoke on expire
            return false;
        }
        return true;
    }

    public function revoke(): void {
        $this->isActive = false;
    }

    public function getMetadata(): array {
        return [
            'license' => $this->licenseKey,
            'owner' => $this->ownerEmail,
            'status' => $this->isValid() ? 'ACTIVE' : 'EXPIRED',
            'expires_timestamp' => $this->expiresAt
        ];
    }
}
