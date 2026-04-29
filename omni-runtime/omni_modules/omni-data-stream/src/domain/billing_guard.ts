/**
 * =======================================================================
 * OMNI REALTIME TELEMETRY HUB: BILLING GUARD (Business Layer)
 * =======================================================================
 * Automated monetization engine. Locks WebSocket gateway (Paywall) when
 * developers exceed free connection limits, triggering upgrade to
 * VELOCITY_PRO subscription at $49/month in realtime.
 */

// Redis connection interface — resolved at OMNI runtime
interface RedisConnection {
  get(key: string): Promise<any>;
  set(key: string, value: any): Promise<void>;
  increment(key: string): Promise<number>;
}

// Stripe billing interface — resolved at OMNI runtime
interface StripeBilling {
  createUpgradeSession(opts: {
    priceId: string;
    customerEmail: string;
  }): string;
}

// Factory functions — injected by OMNI runtime DI container
declare function createRedisConnection(url: string): RedisConnection;
declare function createStripeBilling(apiKey: string): StripeBilling;

export interface DeveloperAccount {
  apiKey: string;
  subscriptionId: string | null;
  tier: "SINGULARITY_FREE" | "VELOCITY_PRO";
  currentConnections: number;
}

export class RuntimeBillingGuard {
  private db: RedisConnection;
  private stripe: StripeBilling;

  // Hard limit per business tier (converts technical load into revenue)
  private readonly FREE_CONNECTION_LIMIT = 10000;
  private readonly PRO_CONNECTION_LIMIT = 150000;

  constructor() {
    this.db = createRedisConnection("redis://omni-internal-cache:6379");
    this.stripe = createStripeBilling("sk_live_omni_secure_stripe_key");
  }

  /**
   * Executed via FFI call on every frontend WebSocket handshake.
   */
  public async interceptConnection(apiKey: string): Promise<boolean> {
    // Check Developer Account in Redis cache
    const account: DeveloperAccount = await this.db.get(`account:${apiKey}`);

    if (!account) {
      console.error(
        `[BILLING GUARD] Connection rejected. API Key not found: ${apiKey}`,
      );
      return false;
    }

    // Tier-based pricing limits (Zero-Touch Monetization)
    if (account.tier === "SINGULARITY_FREE") {
      if (account.currentConnections >= this.FREE_CONNECTION_LIMIT) {
        console.warn(
          `[BILLING PAYWALL] Client (Key: ${apiKey}) exceeded 10,000 sockets.`,
        );
        console.warn(
          `[BILLING PAYWALL] Returning HTTP 402 Payment Required to API Gateway.`,
        );

        // Auto-trigger Stripe $49 invoice to developer
        this.triggerAutomatedUpsell(account);
        return false;
      }
    }

    if (account.tier === "VELOCITY_PRO") {
      // VIP $49 subscribers get higher limits
      if (account.currentConnections >= this.PRO_CONNECTION_LIMIT) {
        return false;
      }
    }

    // Increment realtime counter in memory cache
    await this.db.increment(`account:${apiKey}:connections`);
    return true;
  }

  private triggerAutomatedUpsell(account: DeveloperAccount): void {
    // Create new Checkout session via OMNI-Stripe
    const checkoutUrl = this.stripe.createUpgradeSession({
      priceId: "price_velocity_49_usd_monthly",
      customerEmail: `dev_${account.apiKey}@developer.com`,
    });

    console.log(
      `[SALES ENGINE] Autopilot triggered! Invoice sent to developer.`,
    );
    console.log(`[SALES ENGINE] Payment URL: ${checkoutUrl}`);
  }
}
