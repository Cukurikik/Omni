// ===========================================================================
// OMNI NETWORK LAYER — OPNSENSE FIREWALL ENGINE
// ===========================================================================
// Source Repo   : github.com/O-X-L/ansible-opnsense
// Domain Layer  : Network (Infrastructure automation, firewall management)
// Language      : Go
// Function      : OPNsense firewall API automation — rule management, alias
//                 CRUD, VLAN configuration, VPN (WireGuard/IPSec) tunnels,
//                 HAProxy load balancing, Unbound DNS, interface management,
//                 firmware lifecycle, and configuration backup/restore.
//                 All operations go through OPNsense's REST API with HMAC auth.
// ===========================================================================

package network

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"
)

// ---- OPNsense API Authentication ------------------------------------------

// OPNAuth holds API key + secret for HMAC-SHA256 authentication against OPNsense.
type OPNAuth struct {
	APIKey    string
	APISecret string
	BaseURL   string // e.g. "https://192.168.1.1/api"
	VerifySSL bool
}

func (a *OPNAuth) SignRequest(method, path string, body []byte) *http.Request {
	timestamp := fmt.Sprintf("%d", time.Now().Unix())
	message := fmt.Sprintf("%s\n%s\n%s\n%s", a.APIKey, method, path, timestamp)
	mac := hmac.New(sha256.New, []byte(a.APISecret))
	mac.Write([]byte(message))
	signature := hex.EncodeToString(mac.Sum(nil))

	url := a.BaseURL + path
	var bodyReader io.Reader
	if body != nil {
		bodyReader = strings.NewReader(string(body))
	}
	req, _ := http.NewRequest(method, url, bodyReader)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", a.APIKey)
	req.Header.Set("X-API-Signature", signature)
	req.Header.Set("X-API-Timestamp", timestamp)
	return req
}

// ---- Firewall Rule --------------------------------------------------------

type RuleAction int

const (
	ActionPass RuleAction = iota
	ActionBlock
	ActionReject
)

func (a RuleAction) String() string {
	return [...]string{"pass", "block", "reject"}[a]
}

type IPProtocol int

const (
	ProtoAny IPProtocol = iota
	ProtoTCP
	ProtoUDP
	ProtoICMP
)

func (p IPProtocol) String() string {
	return [...]string{"any", "TCP", "UDP", "ICMP"}[p]
}

type RuleDirection int

const (
	DirIn RuleDirection = iota
	DirOut
)

func (d RuleDirection) String() string {
	return [...]string{"in", "out"}[d]
}

type FirewallRule struct {
	UUID        string
	Description string
	Action      RuleAction
	Interface   string
	Direction   RuleDirection
	Protocol    IPProtocol
	SourceNet   string // CIDR or alias
	SourcePort  string
	DestNet     string
	DestPort    string
	Log         bool
	Enabled     bool
	Sequence    int
	CreatedAt   time.Time
	UpdatedAt   time.Time
}

func (r *FirewallRule) ToJSON() ([]byte, error) {
	payload := map[string]interface{}{
		"rule": map[string]interface{}{
			"description":      r.Description,
			"action":           r.Action.String(),
			"interface":        r.Interface,
			"direction":        r.Direction.String(),
			"ipprotocol":       "inet",
			"protocol":         r.Protocol.String(),
			"source_net":       r.SourceNet,
			"source_port":      r.SourcePort,
			"destination":      r.DestNet,
			"destination_port": r.DestPort,
			"log":              r.Log,
			"enabled":          r.Enabled,
			"sequence":         r.Sequence,
		},
	}
	return json.Marshal(payload)
}

// ---- Alias ----------------------------------------------------------------

type AliasType int

const (
	AliasHost AliasType = iota
	AliasNetwork
	AliasPort
	AliasURL
	AliasURLTable
	AliasGeoIP
	AliasMACAddress
	AliasBGPASN
)

func (a AliasType) String() string {
	return [...]string{
		"host", "network", "port", "url", "urltable",
		"geoip", "mac", "asn",
	}[a]
}

type Alias struct {
	UUID        string
	Name        string
	Type        AliasType
	Content     []string // IPs, CIDRs, ports, URLs, country codes
	Description string
	Enabled     bool
	UpdateFreq  string // for URL tables: "1d", "1h", etc.
}

func (a *Alias) ToJSON() ([]byte, error) {
	payload := map[string]interface{}{
		"alias": map[string]interface{}{
			"name":        a.Name,
			"type":        a.Type.String(),
			"content":     strings.Join(a.Content, "\n"),
			"description": a.Description,
			"enabled":     a.Enabled,
			"updatefreq":  a.UpdateFreq,
		},
	}
	return json.Marshal(payload)
}

// ---- VLAN -----------------------------------------------------------------

type VLAN struct {
	UUID        string
	Tag         int    // 1-4094
	ParentIF    string // e.g. "igb0"
	Description string
	Priority    int // 802.1p priority 0-7
}

// ---- VPN Tunnel -----------------------------------------------------------

type VPNType int

const (
	VPNWireGuard VPNType = iota
	VPNIPSec
	VPNOpenVPN
)

func (v VPNType) String() string {
	return [...]string{"wireguard", "ipsec", "openvpn"}[v]
}

type VPNTunnel struct {
	UUID       string
	Name       string
	Type       VPNType
	LocalAddr  string
	RemoteAddr string
	ListenPort int
	PublicKey  string
	PrivateKey string
	AllowedIPs []string
	Enabled    bool
}

// ---- HAProxy Backend/Server -----------------------------------------------

type HAProxyMode int

const (
	HAProxyHTTP HAProxyMode = iota
	HAProxyTCP
)

func (m HAProxyMode) String() string {
	return [...]string{"http", "tcp"}[m]
}

type HAProxyServer struct {
	Name    string
	Address string
	Port    int
	Weight  int
	Mode    string // "active", "backup"
	SSL     bool
}

type HAProxyBackend struct {
	UUID        string
	Name        string
	Mode        HAProxyMode
	Servers     []HAProxyServer
	BalanceAlgo string // "roundrobin", "leastconn", "source"
	HealthCheck string // "/health"
}

// ---- Unbound DNS ----------------------------------------------------------

type DNSOverride struct {
	UUID        string
	Hostname    string
	Domain      string
	IPAddress   string
	Description string
	Enabled     bool
}

type DNSForwarder struct {
	UUID   string
	Domain string
	Server string
	Port   int
}

// ---- Interface Config -----------------------------------------------------

type InterfaceConfig struct {
	Name        string // e.g. "opt1"
	Device      string // e.g. "igb2"
	Description string
	IPv4Type    string // "static", "dhcp", "none"
	IPv4Addr    string
	IPv4Subnet  int
	IPv4Gateway string
	Enabled     bool
}

// ---- Firmware Info --------------------------------------------------------

type FirmwareInfo struct {
	CurrentVersion string
	LatestVersion  string
	NeedsReboot    bool
	LastCheck      time.Time
	Packages       []FirmwarePackage
}

type FirmwarePackage struct {
	Name         string
	InstalledVer string
	AvailableVer string
	NeedsUpgrade bool
}

// ---- API Client -----------------------------------------------------------

type APIResponse struct {
	StatusCode int
	Body       map[string]interface{}
	UUID       string
	Error      string
}

type OPNsenseClient struct {
	auth   *OPNAuth
	client *http.Client
}

func NewOPNsenseClient(auth *OPNAuth) *OPNsenseClient {
	transport := &http.Transport{}
	return &OPNsenseClient{
		auth: auth,
		client: &http.Client{
			Transport: transport,
			Timeout:   30 * time.Second,
		},
	}
}

func (c *OPNsenseClient) doRequest(method, path string, body []byte) (*APIResponse, error) {
	req := c.auth.SignRequest(method, path, body)
	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("OPNsense API request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(respBody, &result)

	apiResp := &APIResponse{
		StatusCode: resp.StatusCode,
		Body:       result,
	}

	if uuid, ok := result["uuid"].(string); ok {
		apiResp.UUID = uuid
	}
	if resp.StatusCode >= 400 {
		apiResp.Error = string(respBody)
	}

	return apiResp, nil
}

// ---- OPNsense Firewall Engine (Main) --------------------------------------

type OPNsenseEngine struct {
	mu       sync.RWMutex
	client   *OPNsenseClient
	auth     *OPNAuth
	rules    map[string]*FirewallRule
	aliases  map[string]*Alias
	vlans    map[string]*VLAN
	vpns     map[string]*VPNTunnel
	backends map[string]*HAProxyBackend
	dns      map[string]*DNSOverride
	ifaces   map[string]*InterfaceConfig
	firmware *FirmwareInfo
	auditLog []string
}

func NewOPNsenseEngine(baseURL, apiKey, apiSecret string) *OPNsenseEngine {
	auth := &OPNAuth{
		APIKey:    apiKey,
		APISecret: apiSecret,
		BaseURL:   baseURL,
		VerifySSL: false,
	}
	fmt.Printf("[OPNSENSE-OMNI-GO] Firewall engine initialized: %s\n", baseURL)
	return &OPNsenseEngine{
		client:   NewOPNsenseClient(auth),
		auth:     auth,
		rules:    make(map[string]*FirewallRule),
		aliases:  make(map[string]*Alias),
		vlans:    make(map[string]*VLAN),
		vpns:     make(map[string]*VPNTunnel),
		backends: make(map[string]*HAProxyBackend),
		dns:      make(map[string]*DNSOverride),
		ifaces:   make(map[string]*InterfaceConfig),
		auditLog: make([]string, 0),
	}
}

// ---- Firewall Rule CRUD ---------------------------------------------------

func (e *OPNsenseEngine) AddRule(rule *FirewallRule) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	body, err := rule.ToJSON()
	if err != nil {
		return nil, err
	}

	resp, err := e.client.doRequest("POST", "/firewall/filter/addRule", body)
	if err != nil {
		return nil, err
	}

	if resp.UUID != "" {
		rule.UUID = resp.UUID
		rule.CreatedAt = time.Now()
		e.rules[resp.UUID] = rule
	}

	e.logAudit("ADD_RULE", rule.Description)
	fmt.Printf("[OPNSENSE-OMNI-GO] Rule added: %s %s %s:%s -> %s:%s\n",
		rule.Action, rule.Protocol, rule.SourceNet, rule.SourcePort,
		rule.DestNet, rule.DestPort)
	return resp, nil
}

func (e *OPNsenseEngine) DeleteRule(uuid string) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	resp, err := e.client.doRequest("POST", "/firewall/filter/delRule/"+uuid, nil)
	if err != nil {
		return nil, err
	}

	if rule, ok := e.rules[uuid]; ok {
		e.logAudit("DELETE_RULE", rule.Description)
		delete(e.rules, uuid)
	}
	return resp, nil
}

func (e *OPNsenseEngine) ToggleRule(uuid string, enabled bool) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	action := "disableRule"
	if enabled {
		action = "enableRule"
	}

	resp, err := e.client.doRequest("POST", "/firewall/filter/"+action+"/"+uuid, nil)
	if err != nil {
		return nil, err
	}

	if rule, ok := e.rules[uuid]; ok {
		rule.Enabled = enabled
		rule.UpdatedAt = time.Now()
		e.logAudit("TOGGLE_RULE", fmt.Sprintf("%s -> enabled=%v", rule.Description, enabled))
	}
	return resp, nil
}

func (e *OPNsenseEngine) ListRules() []*FirewallRule {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rules := make([]*FirewallRule, 0, len(e.rules))
	for _, r := range e.rules {
		rules = append(rules, r)
	}
	return rules
}

func (e *OPNsenseEngine) ApplyRules() (*APIResponse, error) {
	e.logAudit("APPLY_RULES", fmt.Sprintf("%d rules", len(e.rules)))
	return e.client.doRequest("POST", "/firewall/filter/apply", nil)
}

// ---- Alias Management -----------------------------------------------------

func (e *OPNsenseEngine) AddAlias(alias *Alias) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	body, err := alias.ToJSON()
	if err != nil {
		return nil, err
	}

	resp, err := e.client.doRequest("POST", "/firewall/alias/addItem", body)
	if err != nil {
		return nil, err
	}

	if resp.UUID != "" {
		alias.UUID = resp.UUID
		e.aliases[resp.UUID] = alias
	}

	e.logAudit("ADD_ALIAS", fmt.Sprintf("%s (%s) [%d entries]",
		alias.Name, alias.Type, len(alias.Content)))
	return resp, nil
}

func (e *OPNsenseEngine) DeleteAlias(uuid string) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	resp, err := e.client.doRequest("POST", "/firewall/alias/delItem/"+uuid, nil)
	if err != nil {
		return nil, err
	}
	delete(e.aliases, uuid)
	return resp, nil
}

func (e *OPNsenseEngine) ReconfigureAliases() (*APIResponse, error) {
	e.logAudit("RECONFIGURE_ALIASES", "")
	return e.client.doRequest("POST", "/firewall/alias/reconfigure", nil)
}

// ---- VLAN Management ------------------------------------------------------

func (e *OPNsenseEngine) AddVLAN(vlan *VLAN) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	payload, _ := json.Marshal(map[string]interface{}{
		"vlan": map[string]interface{}{
			"tag":   vlan.Tag,
			"if":    vlan.ParentIF,
			"descr": vlan.Description,
			"pcp":   vlan.Priority,
		},
	})

	resp, err := e.client.doRequest("POST", "/interfaces/vlan_settings/addItem", payload)
	if err != nil {
		return nil, err
	}

	if resp.UUID != "" {
		vlan.UUID = resp.UUID
		e.vlans[resp.UUID] = vlan
	}

	e.logAudit("ADD_VLAN", fmt.Sprintf("tag=%d on %s", vlan.Tag, vlan.ParentIF))
	return resp, nil
}

// ---- VPN Tunnel Management ------------------------------------------------

func (e *OPNsenseEngine) AddWireGuardPeer(tunnel *VPNTunnel) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	payload, _ := json.Marshal(map[string]interface{}{
		"client": map[string]interface{}{
			"name":          tunnel.Name,
			"pubkey":        tunnel.PublicKey,
			"tunneladdress": strings.Join(tunnel.AllowedIPs, ","),
			"enabled":       tunnel.Enabled,
		},
	})

	resp, err := e.client.doRequest("POST", "/wireguard/client/addClient", payload)
	if err != nil {
		return nil, err
	}

	if resp.UUID != "" {
		tunnel.UUID = resp.UUID
		e.vpns[resp.UUID] = tunnel
	}

	e.logAudit("ADD_VPN", fmt.Sprintf("%s %s -> %s",
		tunnel.Type, tunnel.Name, tunnel.RemoteAddr))
	return resp, nil
}

// ---- HAProxy Management ---------------------------------------------------

func (e *OPNsenseEngine) AddHAProxyBackend(backend *HAProxyBackend) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	servers := make([]map[string]interface{}, 0, len(backend.Servers))
	for _, srv := range backend.Servers {
		servers = append(servers, map[string]interface{}{
			"name":    srv.Name,
			"address": srv.Address,
			"port":    srv.Port,
			"weight":  srv.Weight,
			"mode":    srv.Mode,
			"ssl":     srv.SSL,
		})
	}

	payload, _ := json.Marshal(map[string]interface{}{
		"backend": map[string]interface{}{
			"name":        backend.Name,
			"mode":        backend.Mode.String(),
			"algorithm":   backend.BalanceAlgo,
			"healthCheck": backend.HealthCheck,
			"servers":     servers,
		},
	})

	resp, err := e.client.doRequest("POST", "/haproxy/settings/addBackend", payload)
	if err != nil {
		return nil, err
	}

	if resp.UUID != "" {
		backend.UUID = resp.UUID
		e.backends[resp.UUID] = backend
	}

	e.logAudit("ADD_HAPROXY_BACKEND", fmt.Sprintf("%s (%d servers)",
		backend.Name, len(backend.Servers)))
	return resp, nil
}

// ---- Unbound DNS Management -----------------------------------------------

func (e *OPNsenseEngine) AddDNSOverride(override *DNSOverride) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	payload, _ := json.Marshal(map[string]interface{}{
		"host": map[string]interface{}{
			"hostname":    override.Hostname,
			"domain":      override.Domain,
			"server":      override.IPAddress,
			"description": override.Description,
			"enabled":     override.Enabled,
		},
	})

	resp, err := e.client.doRequest("POST", "/unbound/settings/addHostOverride", payload)
	if err != nil {
		return nil, err
	}

	if resp.UUID != "" {
		override.UUID = resp.UUID
		e.dns[resp.UUID] = override
	}

	e.logAudit("ADD_DNS", fmt.Sprintf("%s.%s -> %s",
		override.Hostname, override.Domain, override.IPAddress))
	return resp, nil
}

func (e *OPNsenseEngine) RestartUnbound() (*APIResponse, error) {
	e.logAudit("RESTART_UNBOUND", "")
	return e.client.doRequest("POST", "/unbound/service/restart", nil)
}

// ---- Interface Management -------------------------------------------------

func (e *OPNsenseEngine) ConfigureInterface(iface *InterfaceConfig) (*APIResponse, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	payload, _ := json.Marshal(map[string]interface{}{
		"interface": map[string]interface{}{
			"descr":   iface.Description,
			"if":      iface.Device,
			"ipaddr":  iface.IPv4Addr,
			"subnet":  iface.IPv4Subnet,
			"gateway": iface.IPv4Gateway,
			"enable":  iface.Enabled,
		},
	})

	resp, err := e.client.doRequest("POST", "/interfaces/overview/"+iface.Name, payload)
	if err != nil {
		return nil, err
	}

	e.ifaces[iface.Name] = iface
	e.logAudit("CONFIGURE_INTERFACE", fmt.Sprintf("%s (%s) %s/%d",
		iface.Name, iface.Device, iface.IPv4Addr, iface.IPv4Subnet))
	return resp, nil
}

// ---- Firmware Management --------------------------------------------------

func (e *OPNsenseEngine) CheckFirmware() (*FirmwareInfo, error) {
	resp, err := e.client.doRequest("GET", "/core/firmware/status", nil)
	if err != nil {
		return nil, err
	}

	info := &FirmwareInfo{
		LastCheck: time.Now(),
	}

	if body := resp.Body; body != nil {
		if v, ok := body["product_version"].(string); ok {
			info.CurrentVersion = v
		}
		if v, ok := body["product_latest"].(string); ok {
			info.LatestVersion = v
		}
		if v, ok := body["needs_reboot"].(string); ok {
			info.NeedsReboot = v == "1"
		}
	}

	e.mu.Lock()
	e.firmware = info
	e.mu.Unlock()

	e.logAudit("CHECK_FIRMWARE", fmt.Sprintf("current=%s latest=%s",
		info.CurrentVersion, info.LatestVersion))
	return info, nil
}

func (e *OPNsenseEngine) UpgradeFirmware() (*APIResponse, error) {
	e.logAudit("UPGRADE_FIRMWARE", "initiated")
	return e.client.doRequest("POST", "/core/firmware/upgrade", nil)
}

// ---- Configuration Backup/Restore -----------------------------------------

func (e *OPNsenseEngine) BackupConfig() ([]byte, error) {
	resp, err := e.client.doRequest("GET", "/core/backup/download/this", nil)
	if err != nil {
		return nil, err
	}
	e.logAudit("BACKUP_CONFIG", "")
	data, _ := json.Marshal(resp.Body)
	return data, nil
}

func (e *OPNsenseEngine) RestoreConfig(configData []byte) (*APIResponse, error) {
	e.logAudit("RESTORE_CONFIG", fmt.Sprintf("%d bytes", len(configData)))
	return e.client.doRequest("POST", "/core/backup/restore", configData)
}

// ---- Audit Log ------------------------------------------------------------

func (e *OPNsenseEngine) logAudit(action, detail string) {
	entry := fmt.Sprintf("[%s] %s: %s",
		time.Now().Format("2006-01-02T15:04:05"), action, detail)
	e.auditLog = append(e.auditLog, entry)
	fmt.Printf("[OPNSENSE-OMNI-GO] %s\n", entry)
}

func (e *OPNsenseEngine) GetAuditLog() []string {
	e.mu.RLock()
	defer e.mu.RUnlock()
	log := make([]string, len(e.auditLog))
	copy(log, e.auditLog)
	return log
}

// ---- Engine Stats ---------------------------------------------------------

func (e *OPNsenseEngine) Stats() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	stats := map[string]interface{}{
		"engine":         "OPNsense Firewall Engine",
		"version":        "1.0.0-omni",
		"base_url":       e.auth.BaseURL,
		"rules_count":    len(e.rules),
		"aliases_count":  len(e.aliases),
		"vlans_count":    len(e.vlans),
		"vpns_count":     len(e.vpns),
		"backends_count": len(e.backends),
		"dns_count":      len(e.dns),
		"interfaces":     len(e.ifaces),
		"audit_entries":  len(e.auditLog),
	}

	if e.firmware != nil {
		stats["firmware_current"] = e.firmware.CurrentVersion
		stats["firmware_latest"] = e.firmware.LatestVersion
		stats["firmware_needs_reboot"] = e.firmware.NeedsReboot
	}

	return stats
}
