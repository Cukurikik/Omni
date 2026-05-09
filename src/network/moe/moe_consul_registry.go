// moe_consul_registry.go — Network / Service Discovery
// Layer: Network / Discovery — MoE Cluster
//
// Integrates MoE expert tracking with HashiCorp Consul.
// Allows compute nodes to register which experts they host,
// and routing nodes to query Consul to find healthy expert hosts.

package network_moe

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Consul integration config
type ConsulConfig struct {
	Address    string
	Datacenter string
	Token      string
}

// MoEConsulRegistry manages interaction with Consul API.
type MoEConsulRegistry struct {
	config     ConsulConfig
	httpClient *http.Client
}

func NewConsulRegistry(cfg ConsulConfig) *MoEConsulRegistry {
	return &MoEConsulRegistry{
		config:     cfg,
		httpClient: &http.Client{Timeout: 10 * time.Second},
	}
}

type ConsulRegistration struct {
	ID      string   `json:"ID"`
	Name    string   `json:"Name"`
	Tags    []string `json:"Tags"`
	Address string   `json:"Address"`
	Port    int      `json:"Port"`
	Check   struct {
		HTTP     string `json:"HTTP"`
		Interval string `json:"Interval"`
	} `json:"Check"`
}

// RegisterExpertNode registers a node providing specific MoE experts.
func (r *MoEConsulRegistry) RegisterExpertNode(nodeID, address string, port int, expertIDs []int) error {
	// Format tags: "expert-0", "expert-1", etc.
	tags := make([]string, len(expertIDs))
	for i, eid := range expertIDs {
		tags[i] = fmt.Sprintf("expert-%d", eid)
	}

	reg := ConsulRegistration{
		ID:      fmt.Sprintf("moe-node-%s", nodeID),
		Name:    "moe-expert-service",
		Tags:    tags,
		Address: address,
		Port:    port,
	}

	// Add a basic HTTP health check
	reg.Check.HTTP = fmt.Sprintf("http://%s:%d/health", address, port)
	reg.Check.Interval = "10s"

	payload, err := json.Marshal(reg)
	if err != nil {
		return err
	}

	url := fmt.Sprintf("%s/v1/agent/service/register", r.config.Address)
	req, err := http.NewRequest("PUT", url, bytes.NewBuffer(payload))
	if err != nil {
		return err
	}

	if r.config.Token != "" {
		req.Header.Set("X-Consul-Token", r.config.Token)
	}

	resp, err := r.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("consul registration failed with status: %d", resp.StatusCode)
	}

	return nil
}

// DiscoverExpert finds healthy nodes hosting a specific expert ID.
func (r *MoEConsulRegistry) DiscoverExpert(expertID int) ([]string, error) {
	tag := fmt.Sprintf("expert-%d", expertID)
	url := fmt.Sprintf("%s/v1/health/service/moe-expert-service?passing=true&tag=%s", r.config.Address, tag)

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	resp, err := r.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("consul discovery failed with status: %d", resp.StatusCode)
	}

	var results []struct {
		Service struct {
			Address string `json:"Address"`
			Port    int    `json:"Port"`
		} `json:"Service"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&results); err != nil {
		return nil, err
	}

	var endpoints []string
	for _, res := range results {
		endpoints = append(endpoints, fmt.Sprintf("%s:%d", res.Service.Address, res.Service.Port))
	}

	return endpoints, nil
}

