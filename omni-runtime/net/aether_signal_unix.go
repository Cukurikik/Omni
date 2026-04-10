//go:build !windows

package net

import (
	"os"
	"os/signal"
	"syscall"
)

// registerPlatformSignals di Unix/Linux/Mac mendaftarkan SIGHUP dan SIGUSR2.
// SIGHUP = hot-swap trigger (cocok untuk daemon)
// SIGUSR2 = alternatif hot-swap trigger
func registerPlatformSignals(sigChan chan<- os.Signal) {
	signal.Notify(sigChan, syscall.SIGHUP, syscall.SIGUSR2, syscall.SIGTERM)
}

// isHotSwapSignal menentukan apakah sinyal ini adalah trigger hot-swap.
// SIGHUP atau SIGUSR2 = hot-swap
// SIGINT / SIGTERM = graceful shutdown
func isHotSwapSignal(sig os.Signal) bool {
	switch sig {
	case syscall.SIGHUP, syscall.SIGUSR2:
		return true
	default:
		return false
	}
}
