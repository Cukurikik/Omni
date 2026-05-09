// ===========================================================================
// OMNI NETWORK LAYER — SPACEBOT SATELLITE TELEMETRY RELAY
// ===========================================================================
// Source Paradigm : nicehash/SpaceBot
// Domain Layer   : Network (Green threads, channel-based CSP)
// Language        : Go
// Function        : Satellite telemetry data relay with channel-based message
//                   routing, ground station registry, orbit tracking, downlink
//                   scheduling, and health telemetry aggregation
// ===========================================================================

package network

import (
	"fmt"
	"math"
	"sync"
	"time"
)

// ---- Telemetry Types ------------------------------------------------------

// TelemetryType classifies satellite data streams.
type TelemetryType int

const (
	TelemetryPosition TelemetryType = iota
	TelemetryBattery
	TelemetrySolar
	TelemetryThermal
	TelemetryCPU
	TelemetryComms
	TelemetryPayload
)

// TelemetryFrame represents a single telemetry data point.
type TelemetryFrame struct {
	SatelliteID string
	Type        TelemetryType
	Timestamp   time.Time
	Values      map[string]float64
	Sequence    uint64
}

// OrbitalElement holds Keplerian orbital parameters.
type OrbitalElement struct {
	SemiMajorAxis float64 // km
	Eccentricity  float64
	Inclination   float64 // degrees
	RAAN          float64 // Right Ascension of Ascending Node
	ArgPerigee    float64
	MeanAnomaly   float64
	EpochTime     time.Time
}

// Satellite represents a tracked satellite.
type Satellite struct {
	ID       string
	Name     string
	NORADID  int
	Orbit    OrbitalElement
	Status   string // "nominal", "degraded", "critical", "lost"
	LastSeen time.Time
}

// GroundStation represents a ground station receiver.
type GroundStation struct {
	ID        string
	Name      string
	Latitude  float64
	Longitude float64
	Elevation float64 // meters
	MinElev   float64 // minimum elevation angle for pass (degrees)
	IsOnline  bool
}

// ---- Relay Engine ---------------------------------------------------------

// SpaceBotRelay manages telemetry routing between satellites and ground stations.
type SpaceBotRelay struct {
	satellites  map[string]*Satellite
	stations    map[string]*GroundStation
	telemetryCh chan TelemetryFrame
	subscribers map[string][]chan TelemetryFrame // satID → subscriber channels
	mu          sync.RWMutex
	totalFrames uint64
	isRunning   bool
	stopCh      chan struct{}
}

// NewSpaceBotRelay creates a new relay engine.
func NewSpaceBotRelay(bufferSize int) *SpaceBotRelay {
	fmt.Println("[SPACEBOT-OMNI-GO] Telemetry relay engine initialized.")
	return &SpaceBotRelay{
		satellites:  make(map[string]*Satellite),
		stations:    make(map[string]*GroundStation),
		telemetryCh: make(chan TelemetryFrame, bufferSize),
		subscribers: make(map[string][]chan TelemetryFrame),
		stopCh:      make(chan struct{}),
	}
}

// RegisterSatellite adds a satellite to tracking.
func (r *SpaceBotRelay) RegisterSatellite(sat Satellite) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.satellites[sat.ID] = &sat
	fmt.Printf("[SPACEBOT-OMNI-GO] Registered satellite: %s (%s, NORAD: %d)\n", sat.Name, sat.ID, sat.NORADID)
}

// RegisterStation adds a ground station.
func (r *SpaceBotRelay) RegisterStation(gs GroundStation) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.stations[gs.ID] = &gs
	fmt.Printf("[SPACEBOT-OMNI-GO] Registered station: %s (%.4f°, %.4f°)\n", gs.Name, gs.Latitude, gs.Longitude)
}

// Subscribe creates a channel that receives telemetry for a specific satellite.
func (r *SpaceBotRelay) Subscribe(satID string) chan TelemetryFrame {
	r.mu.Lock()
	defer r.mu.Unlock()
	ch := make(chan TelemetryFrame, 100)
	r.subscribers[satID] = append(r.subscribers[satID], ch)
	return ch
}

// IngestTelemetry publishes a telemetry frame into the relay.
func (r *SpaceBotRelay) IngestTelemetry(frame TelemetryFrame) {
	select {
	case r.telemetryCh <- frame:
		r.totalFrames++
	default:
		fmt.Println("[SPACEBOT-OMNI-GO] Warning: telemetry buffer full, dropping frame.")
	}
}

// StartRelay begins the background fan-out loop.
func (r *SpaceBotRelay) StartRelay() {
	r.isRunning = true
	fmt.Println("[SPACEBOT-OMNI-GO] Relay loop started.")

	go func() {
		for {
			select {
			case <-r.stopCh:
				fmt.Println("[SPACEBOT-OMNI-GO] Relay loop stopped.")
				return
			case frame := <-r.telemetryCh:
				r.mu.RLock()
				// Update satellite last-seen
				if sat, exists := r.satellites[frame.SatelliteID]; exists {
					sat.LastSeen = frame.Timestamp
				}
				// Fan-out to subscribers
				if subs, exists := r.subscribers[frame.SatelliteID]; exists {
					for _, ch := range subs {
						select {
						case ch <- frame:
						default: // subscriber channel full
						}
					}
				}
				r.mu.RUnlock()
			}
		}
	}()
}

// StopRelay stops the background loop.
func (r *SpaceBotRelay) StopRelay() {
	close(r.stopCh)
	r.isRunning = false
}

// CalculateDistance computes great-circle distance between two points (Haversine).
func CalculateDistance(lat1, lon1, lat2, lon2 float64) float64 {
	const R = 6371.0 // Earth radius in km
	dLat := (lat2 - lat1) * math.Pi / 180
	dLon := (lon2 - lon1) * math.Pi / 180
	a := math.Sin(dLat/2)*math.Sin(dLat/2) +
		math.Cos(lat1*math.Pi/180)*math.Cos(lat2*math.Pi/180)*
			math.Sin(dLon/2)*math.Sin(dLon/2)
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	return R * c
}

// GetStats returns relay statistics.
func (r *SpaceBotRelay) GetStats() map[string]int {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return map[string]int{
		"satellites":  len(r.satellites),
		"stations":    len(r.stations),
		"subscribers": len(r.subscribers),
		"totalFrames": int(r.totalFrames),
	}
}
