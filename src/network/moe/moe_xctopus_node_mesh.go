// moe_xctopus_node_mesh.go — Network
// Layer: Network — P2P LoRA Node Mesh
// Inspired by: xctopus-core (Autonomous Knowledge Induction for LLMs)

package network_moe

import (
	"context"
	"fmt"
	"log"

	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/host"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/multiformats/go-multiaddr"
)

type XctopusMesh struct {
	Host host.Host
	Ctx  context.Context
}

// Initialize a libp2p node to share dynamic LoRA adapters across the cluster
func InitXctopusMesh(ctx context.Context, listenPort int) (*XctopusMesh, error) {
	addr, _ := multiaddr.NewMultiaddr(fmt.Sprintf("/ip4/0.0.0.0/tcp/%d", listenPort))

	node, err := libp2p.New(
		libp2p.ListenAddrs(addr),
	)
	if err != nil {
		return nil, err
	}

	log.Printf("[Xctopus Mesh] Node started. Peer ID: %s", node.ID().String())
	log.Printf("[Xctopus Mesh] Listening on: %v", node.Addrs())

	return &XctopusMesh{
		Host: node,
		Ctx:  ctx,
	}, nil
}

func (m *XctopusMesh) ConnectToPeer(peerAddr string) error {
	maddr, err := multiaddr.NewMultiaddr(peerAddr)
	if err != nil {
		return err
	}

	info, err := peer.AddrInfoFromP2pAddr(maddr)
	if err != nil {
		return err
	}

	err = m.Host.Connect(m.Ctx, *info)
	if err != nil {
		return fmt.Errorf("failed to connect to peer %s: %v", info.ID, err)
	}

	log.Printf("[Xctopus Mesh] Connected to LoRA cluster peer: %s", info.ID)
	return nil
}

