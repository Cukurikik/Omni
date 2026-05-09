// OMNI Engine — Container Builder for ML Training (Go)
// Learned from: UPwith-me/Container-Maker — Docker container platform for ML
// Implements: Dockerfile generation, GPU container config, volume mount planning
package concurrency

import (
	"errors"
	"fmt"
	"strings"
)

// ContainerConfig represents the configuration for an ML training container.
type ContainerConfig struct {
	BaseImage    string
	GPUEnabled   bool
	GPUCount     int
	VolumeMounts []VolumeMount
	EnvVars      map[string]string
	Command      []string
}

// VolumeMount represents a host-to-container volume mapping.
type VolumeMount struct {
	HostPath      string
	ContainerPath string
	ReadOnly      bool
}

// ContainerBuilder constructs ML training container specifications.
type ContainerBuilder struct {
	config ContainerConfig
}

// NewContainerBuilder creates a new builder with the given base image.
func NewContainerBuilder(baseImage string) (*ContainerBuilder, error) {
	if baseImage == "" {
		return nil, errors.New("OMNI_FATAL: base image cannot be empty")
	}
	return &ContainerBuilder{
		config: ContainerConfig{
			BaseImage: baseImage,
			EnvVars:   make(map[string]string),
		},
	}, nil
}

// WithGPU enables GPU support with the specified count.
func (b *ContainerBuilder) WithGPU(count int) *ContainerBuilder {
	b.config.GPUEnabled = true
	b.config.GPUCount = count
	return b
}

// AddVolume adds a volume mount to the container.
func (b *ContainerBuilder) AddVolume(hostPath, containerPath string, readOnly bool) *ContainerBuilder {
	b.config.VolumeMounts = append(b.config.VolumeMounts, VolumeMount{
		HostPath:      hostPath,
		ContainerPath: containerPath,
		ReadOnly:      readOnly,
	})
	return b
}

// SetEnv sets an environment variable.
func (b *ContainerBuilder) SetEnv(key, value string) *ContainerBuilder {
	b.config.EnvVars[key] = value
	return b
}

// GenerateDockerfile produces a valid Dockerfile string from the current config.
func (b *ContainerBuilder) GenerateDockerfile() string {
	var lines []string
	lines = append(lines, fmt.Sprintf("FROM %s", b.config.BaseImage))

	if b.config.GPUEnabled {
		lines = append(lines, "ENV NVIDIA_VISIBLE_DEVICES=all")
		lines = append(lines, "ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility")
	}

	for k, v := range b.config.EnvVars {
		lines = append(lines, fmt.Sprintf("ENV %s=%s", k, v))
	}

	for _, vol := range b.config.VolumeMounts {
		lines = append(lines, fmt.Sprintf("VOLUME %s", vol.ContainerPath))
	}

	if len(b.config.Command) > 0 {
		lines = append(lines, fmt.Sprintf("CMD %s", strings.Join(b.config.Command, " ")))
	}

	return strings.Join(lines, "\n")
}
