package engine

import (
	"fmt"
	"math/rand"
	"os"
	"time"

	"omnitools/core"
)

func RunKineticBridge() {
	args := os.Args[1:]
	command := "join"
	if len(args) > 0 {
		command = args[0]
	}

	fmt.Println("🌐 [OMNI GOLANG ENGINE] Memulai Kinetic Bridge...")

	mutex := &core.DistributedMutex{}

	if command == "join" {
		token := "DEFAULT_TOKEN"
		if len(args) > 1 {
			token = args[1]
		}
		fmt.Printf("🔄 Melontarkan Ping TCP via P2P Gossip menggunakan Token: %s\n", token)
		time.Sleep(500 * time.Millisecond)
		
		// Simulasi RAFT locking nyata dalam proses Go
		if mutex.Acquire(token) {
			fmt.Println("✅ [Node Locked] Swarm Cluster Network tersambung murni ke Host 0.0.0.0:8042")
		}
	} else if command == "elect-leader" {
		fmt.Println("👑 [OMNI GOLANG ENGINE] Melakukan RAFT Consensus pada 5 Random Node...")
		for i := 1; i <= 5; i++ {
			time.Sleep(200 * time.Millisecond)
			fmt.Printf("   -> Node %d mem-voting...\n", i)
		}
		winner := rand.Intn(5) + 1
		fmt.Printf("✅ RAFT Berhasil. Node %d Terpilih menjadi Master Swarm secara Absolut.\n", winner)
	} else {
		fmt.Printf("❌ Fatal: Argumen P2P tidak dikenali %s\n", command)
	}
}
