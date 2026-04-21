// omni_multisoundchanger_engine.cs
// Production-Grade Multi-Device Audio Routing Engine
// ==============================================================
// Absorbed from: rlxone/MultiSoundChanger
//
// OMNI Layer: domain/csharp_core
// @since 2026.4.0

using System;
using System.Collections.Generic;
using System.Linq;

namespace OmniFramework.Domain.AudioRouting
{
    public const string EngineVersion = "1.0.0-omni";

    /// <summary>
    /// Error types for audio routing operations.
    /// </summary>
    public class AudioRoutingException : Exception
    {
        public string Code { get; }
        public AudioRoutingException(string code, string message) : base(message)
        {
            Code = code;
        }
    }

    /// <summary>
    /// Represents an audio device with capabilities.
    /// </summary>
    public class AudioDevice
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Type { get; set; } // "output", "input", "duplex"
        public int SampleRate { get; set; }
        public int Channels { get; set; }
        public int BitDepth { get; set; }
        public float Volume { get; set; }
        public bool IsMuted { get; set; }
        public bool IsDefault { get; set; }
        public bool IsActive { get; set; }
    }

    /// <summary>
    /// Represents an audio routing rule.
    /// </summary>
    public class RoutingRule
    {
        public string Id { get; set; }
        public string SourceDeviceId { get; set; }
        public string TargetDeviceId { get; set; }
        public float GainDb { get; set; }
        public bool Enabled { get; set; }
        public string Description { get; set; }
    }

    /// <summary>
    /// Production-grade multi-device audio routing engine.
    ///
    /// Manages audio device discovery, volume control across
    /// multiple outputs, routing rules, and default device
    /// switching for multi-monitor/multi-speaker setups.
    /// </summary>
    public class OmniMultisoundchangerEngine
    {
        private readonly Dictionary<string, AudioDevice> _devices;
        private readonly Dictionary<string, RoutingRule> _rules;
        private string _defaultOutputId;
        private string _defaultInputId;
        private readonly int _maxDevices;

        public OmniMultisoundchangerEngine(int maxDevices = 32)
        {
            _devices = new Dictionary<string, AudioDevice>();
            _rules = new Dictionary<string, RoutingRule>();
            _maxDevices = maxDevices;
        }

        /// <summary>
        /// Register an audio device.
        /// </summary>
        public Dictionary<string, object> RegisterDevice(AudioDevice device)
        {
            if (string.IsNullOrEmpty(device.Id))
                throw new AudioRoutingException("INVALID_ID", "Device ID cannot be empty");
            if (_devices.Count >= _maxDevices)
                throw new AudioRoutingException("MAX_DEVICES", $"Maximum {_maxDevices} devices reached");

            _devices[device.Id] = device;

            if (device.IsDefault && device.Type == "output")
                _defaultOutputId = device.Id;
            if (device.IsDefault && device.Type == "input")
                _defaultInputId = device.Id;

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "deviceId", device.Id },
                { "name", device.Name },
                { "type", device.Type },
                { "totalDevices", _devices.Count }
            };
        }

        /// <summary>
        /// Set the default output device.
        /// </summary>
        public Dictionary<string, object> SetDefaultOutput(string deviceId)
        {
            if (!_devices.ContainsKey(deviceId))
                throw new AudioRoutingException("NOT_FOUND", $"Device '{deviceId}' not found");

            var device = _devices[deviceId];
            if (device.Type != "output" && device.Type != "duplex")
                throw new AudioRoutingException("INVALID_TYPE", "Device must be output or duplex");

            // Clear previous default
            foreach (var d in _devices.Values)
            {
                if (d.Type == "output" || d.Type == "duplex")
                    d.IsDefault = false;
            }

            device.IsDefault = true;
            _defaultOutputId = deviceId;

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "defaultOutput", deviceId },
                { "name", device.Name }
            };
        }

        /// <summary>
        /// Set volume for a device.
        /// </summary>
        public Dictionary<string, object> SetDeviceVolume(string deviceId, float volume)
        {
            if (!_devices.ContainsKey(deviceId))
                throw new AudioRoutingException("NOT_FOUND", $"Device '{deviceId}' not found");
            if (volume < 0f || volume > 1f)
                throw new AudioRoutingException("INVALID_VOLUME", "Volume must be [0, 1]");

            _devices[deviceId].Volume = volume;

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "deviceId", deviceId },
                { "volume", Math.Round(volume, 4) }
            };
        }

        /// <summary>
        /// Set volume for ALL output devices simultaneously.
        /// </summary>
        public Dictionary<string, object> SetGlobalVolume(float volume)
        {
            if (volume < 0f || volume > 1f)
                throw new AudioRoutingException("INVALID_VOLUME", "Volume must be [0, 1]");

            int count = 0;
            foreach (var device in _devices.Values)
            {
                if (device.Type == "output" || device.Type == "duplex")
                {
                    device.Volume = volume;
                    count++;
                }
            }

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "volume", Math.Round(volume, 4) },
                { "devicesAffected", count }
            };
        }

        /// <summary>
        /// Toggle mute for a device.
        /// </summary>
        public Dictionary<string, object> ToggleMute(string deviceId)
        {
            if (!_devices.ContainsKey(deviceId))
                throw new AudioRoutingException("NOT_FOUND", $"Device '{deviceId}' not found");

            _devices[deviceId].IsMuted = !_devices[deviceId].IsMuted;

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "deviceId", deviceId },
                { "muted", _devices[deviceId].IsMuted }
            };
        }

        /// <summary>
        /// Add a routing rule between devices.
        /// </summary>
        public Dictionary<string, object> AddRoutingRule(RoutingRule rule)
        {
            if (string.IsNullOrEmpty(rule.Id))
                throw new AudioRoutingException("INVALID_ID", "Rule ID cannot be empty");
            if (!_devices.ContainsKey(rule.SourceDeviceId))
                throw new AudioRoutingException("SOURCE_NOT_FOUND", $"Source '{rule.SourceDeviceId}' not found");
            if (!_devices.ContainsKey(rule.TargetDeviceId))
                throw new AudioRoutingException("TARGET_NOT_FOUND", $"Target '{rule.TargetDeviceId}' not found");

            _rules[rule.Id] = rule;

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "ruleId", rule.Id },
                { "source", rule.SourceDeviceId },
                { "target", rule.TargetDeviceId },
                { "gainDb", Math.Round(rule.GainDb, 2) },
                { "totalRules", _rules.Count }
            };
        }

        /// <summary>
        /// List all registered devices.
        /// </summary>
        public Dictionary<string, object> ListDevices(string typeFilter = null)
        {
            var filtered = _devices.Values.AsEnumerable();
            if (!string.IsNullOrEmpty(typeFilter))
                filtered = filtered.Where(d => d.Type == typeFilter);

            var deviceList = filtered.Select(d => new Dictionary<string, object>
            {
                { "id", d.Id },
                { "name", d.Name },
                { "type", d.Type },
                { "volume", Math.Round(d.Volume, 4) },
                { "muted", d.IsMuted },
                { "isDefault", d.IsDefault },
                { "sampleRate", d.SampleRate },
                { "channels", d.Channels }
            }).ToList();

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "devices", deviceList },
                { "count", deviceList.Count },
                { "defaultOutput", _defaultOutputId ?? "none" },
                { "defaultInput", _defaultInputId ?? "none" }
            };
        }

        /// <summary>
        /// Get engine statistics.
        /// </summary>
        public Dictionary<string, object> GetStats()
        {
            int outputs = _devices.Values.Count(d => d.Type == "output" || d.Type == "duplex");
            int inputs = _devices.Values.Count(d => d.Type == "input" || d.Type == "duplex");
            int muted = _devices.Values.Count(d => d.IsMuted);
            int activeRules = _rules.Values.Count(r => r.Enabled);

            return new Dictionary<string, object>
            {
                { "status", "success" },
                { "totalDevices", _devices.Count },
                { "outputDevices", outputs },
                { "inputDevices", inputs },
                { "mutedDevices", muted },
                { "routingRules", _rules.Count },
                { "activeRules", activeRules }
            };
        }
    }
}
