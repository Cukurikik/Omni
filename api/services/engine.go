package services

import (
	"bytes"
	"context"
	"fmt"
	"os/exec"
	"runtime"
	"strings"
	"time"

	"omnitools/core"
)

// ==========================================
// PISAU GUILLOTINE & ALGOJO RAM (Eksekutor C++/Python dengan Timeout dan RAM Limit)
// ==========================================
// Fungsi ini menggantikan exec.Command biasa. Jika C++ atau Python
// memakan waktu lebih dari batas, Golang akan memenggal prosesnya!
// Jika proses memakan lebih dari 2GB RAM (di Linux), OS akan membunuhnya!
func ExecuteEngineWithTimeout(enginePath string, args []string, timeout time.Duration) ([]byte, error) {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel() // Wajib agar memori timer dibebaskan

	// 🔥 OMNI ENGINE RESOLVER: Jika ffmpeg tidak ada di PATH, gunakan jalur dari config
	if enginePath == "ffmpeg" {
		if core.Config != nil && core.Config.FFmpegPath != "" {
			WriteLog("ENGINE", "INFO_RESOLVE", fmt.Sprintf("Meresolusi 'ffmpeg' -> %s", core.Config.FFmpegPath))
			enginePath = core.Config.FFmpegPath
		} else {
			status := "Config=nil"
			if core.Config != nil {
				status = "FFmpegPath=kosong"
			}
			WriteLog("ENGINE", "WARN_RESOLVE", fmt.Sprintf("Gagal meresolusi 'ffmpeg' (%s). Menggunakan default PATH.", status))
		}
	}

	WriteLog("ENGINE", "INFO_EXEC", fmt.Sprintf("Menjalankan %s %s", enginePath, strings.Join(args, " ")))

	var cmd *exec.Cmd

	// 1. CEK DISTRIBUTED NODE (Remote Slave Check)
	remoteHost := GetNextNode()

	if remoteHost != "" {
		// THE MULTIPLIER: Menerbangkan tugas mematikan ini ke Slave Node via SSH!
		// Asumsi Arsitektur: Folder /omni_cache/ dan /omni_quarantine/ sudah menjadi NFS/NAS Shared Drive.
		var remoteCmdStr string
		if runtime.GOOS == "linux" {
			remoteCmdStr = fmt.Sprintf("unshare --user --map-root-user --net --pid --fork --mount-proc prlimit --as=2147483648 %s %s", enginePath, strings.Join(args, " "))
		} else {
			remoteCmdStr = fmt.Sprintf("%s %s", enginePath, strings.Join(args, " "))
		}

		sshArgs := []string{
			"-o", "StrictHostKeyChecking=no", // Bebas rewel login ssh di Docker
			"-o", "PasswordAuthentication=no", // Pastikan key public / Private key OMNI terpasang (IdentityFile)
			fmt.Sprintf("root@%s", remoteHost),
			remoteCmdStr,
		}

		cmd = exec.CommandContext(ctx, "ssh", sshArgs...)
		WriteLog("CLUSTER", "INFO_REMOTE_EXEC", fmt.Sprintf("Mendelegasikan %s ke Slave [%s]", enginePath, remoteHost))
	} else {
		// 2. EKSEKUSI LOKAL NORMAL (Jika Belum Ada Jaringan Cluster)
		if runtime.GOOS == "linux" {
			// THE EXECUTIONER + THE CAGE (OOM Guard & OS-Level Sandboxing via Seccomp-BPF)
			var guardedArgs []string
			var guardedBinary string

			// Mengaktifkan The Kernel Sheriff (Read-Only RootFS & Drop Syscalls)
			guardedArgs, guardedBinary = GetSecuredBPFCommand(enginePath, args)

			cmd = exec.CommandContext(ctx, "prlimit", append([]string{"--as=2147483648", guardedBinary}, guardedArgs...)...)
			WriteLog("ENGINE", "INFO_SEC_SANDBOX", fmt.Sprintf("The Cage & BPF Guard mengunci %s dengan RAM limit 2GB", enginePath))
		} else {
			// OS Windows / macOS (Development mode)
			cmd = exec.CommandContext(ctx, enginePath, args...)
		}
	}

	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	err := cmd.Run()

	// Jika proses dipenggal karena melewati batas waktu (Timeout)
	if ctx.Err() == context.DeadlineExceeded {
		WriteLog("ENGINE", "ERR_TIMEOUT", "Proses "+enginePath+" dipenggal karena melebihi batas waktu!")
		return nil, fmt.Errorf("timeout exceeded: proses %s melampaui batas %v", enginePath, timeout)
	}

	if err != nil {
		outStr := string(out.Bytes())
		if len(outStr) > 500 {
			outStr = outStr[len(outStr)-500:] // Keep last 500 chars
		}
		WriteLog("ENGINE", "ERR_ENGINE_CRASH", fmt.Sprintf("Engine %s crash: %v\nOutput: %s", enginePath, err, outStr))
		return out.Bytes(), fmt.Errorf("engine crash: %v - %s", err, outStr)
	}

	return out.Bytes(), nil
}
