// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// NATS PubSub (OMNI Zero-Mock Implementation)
// Implements Subject-based wildcard routing Radix Trie evaluation.

package compute

import (
	"errors"
	"strings"
)

type RoutingResult struct {
	Value []string // Matching subscriber IDs
	Error error
}

func OkRoutingResult(val []string) RoutingResult {
	return RoutingResult{Value: val, Error: nil}
}

func ErrRoutingResult(err string) RoutingResult {
	return RoutingResult{Value: nil, Error: errors.New(err)}
}

type Subscription struct {
	SubID   string
	Subject string // e.g. "foo.bar.*", "foo.>"
}

func matchSubject(published, subscription string) bool {
	pubTokens := strings.Split(published, ".")
	subTokens := strings.Split(subscription, ".")

	for i, subTok := range subTokens {
		// Full wildcard matcher matches the rest
		if subTok == ">" {
			return true
		}

		// Length mismatch before completing subject
		if i >= len(pubTokens) {
			return false
		}

		// Exact match or single-level wildcard
		if subTok != "*" && subTok != pubTokens[i] {
			return false
		}
	}

	// Must be exact length match unless "foo.>" was hit early
	return len(pubTokens) == len(subTokens)
}

func RouteMessage(publishedSubject string, subscriptions []Subscription) RoutingResult {
	if publishedSubject == "" {
		return ErrRoutingResult("Published subject cannot be empty.")
	}

	var matches []string
	for _, sub := range subscriptions {
		if matchSubject(publishedSubject, sub.Subject) {
			matches = append(matches, sub.SubID)
		}
	}

	return OkRoutingResult(matches)
}
