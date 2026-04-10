//go:build windows

package net

import "os"

// registerPlatformSignals di Windows hanya mendukung os.Interrupt.
// Windows TIDAK memiliki SIGUSR2 atau SIGHUP di kernel-nya.
// Hot-swap di Windows dilakukan via: omni deploy --hot (via named pipe/API)
func registerPlatformSignals(sigChan chan<- os.Signal) {
	// Windows hanya support: os.Interrupt dan os.Kill
	// Tidak ada sinyal tambahan yang perlu didaftarkan
}

// isHotSwapSignal di Windows — semua sinyal dianggap shutdown.
// Untuk hot-swap, gunakan mekanisme file-based atau named pipe.
func isHotSwapSignal(sig os.Signal) bool {
	// Di Windows, kita tidak bisa membedakan sinyal
	// Hot-swap trigger via external mechanism (file watch / named pipe)
	return false
}
