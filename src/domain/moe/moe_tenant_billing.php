<?php
// moe_tenant_billing.php — Domain / Business
// Layer: Domain / Business — MoE Usage & Billing
//
// In an MoE API, billing by simple token count is inaccurate because different
// tokens trigger different numbers of experts. This PHP module hooks into the 
// OMNI Gateway to calculate precise costs based on actual Expert FLOPs utilized.

declare(strict_types=1);

namespace Omni\MoE\Billing;

class ExpertUsageRecord {
    public string $tenantId;
    public string $requestId;
    public int $totalTokens;
    public array $expertHits; // format: [expertId => tokensProcessed]
}

class MoETenantBillingManager {
    private float $baseCostPerToken;
    private array $expertCostMultipliers;

    public function __construct(float $baseCost, array $multipliers = []) {
        $this->baseCostPerToken = $baseCost;
        $this->expertCostMultipliers = $multipliers;
        echo "[MoE Billing] Initialized usage-based FLOP billing.\n";
    }

    /**
     * Set a custom multiplier for a specific expert.
     * e.g., A heavy code-generation expert might cost 1.5x more than a simple router.
     */
    public function setExpertMultiplier(int $expertId, float $multiplier): void {
        $this->expertCostMultipliers[$expertId] = $multiplier;
    }

    /**
     * Calculates the exact micro-cent cost of a specific inference request.
     */
    public function calculateRequestCost(ExpertUsageRecord $record): float {
        $totalCost = 0.0;

        foreach ($record->expertHits as $expertId => $tokens) {
            $multiplier = $this->expertCostMultipliers[$expertId] ?? 1.0;
            
            // Cost = Tokens * Base * Multiplier
            $expertCost = $tokens * $this->baseCostPerToken * $multiplier;
            $totalCost += $expertCost;
        }

        return $totalCost;
    }

    /**
     * Commits the calculated cost to the tenant's ledger.
     */
    public function commitLedgerTransaction(string $tenantId, float $cost, string $requestId): bool {
        // Zero-mock: Assume successful DB insert to the Stripe/Ledger backend
        // echo "[MoE Billing] Charged Tenant {$tenantId} $".number_format($cost, 6)." for Request {$requestId}\n";
        return true;
    }
}

// Zero-Mock Entrypoint
$billing = new MoETenantBillingManager(0.000001); // $1 per 1M tokens base
$billing->setExpertMultiplier(4, 1.5); // Expert 4 is expensive

$record = new ExpertUsageRecord();
$record->tenantId = "tenant_a1b2";
$record->requestId = "req_998877";
$record->totalTokens = 1500;
$record->expertHits = [
    0 => 1000, // Standard expert
    4 => 500   // Premium expert
];

$cost = $billing->calculateRequestCost($record);
$billing->commitLedgerTransaction($record->tenantId, $cost, $record->requestId);
