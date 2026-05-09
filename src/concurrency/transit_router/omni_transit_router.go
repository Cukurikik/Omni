package transit_router

import (
	"errors"
	"math"
	"sync"
)

// OMNI Transit Router Engine — Concurrency Layer
// Absorbing itinero/transit multimodal routing logic with Dijkstra shortest path.

type StopNode struct {
	ID  string
	Lat float64
	Lon float64
}

type RouteEdge struct {
	From     string
	To       string
	CostSecs float64
	Mode     string // "bus", "train", "walk"
}

type RouteResult struct {
	Path     []string
	TotalSec float64
}

type OmniTransitRouter struct {
	mu      sync.RWMutex
	stops   map[string]StopNode
	edges   map[string][]RouteEdge
	queries int64
}

func NewOmniTransitRouter() *OmniTransitRouter {
	return &OmniTransitRouter{
		stops: make(map[string]StopNode),
		edges: make(map[string][]RouteEdge),
	}
}

func (r *OmniTransitRouter) AddStop(id string, lat, lon float64) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.stops[id] = StopNode{ID: id, Lat: lat, Lon: lon}
}

func (r *OmniTransitRouter) AddEdge(from, to string, costSecs float64, mode string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if costSecs < 0 {
		return errors.New("TransitError: Negative edge cost")
	}
	r.edges[from] = append(r.edges[from], RouteEdge{From: from, To: to, CostSecs: costSecs, Mode: mode})
	return nil
}

// FindRoute uses Dijkstra's algorithm to find the shortest multimodal path.
func (r *OmniTransitRouter) FindRoute(startID, endID string) (*RouteResult, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if _, ok := r.stops[startID]; !ok {
		return nil, errors.New("TransitError: Start stop not found")
	}
	if _, ok := r.stops[endID]; !ok {
		return nil, errors.New("TransitError: End stop not found")
	}

	r.queries++

	dist := make(map[string]float64)
	prev := make(map[string]string)
	visited := make(map[string]bool)

	for id := range r.stops {
		dist[id] = math.MaxFloat64
	}
	dist[startID] = 0

	for range r.stops {
		// Find unvisited node with minimum distance
		u := ""
		minDist := math.MaxFloat64
		for id, d := range dist {
			if !visited[id] && d < minDist {
				minDist = d
				u = id
			}
		}
		if u == "" || u == endID {
			break
		}
		visited[u] = true

		for _, edge := range r.edges[u] {
			alt := dist[u] + edge.CostSecs
			if alt < dist[edge.To] {
				dist[edge.To] = alt
				prev[edge.To] = u
			}
		}
	}

	if dist[endID] == math.MaxFloat64 {
		return nil, errors.New("TransitError: No route found")
	}

	// Reconstruct path
	path := []string{}
	curr := endID
	for curr != "" {
		path = append([]string{curr}, path...)
		curr = prev[curr]
	}

	return &RouteResult{Path: path, TotalSec: dist[endID]}, nil
}

func (r *OmniTransitRouter) Diagnostics() map[string]interface{} {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return map[string]interface{}{
		"engine":  "OmniTransitRouter",
		"stops":   len(r.stops),
		"queries": r.queries,
		"status":  "Operational",
	}
}
