// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Fastify Radix Router (OMNI Zero-Mock Implementation)
// Implements Radix Tree (Trie) path insertion and routing abstraction.

package compute

import (
	"errors"
	"strings"
)

type RouterResult struct {
	Value string
	Error error
}

func OkRouterResult(val string) RouterResult {
	return RouterResult{Value: val, Error: nil}
}

func ErrRouterResult(err string) RouterResult {
	return RouterResult{Value: "", Error: errors.New(err)}
}

type Node struct {
	path     string
	isHandle bool
	handler  string
	children []*Node
}

type FastifyRadixTree struct {
	root *Node
}

func NewFastifyRadixTree() *FastifyRadixTree {
	return &FastifyRadixTree{
		root: &Node{path: "/", isHandle: false},
	}
}

func (t *FastifyRadixTree) Insert(path string, handler string) {
	if path == "/" {
		t.root.isHandle = true
		t.root.handler = handler
		return
	}

	parts := strings.Split(strings.Trim(path, "/"), "/")
	curr := t.root

	for _, part := range parts {
		found := false
		for _, child := range curr.children {
			if child.path == part {
				curr = child
				found = true
				break
			}
		}

		if !found {
			newNode := &Node{path: part, isHandle: false}
			curr.children = append(curr.children, newNode)
			curr = newNode
		}
	}
	curr.isHandle = true
	curr.handler = handler
}

func (t *FastifyRadixTree) Lookup(path string) RouterResult {
	if path == "/" {
		if t.root.isHandle {
			return OkRouterResult(t.root.handler)
		}
		return ErrRouterResult("404 Not Found")
	}

	parts := strings.Split(strings.Trim(path, "/"), "/")
	curr := t.root

	for _, part := range parts {
		found := false
		for _, child := range curr.children {
			if child.path == part {
				curr = child
				found = true
				break
			}
		}

		if !found {
			return ErrRouterResult("404 Not Found")
		}
	}

	if curr.isHandle {
		return OkRouterResult(curr.handler)
	}

	return ErrRouterResult("404 Not Found")
}
