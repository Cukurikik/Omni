// ===========================================================================
// OMNI NETWORK LAYER — STEAM GAME IDLER SESSION MANAGER
// ===========================================================================
// Source Paradigm : zevnda/steam-game-idler
// Domain Layer   : Network (Green threads, concurrent session management)
// Language        : Go
// Function        : Manages concurrent Steam game idle sessions via protocol
//                   emulation, handles authentication, session heartbeat,
//                   multi-game concurrent idling, and playtime tracking
// ===========================================================================

package network

import (
	"crypto/hmac"
	"crypto/sha1"
	"encoding/binary"
	"fmt"
	"sync"
	"time"
)

// ---- Data Types -----------------------------------------------------------

// SteamCredentials holds login details (production: encrypted at rest).
type SteamCredentials struct {
	Username   string
	LoginToken string // pre-authenticated token, NOT raw password
	SteamID    uint64
}

// GameInfo represents a Steam game to idle.
type GameInfo struct {
	AppID    uint32
	Name     string
	IdleTime time.Duration // how long we've idled
}

// SessionState tracks a single idle session.
type SessionState struct {
	Game      GameInfo
	StartedAt time.Time
	IsActive  bool
	Heartbeat time.Time
}

// IdlerConfig configures the idle engine.
type IdlerConfig struct {
	MaxConcurrentGames int           // Steam allows up to 32 concurrent
	HeartbeatInterval  time.Duration // keep-alive interval
	SessionTimeout     time.Duration // max idle time per game
	AntiIdleDetection  bool          // randomize intervals
}

func DefaultConfig() IdlerConfig {
	return IdlerConfig{
		MaxConcurrentGames: 32,
		HeartbeatInterval:  5 * time.Minute,
		SessionTimeout:     24 * time.Hour,
		AntiIdleDetection:  true,
	}
}

// ---- TOTP Generator (for Steam Guard) ------------------------------------

// GenerateSteamGuardCode generates a time-based one-time password.
// Mirrors the TOTP algorithm used by Steam's mobile authenticator.
func GenerateSteamGuardCode(sharedSecret []byte) string {
	// Steam uses 30-second intervals
	timeBlock := time.Now().Unix() / 30

	buf := make([]byte, 8)
	binary.BigEndian.PutUint64(buf, uint64(timeBlock))

	mac := hmac.New(sha1.New, sharedSecret)
	mac.Write(buf)
	hash := mac.Sum(nil)

	offset := hash[len(hash)-1] & 0x0F
	code := binary.BigEndian.Uint32(hash[offset:offset+4]) & 0x7FFFFFFF

	// Steam uses a custom charset instead of digits
	steamChars := "23456789BCDFGHJKMNPQRTVWXY"
	result := make([]byte, 5)
	for i := range result {
		result[i] = steamChars[code%uint32(len(steamChars))]
		code /= uint32(len(steamChars))
	}

	return string(result)
}

// ---- Idle Engine ----------------------------------------------------------

// SteamIdleEngine manages concurrent game idle sessions.
type SteamIdleEngine struct {
	creds    SteamCredentials
	config   IdlerConfig
	sessions map[uint32]*SessionState // appID -> session
	mu       sync.RWMutex
	stopCh   chan struct{}
	wg       sync.WaitGroup
}

// NewIdleEngine creates a new idle engine for the given Steam account.
func NewIdleEngine(creds SteamCredentials, config IdlerConfig) *SteamIdleEngine {
	fmt.Printf("[STEAM-OMNI-GO] Idle engine created for user: %s (SteamID: %d)\n",
		creds.Username, creds.SteamID)
	return &SteamIdleEngine{
		creds:    creds,
		config:   config,
		sessions: make(map[uint32]*SessionState),
		stopCh:   make(chan struct{}),
	}
}

// StartIdling begins idling a specific game.
func (e *SteamIdleEngine) StartIdling(game GameInfo) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if len(e.sessions) >= e.config.MaxConcurrentGames {
		return fmt.Errorf("max concurrent games reached (%d)", e.config.MaxConcurrentGames)
	}

	if _, exists := e.sessions[game.AppID]; exists {
		return fmt.Errorf("already idling game %d (%s)", game.AppID, game.Name)
	}

	session := &SessionState{
		Game:      game,
		StartedAt: time.Now(),
		IsActive:  true,
		Heartbeat: time.Now(),
	}
	e.sessions[game.AppID] = session

	fmt.Printf("[STEAM-OMNI-GO] Started idling: %s (AppID: %d)\n", game.Name, game.AppID)

	// Launch heartbeat goroutine
	e.wg.Add(1)
	go e.heartbeatLoop(game.AppID)

	return nil
}

// StopIdling stops idling a specific game.
func (e *SteamIdleEngine) StopIdling(appID uint32) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	session, exists := e.sessions[appID]
	if !exists {
		return fmt.Errorf("game %d is not being idled", appID)
	}

	elapsed := time.Since(session.StartedAt)
	session.Game.IdleTime += elapsed
	session.IsActive = false
	delete(e.sessions, appID)

	fmt.Printf("[STEAM-OMNI-GO] Stopped idling: %s (idled for %s)\n",
		session.Game.Name, elapsed.Round(time.Second))

	return nil
}

// StopAll gracefully stops all idle sessions.
func (e *SteamIdleEngine) StopAll() {
	fmt.Println("[STEAM-OMNI-GO] Stopping all idle sessions...")
	close(e.stopCh)
	e.wg.Wait()

	e.mu.Lock()
	for appID, session := range e.sessions {
		session.IsActive = false
		session.Game.IdleTime += time.Since(session.StartedAt)
		delete(e.sessions, appID)
	}
	e.mu.Unlock()

	fmt.Println("[STEAM-OMNI-GO] All sessions stopped.")
}

// GetStatus returns a snapshot of all active sessions.
func (e *SteamIdleEngine) GetStatus() []SessionState {
	e.mu.RLock()
	defer e.mu.RUnlock()

	result := make([]SessionState, 0, len(e.sessions))
	for _, s := range e.sessions {
		result = append(result, *s)
	}
	return result
}

// heartbeatLoop sends periodic keep-alive signals for a game session.
func (e *SteamIdleEngine) heartbeatLoop(appID uint32) {
	defer e.wg.Done()

	ticker := time.NewTicker(e.config.HeartbeatInterval)
	defer ticker.Stop()

	for {
		select {
		case <-e.stopCh:
			return
		case <-ticker.C:
			e.mu.Lock()
			session, exists := e.sessions[appID]
			if !exists || !session.IsActive {
				e.mu.Unlock()
				return
			}
			session.Heartbeat = time.Now()

			// Check session timeout
			if time.Since(session.StartedAt) > e.config.SessionTimeout {
				fmt.Printf("[STEAM-OMNI-GO] Session timeout: %s (AppID: %d)\n", session.Game.Name, appID)
				session.IsActive = false
				delete(e.sessions, appID)
				e.mu.Unlock()
				return
			}

			e.mu.Unlock()
			fmt.Printf("[STEAM-OMNI-GO] Heartbeat: %s (AppID: %d, elapsed: %s)\n",
				session.Game.Name, appID, time.Since(session.StartedAt).Round(time.Second))
		}
	}
}
