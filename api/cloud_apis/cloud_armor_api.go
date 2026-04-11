package cloud_apis

import (
	"context"
	"fmt"
	"log"

	compute "cloud.google.com/go/compute/apiv1"
	"cloud.google.com/go/compute/apiv1/computepb"
	"google.golang.org/protobuf/proto"
)

// ==========================================
// 🛡️ OMNI CLOUD ARMOR — ENTERPRISE WAF & DDOS SHIELD
// ==========================================
// Cloud Armor memberikan perlindungan WAF (Web Application Firewall)
// dan DDoS di layer 3/4/7 di atas Google's global edge network.
//
// Melengkapi OMNI eBPF Sentinel (Ring-0 XDP) untuk pertahanan berlapis:
//   Layer 3/4 DDoS → Google Cloud Armor (edge)
//   Layer 7 WAF    → Cloud Armor Security Policies
//   Ring-0 NIC     → OMNI eBPF Sentinel (XDP_DROP)
//
// Target ARR: +$40.000 via Enterprise Security Tier
// ==========================================

// CloudArmorBridge menyediakan akses ke Cloud Armor Security Policies
type CloudArmorBridge struct {
	projectID string
}

// NewCloudArmorBridge membuat bridge baru
func NewCloudArmorBridge(projectID string) *CloudArmorBridge {
	return &CloudArmorBridge{projectID: projectID}
}

// CreateSecurityPolicy membuat kebijakan keamanan baru
func (c *CloudArmorBridge) CreateSecurityPolicy(ctx context.Context, policyName, description string) error {
	client, err := compute.NewSecurityPoliciesRESTClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: gagal membuat security policies client: %v", err)
	}
	defer client.Close()

	policy := &computepb.SecurityPolicy{
		Name:        proto.String(policyName),
		Description: proto.String(description),
		Type:        proto.String("CLOUD_ARMOR"),
	}

	op, err := client.Insert(ctx, &computepb.InsertSecurityPolicyRequest{
		Project:                c.projectID,
		SecurityPolicyResource: policy,
	})
	if err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: gagal membuat security policy: %v", err)
	}

	if err := op.Wait(ctx); err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: gagal menunggu operasi selesai: %v", err)
	}

	log.Printf("🛡️ [OMNI ARMOR] Security Policy '%s' berhasil dibuat", policyName)
	return nil
}

// AddWAFRule menambahkan aturan WAF (SQL injection, XSS protection, dll.)
func (c *CloudArmorBridge) AddWAFRule(ctx context.Context, policyName string, priority int32, expression string, action string, description string) error {
	client, err := compute.NewSecurityPoliciesRESTClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	rule := &computepb.SecurityPolicyRule{
		Priority:    proto.Int32(priority),
		Description: proto.String(description),
		Action:      proto.String(action), // "allow" atau "deny(403)"
		Match: &computepb.SecurityPolicyRuleMatcher{
			Expr: &computepb.Expr{
				Expression: proto.String(expression),
			},
		},
	}

	op, err := client.AddRule(ctx, &computepb.AddRuleSecurityPolicyRequest{
		Project:                    c.projectID,
		SecurityPolicy:             policyName,
		SecurityPolicyRuleResource: rule,
	})
	if err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: gagal menambahkan WAF rule: %v", err)
	}

	if err := op.Wait(ctx); err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: operasi rule gagal: %v", err)
	}

	log.Printf("🛡️ [OMNI ARMOR] WAF Rule priority=%d ditambahkan ke '%s': %s → %s",
		priority, policyName, expression, action)
	return nil
}

// AddRateLimitRule menambahkan aturan rate limiting ke policy
func (c *CloudArmorBridge) AddRateLimitRule(ctx context.Context, policyName string, priority int32, conformRate int32, exceedAction string) error {
	client, err := compute.NewSecurityPoliciesRESTClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	rule := &computepb.SecurityPolicyRule{
		Priority:    proto.Int32(priority),
		Description: proto.String(fmt.Sprintf("OMNI Rate Limit: %d req/min", conformRate)),
		Action:      proto.String("throttle"),
		Match: &computepb.SecurityPolicyRuleMatcher{
			VersionedExpr: proto.String("SRC_IPS_V1"),
			Config: &computepb.SecurityPolicyRuleMatcherConfig{
				SrcIpRanges: []string{"*"},
			},
		},
		RateLimitOptions: &computepb.SecurityPolicyRuleRateLimitOptions{
			ConformAction: proto.String("allow"),
			ExceedAction:  proto.String(exceedAction),
			RateLimitThreshold: &computepb.SecurityPolicyRuleRateLimitOptionsThreshold{
				Count:       proto.Int32(conformRate),
				IntervalSec: proto.Int32(60),
			},
		},
	}

	op, err := client.AddRule(ctx, &computepb.AddRuleSecurityPolicyRequest{
		Project:                    c.projectID,
		SecurityPolicy:             policyName,
		SecurityPolicyRuleResource: rule,
	})
	if err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: gagal menambahkan rate limit rule: %v", err)
	}

	if err := op.Wait(ctx); err != nil {
		return fmt.Errorf("OMNI_ARMOR_ERROR: operasi rate limit gagal: %v", err)
	}

	log.Printf("🛡️ [OMNI ARMOR] Rate Limit %d req/min ditambahkan ke '%s'", conformRate, policyName)
	return nil
}

// ListPolicies menampilkan semua security policies di project
func (c *CloudArmorBridge) ListPolicies(ctx context.Context) ([]*ArmorPolicyInfo, error) {
	client, err := compute.NewSecurityPoliciesRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ARMOR_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &computepb.ListSecurityPoliciesRequest{
		Project: c.projectID,
	}

	var policies []*ArmorPolicyInfo
	it := client.List(ctx, req)
	for {
		policy, err := it.Next()
		if err != nil {
			break
		}
		policies = append(policies, &ArmorPolicyInfo{
			Name:        policy.GetName(),
			Description: policy.GetDescription(),
			RuleCount:   int32(len(policy.GetRules())),
			Type:        policy.GetType(),
		})
	}

	log.Printf("🛡️ [OMNI ARMOR] Ditemukan %d security policies", len(policies))
	return policies, nil
}

// ArmorPolicyInfo berisi informasi ringkas tentang security policy
type ArmorPolicyInfo struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	RuleCount   int32  `json:"rule_count"`
	Type        string `json:"type"`
}

// ==========================================
// 🏗️ PRE-BUILT WAF TEMPLATES UNTUK OMNI
// ==========================================

// DeployOMNIShieldPolicy membuat security policy standar OMNI
// dengan perlindungan SQLi, XSS, dan rate limiting bawaan
func (c *CloudArmorBridge) DeployOMNIShieldPolicy(ctx context.Context) error {
	policyName := "omni-shield-policy"

	// 1. Buat policy
	if err := c.CreateSecurityPolicy(ctx, policyName, "OMNI Framework Enterprise WAF Shield"); err != nil {
		return err
	}

	// 2. Block SQL Injection (priority 1000)
	if err := c.AddWAFRule(ctx, policyName, 1000,
		"evaluatePreconfiguredExpr('sqli-v33-stable')",
		"deny(403)",
		"OMNI Shield: Block SQL Injection"); err != nil {
		return err
	}

	// 3. Block XSS (priority 2000)
	if err := c.AddWAFRule(ctx, policyName, 2000,
		"evaluatePreconfiguredExpr('xss-v33-stable')",
		"deny(403)",
		"OMNI Shield: Block Cross-Site Scripting"); err != nil {
		return err
	}

	// 4. Block Remote Code Execution (priority 3000)
	if err := c.AddWAFRule(ctx, policyName, 3000,
		"evaluatePreconfiguredExpr('rce-v33-stable')",
		"deny(403)",
		"OMNI Shield: Block Remote Code Execution"); err != nil {
		return err
	}

	// 5. Rate Limit: 1000 req/min per IP (priority 9000)
	if err := c.AddRateLimitRule(ctx, policyName, 9000, 1000, "deny(429)"); err != nil {
		return err
	}

	log.Println("🛡️ [OMNI ARMOR] ========================================")
	log.Println("🛡️ [OMNI ARMOR] OMNI Shield Policy DEPLOYED!")
	log.Println("🛡️ [OMNI ARMOR]   ├── SQLi Protection    ✅")
	log.Println("🛡️ [OMNI ARMOR]   ├── XSS Protection     ✅")
	log.Println("🛡️ [OMNI ARMOR]   ├── RCE Protection     ✅")
	log.Println("🛡️ [OMNI ARMOR]   └── Rate Limit 1K/min  ✅")
	log.Println("🛡️ [OMNI ARMOR] ========================================")
	return nil
}
