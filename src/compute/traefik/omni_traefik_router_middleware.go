// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Traefik Router (OMNI Zero-Mock Implementation)
// Implements declarative priority matching evaluation for host routes.

package compute

import (
	"errors"
	"strings"
)

type TraefikResult struct {
	Value string // Matched route ID
	Error error
}

func OkTraefikResult(val string) TraefikResult {
	return TraefikResult{Value: val, Error: nil}
}

func ErrTraefikResult(err string) TraefikResult {
	return TraefikResult{Value: "", Error: errors.New(err)}
}

type Rule struct {
	RouteID  string
	HostRule string
	PathRule string
	Priority int
}

func MatchTraefikRule(host, path string, rules []Rule) TraefikResult {
	if host == "" || path == "" {
		return ErrTraefikResult("Host and path payload required for routing validation.")
	}

	// Mathematical abstraction of Traefik deterministic prioritization
	// Highest priority number wins. If same priority, longest rule string wins.
	var bestMatch *Rule

	for _, rule := range rules {
		hostMatch := rule.HostRule == "*" || rule.HostRule == host
		pathMatch := rule.PathRule == "/*" || strings.HasPrefix(path, rule.PathRule)

		if hostMatch && pathMatch {
			// Compare against best match so far
			r := rule // copy to avoid loop variable memory issues
			if bestMatch == nil {
				bestMatch = &r
			} else {
				if r.Priority > bestMatch.Priority {
					bestMatch = &r
				} else if r.Priority == bestMatch.Priority {
					// Fallback to Rule Length as per Traefik router docs logic mathematically
					rLen := len(r.HostRule) + len(r.PathRule)
					bLen := len(bestMatch.HostRule) + len(bestMatch.PathRule)
					if rLen > bLen {
						bestMatch = &r
					}
				}
			}
		}
	}

	if bestMatch == nil {
		return ErrTraefikResult("No matching rules found in Traefik router table.")
	}

	return OkTraefikResult(bestMatch.RouteID)
}
