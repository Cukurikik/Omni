// ===========================================================================
// OMNI NETWORK LAYER — OPENDIA MULTI-CHANNEL PLATFORM BRIDGE
// ===========================================================================
// Source Paradigm : nicehash/opendia-mcp
// Domain Layer   : Network (HTTP/gRPC bridge, event routing)
// Language        : Go
// Function        : Multi-channel communication platform bridge that routes
//                   messages between providers (Discord, Slack, Telegram, SMS),
//                   normalizes payloads, tracks delivery, and handles failover
// ===========================================================================

package network

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

// ---- Channel Types --------------------------------------------------------

type ChannelProvider int

const (
	ProviderDiscord ChannelProvider = iota
	ProviderSlack
	ProviderTelegram
	ProviderSMS
	ProviderEmail
	ProviderWebhook
)

func (p ChannelProvider) String() string {
	names := [...]string{"discord", "slack", "telegram", "sms", "email", "webhook"}
	if int(p) < len(names) {
		return names[p]
	}
	return "unknown"
}

// ChannelConfig defines connection settings for a provider.
type ChannelConfig struct {
	Provider   ChannelProvider
	APIKey     string
	WebhookURL string
	ChatID     string // Telegram chat ID, Discord channel ID, etc.
	IsEnabled  bool
	Priority   int // lower = higher priority (for failover)
}

// NormalizedMessage is the provider-agnostic message format.
type NormalizedMessage struct {
	ID          string
	From        string
	To          string // channel reference
	Content     string
	ContentType string   // "text", "markdown", "html"
	Attachments []string // URLs
	Timestamp   time.Time
	Provider    ChannelProvider
}

// DeliveryStatus tracks a message's delivery lifecycle.
type DeliveryStatus struct {
	MessageID   string
	Provider    ChannelProvider
	Status      string // "queued", "sent", "delivered", "failed"
	SentAt      time.Time
	DeliveredAt *time.Time
	Error       string
	Attempts    int
}

// ---- Multi-Channel Router -------------------------------------------------

type OpendiaMCPBridge struct {
	channels   map[ChannelProvider]*ChannelConfig
	outbox     []NormalizedMessage
	deliveries map[string]*DeliveryStatus
	mu         sync.RWMutex
	maxRetries int
}

func NewOpendiaBridge(maxRetries int) *OpendiaMCPBridge {
	fmt.Println("[OPENDIA-OMNI-GO] MCP Bridge initialized.")
	return &OpendiaMCPBridge{
		channels:   make(map[ChannelProvider]*ChannelConfig),
		deliveries: make(map[string]*DeliveryStatus),
		maxRetries: maxRetries,
	}
}

// RegisterChannel adds a provider configuration.
func (b *OpendiaMCPBridge) RegisterChannel(config ChannelConfig) {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.channels[config.Provider] = &config
	fmt.Printf("[OPENDIA-OMNI-GO] Registered channel: %s (priority: %d)\n",
		config.Provider, config.Priority)
}

// Send dispatches a message to a specific provider.
func (b *OpendiaMCPBridge) Send(msg NormalizedMessage) *DeliveryStatus {
	b.mu.Lock()
	defer b.mu.Unlock()

	config, exists := b.channels[msg.Provider]
	if !exists || !config.IsEnabled {
		return &DeliveryStatus{
			MessageID: msg.ID, Provider: msg.Provider,
			Status: "failed", Error: "provider not registered or disabled",
		}
	}

	fmt.Printf("[OPENDIA-OMNI-GO] Sending via %s: %s → %s\n",
		msg.Provider, msg.From, msg.To)

	status := &DeliveryStatus{
		MessageID: msg.ID,
		Provider:  msg.Provider,
		Status:    "sent",
		SentAt:    time.Now(),
		Attempts:  1,
	}

	// Production: HTTP POST to provider API
	// Discord: POST /api/v10/channels/{id}/messages
	// Slack: POST /api/chat.postMessage
	// Telegram: POST /bot{token}/sendMessage

	b.deliveries[msg.ID] = status
	return status
}

// SendWithFailover tries primary provider, falls back to alternates.
func (b *OpendiaMCPBridge) SendWithFailover(msg NormalizedMessage) *DeliveryStatus {
	b.mu.RLock()
	// Build priority-sorted channel list
	type prioritized struct {
		provider ChannelProvider
		priority int
	}
	var sorted []prioritized
	for prov, config := range b.channels {
		if config.IsEnabled {
			sorted = append(sorted, prioritized{prov, config.Priority})
		}
	}
	b.mu.RUnlock()

	// Sort by priority (simple bubble)
	for i := 0; i < len(sorted); i++ {
		for j := i + 1; j < len(sorted); j++ {
			if sorted[j].priority < sorted[i].priority {
				sorted[i], sorted[j] = sorted[j], sorted[i]
			}
		}
	}

	for _, s := range sorted {
		msg.Provider = s.provider
		status := b.Send(msg)
		if status.Status != "failed" {
			return status
		}
		fmt.Printf("[OPENDIA-OMNI-GO] Failover: %s failed, trying next...\n", s.provider)
	}

	return &DeliveryStatus{
		MessageID: msg.ID, Status: "failed",
		Error: "all providers exhausted",
	}
}

// Broadcast sends a message to ALL enabled channels.
func (b *OpendiaMCPBridge) Broadcast(content string, from string) []*DeliveryStatus {
	b.mu.RLock()
	providers := make([]ChannelProvider, 0)
	for prov, config := range b.channels {
		if config.IsEnabled {
			providers = append(providers, prov)
		}
	}
	b.mu.RUnlock()

	fmt.Printf("[OPENDIA-OMNI-GO] Broadcasting to %d channel(s)...\n", len(providers))

	var results []*DeliveryStatus
	for _, prov := range providers {
		msg := NormalizedMessage{
			ID:          fmt.Sprintf("bc-%d-%s", time.Now().UnixNano(), prov),
			From:        from,
			Content:     content,
			ContentType: "text",
			Timestamp:   time.Now(),
			Provider:    prov,
		}
		results = append(results, b.Send(msg))
	}
	return results
}

// GetDeliveryStats returns aggregated delivery statistics.
func (b *OpendiaMCPBridge) GetDeliveryStats() map[string]int {
	b.mu.RLock()
	defer b.mu.RUnlock()

	stats := map[string]int{"total": 0, "sent": 0, "failed": 0}
	for _, d := range b.deliveries {
		stats["total"]++
		if strings.Contains(d.Status, "fail") {
			stats["failed"]++
		} else {
			stats["sent"]++
		}
	}
	return stats
}
