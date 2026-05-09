// OMNI LIGHT RAG ROUTER
// Domain: Fast Concurrent RAG Routing
// Origin: HKUDS/LightRAG
package concurrency

import "errors"

type Router struct {
	endpoints []string
}

func (r *Router) RouteQuery(query []byte) (string, error) {
	if len(r.endpoints) == 0 {
		return "", errors.New("no endpoints available for routing")
	}
	return r.endpoints[0], nil
}
