package core

import (
	"os"
	"path/filepath"
)

// ResolveConfigPath mencari file konfigurasi secara cerdas di berbagai lokasi
// Prioritas: ./configs/ -> ../configs/ -> (ExecutableDir)/configs/
func ResolveConfigPath(filename string) string {
	// 1. Cek di ./configs/ (Jika dijalankan dari ROOT Proyek)
	localPath := filepath.Join("configs", filename)
	if _, err := os.Stat(localPath); err == nil {
		return localPath
	}

	// 2. Cek di ../configs/ (Jika dijalankan dari api/ atau bin/)
	parentPath := filepath.Join("..", "configs", filename)
	if _, err := os.Stat(parentPath); err == nil {
		return parentPath
	}

	// 3. Fallback: Cari relatif terhadap binary executable
	exePath, err := os.Executable()
	if err == nil {
		exeDir := filepath.Dir(exePath)
		binaryRelPath := filepath.Join(exeDir, "configs", filename)
		if _, err := os.Stat(binaryRelPath); err == nil {
			return binaryRelPath
		}
		
		binaryRelParentPath := filepath.Join(exeDir, "..", "configs", filename)
		if _, err := os.Stat(binaryRelParentPath); err == nil {
			return binaryRelParentPath
		}
	}

	return localPath
}

// ResolveLogPath mencari folder logs secara cerdas
func ResolveLogPath() string {
	// 1. Cek ./logs/
	if _, err := os.Stat("logs"); err == nil {
		return "logs"
	}

	// 2. Cek ../logs/
	if _, err := os.Stat("../logs"); err == nil {
		return "../logs"
	}

	// 3. Fallback: Cari relatif terhadap binary executable
	exePath, err := os.Executable()
	if err == nil {
		exeDir := filepath.Dir(exePath)
		binaryRelPath := filepath.Join(exeDir, "logs")
		if _, err := os.Stat(binaryRelPath); err == nil {
			return binaryRelPath
		}
		
		binaryRelParentPath := filepath.Join(exeDir, "..", "logs")
		if _, err := os.Stat(binaryRelParentPath); err == nil {
			return binaryRelParentPath
		}
	}

	// Jika tidak ada, buat saja di current directory ./logs
	os.MkdirAll("logs", 0755)
	return "logs"
}

// dirExists checks whether a directory exists
func dirExists(path string) bool {
	info, err := os.Stat(path)
	if os.IsNotExist(err) {
		return false
	}
	return info.IsDir()
}
