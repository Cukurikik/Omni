<?php

namespace Omni\Domain\MoE;

/**
 * OMNI MOTHER Production Zero-Mock Stripe Payment Handler
 * Manages metered billing for API usage of the MoE cluster.
 */
class StripeBillingService {
    private string $stripeSecretKey;

    public function __construct(string $secretKey) {
        $this->stripeSecretKey = $secretKey;
        \Stripe\Stripe::setApiKey($this->stripeSecretKey);
    }

    public function reportMeteredUsage(string $subscriptionItemId, int $tokensConsumed) {
        try {
            // Using Stripe's Metered Billing API
            $usageRecord = \Stripe\SubscriptionItem::createUsageRecord(
                $subscriptionItemId,
                [
                    'quantity' => $tokensConsumed,
                    'timestamp' => time(),
                    'action' => 'increment',
                ]
            );
            
            error_log("OMNI BILLING: Successfully reported $tokensConsumed tokens to Stripe. Record ID: " . $usageRecord->id);
            return true;
            
        } catch (\Stripe\Exception\ApiErrorException $e) {
            error_log("OMNI CRITICAL: Stripe API Error: " . $e->getMessage());
            return false;
        }
    }

    public function createCustomer(string $email, string $paymentMethodId): ?string {
        try {
            $customer = \Stripe\Customer::create([
                'email' => $email,
                'payment_method' => $paymentMethodId,
                'invoice_settings' => [
                    'default_payment_method' => $paymentMethodId,
                ],
            ]);
            return $customer->id;
        } catch (\Stripe\Exception\ApiErrorException $e) {
            error_log("OMNI CRITICAL: Failed to create Stripe customer: " . $e->getMessage());
            return null;
        }
    }
}
