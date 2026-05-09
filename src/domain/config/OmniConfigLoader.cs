// OmniConfigLoader.cs — Typed Configuration Loader
// Inspired by: OMNI Omnifile.toml patterns
// Layer: Domain / C#
//
// Strongly-typed configuration loading from TOML/JSON/env
// with validation, defaults, and environment overlay.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Omni.Domain.Config
{
    public enum ConfigSource
    {
        File,
        Environment,
        Default,
        Override
    }

    public sealed class ConfigEntry<T>
    {
        public T Value { get; }
        public ConfigSource Source { get; }
        public string Key { get; }

        public ConfigEntry(string key, T value, ConfigSource source)
        {
            Key = key;
            Value = value;
            Source = source;
        }
    }

    public sealed class ValidationError
    {
        public string Field { get; }
        public string Message { get; }
        public string Severity { get; }

        public ValidationError(string field, string message, string severity = "error")
        {
            Field = field;
            Message = message;
            Severity = severity;
        }

        public override string ToString() => $"[{Severity.ToUpper()}] {Field}: {Message}";
    }

    public sealed class ModelConfig
    {
        [JsonPropertyName("model_name")]
        public string ModelName { get; set; } = "omni-base";

        [JsonPropertyName("hidden_dim")]
        public int HiddenDim { get; set; } = 768;

        [JsonPropertyName("num_heads")]
        public int NumHeads { get; set; } = 12;

        [JsonPropertyName("num_layers")]
        public int NumLayers { get; set; } = 12;

        [JsonPropertyName("vocab_size")]
        public int VocabSize { get; set; } = 32000;

        [JsonPropertyName("max_seq_length")]
        public int MaxSeqLength { get; set; } = 2048;

        [JsonPropertyName("dropout")]
        public double Dropout { get; set; } = 0.1;

        [JsonPropertyName("ff_multiplier")]
        public int FFMultiplier { get; set; } = 4;

        [JsonPropertyName("precision")]
        public string Precision { get; set; } = "bf16";
    }

    public sealed class TrainingConfig
    {
        [JsonPropertyName("learning_rate")]
        public double LearningRate { get; set; } = 3e-4;

        [JsonPropertyName("batch_size")]
        public int BatchSize { get; set; } = 32;

        [JsonPropertyName("warmup_steps")]
        public int WarmupSteps { get; set; } = 1000;

        [JsonPropertyName("total_steps")]
        public int TotalSteps { get; set; } = 100000;

        [JsonPropertyName("grad_accum_steps")]
        public int GradAccumSteps { get; set; } = 1;

        [JsonPropertyName("weight_decay")]
        public double WeightDecay { get; set; } = 0.01;

        [JsonPropertyName("max_grad_norm")]
        public double MaxGradNorm { get; set; } = 1.0;

        [JsonPropertyName("scheduler")]
        public string Scheduler { get; set; } = "cosine";

        [JsonPropertyName("seed")]
        public int Seed { get; set; } = 42;
    }

    public sealed class InferenceConfig
    {
        [JsonPropertyName("max_batch_size")]
        public int MaxBatchSize { get; set; } = 64;

        [JsonPropertyName("max_sequence_length")]
        public int MaxSequenceLength { get; set; } = 2048;

        [JsonPropertyName("temperature")]
        public double Temperature { get; set; } = 1.0;

        [JsonPropertyName("top_k")]
        public int TopK { get; set; } = 50;

        [JsonPropertyName("top_p")]
        public double TopP { get; set; } = 0.9;

        [JsonPropertyName("quantization")]
        public string Quantization { get; set; } = "none";

        [JsonPropertyName("device")]
        public string Device { get; set; } = "cuda:0";
    }

    public sealed class OmniConfig
    {
        [JsonPropertyName("model")]
        public ModelConfig Model { get; set; } = new();

        [JsonPropertyName("training")]
        public TrainingConfig Training { get; set; } = new();

        [JsonPropertyName("inference")]
        public InferenceConfig Inference { get; set; } = new();

        [JsonPropertyName("metadata")]
        public Dictionary<string, string> Metadata { get; set; } = new();
    }

    public sealed class OmniConfigLoader
    {
        private readonly Dictionary<string, string> _envOverrides = new();
        private readonly List<ValidationError> _errors = new();

        public OmniConfig LoadFromFile(string path)
        {
            if (!File.Exists(path))
            {
                throw new FileNotFoundException($"Config file not found: {path}");
            }

            var json = File.ReadAllText(path);
            var config = JsonSerializer.Deserialize<OmniConfig>(json,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
                ?? new OmniConfig();

            ApplyEnvironmentOverrides(config);
            return config;
        }

        public OmniConfig LoadFromJson(string json)
        {
            var config = JsonSerializer.Deserialize<OmniConfig>(json,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
                ?? new OmniConfig();

            ApplyEnvironmentOverrides(config);
            return config;
        }

        public OmniConfig LoadDefault()
        {
            var config = new OmniConfig();
            ApplyEnvironmentOverrides(config);
            return config;
        }

        public void AddEnvironmentOverride(string key, string value)
        {
            _envOverrides[key] = value;
        }

        private void ApplyEnvironmentOverrides(OmniConfig config)
        {
            // Check environment variables
            var envLR = GetEnvOrOverride("OMNI_LEARNING_RATE");
            if (envLR != null && double.TryParse(envLR, out var lr))
                config.Training.LearningRate = lr;

            var envBS = GetEnvOrOverride("OMNI_BATCH_SIZE");
            if (envBS != null && int.TryParse(envBS, out var bs))
                config.Training.BatchSize = bs;

            var envDevice = GetEnvOrOverride("OMNI_DEVICE");
            if (envDevice != null)
                config.Inference.Device = envDevice;

            var envPrecision = GetEnvOrOverride("OMNI_PRECISION");
            if (envPrecision != null)
                config.Model.Precision = envPrecision;

            var envSeed = GetEnvOrOverride("OMNI_SEED");
            if (envSeed != null && int.TryParse(envSeed, out var seed))
                config.Training.Seed = seed;
        }

        private string? GetEnvOrOverride(string key)
        {
            if (_envOverrides.TryGetValue(key, out var val))
                return val;
            return Environment.GetEnvironmentVariable(key);
        }

        public List<ValidationError> Validate(OmniConfig config)
        {
            _errors.Clear();

            // Model validation
            if (config.Model.HiddenDim <= 0)
                _errors.Add(new ValidationError("model.hidden_dim", "Must be positive"));
            if (config.Model.HiddenDim % config.Model.NumHeads != 0)
                _errors.Add(new ValidationError("model.hidden_dim",
                    $"Must be divisible by num_heads ({config.Model.NumHeads})"));
            if (config.Model.NumLayers <= 0)
                _errors.Add(new ValidationError("model.num_layers", "Must be positive"));
            if (!new[] { "fp32", "fp16", "bf16" }.Contains(config.Model.Precision))
                _errors.Add(new ValidationError("model.precision",
                    $"Invalid precision: {config.Model.Precision}"));

            // Training validation
            if (config.Training.LearningRate <= 0 || config.Training.LearningRate > 0.1)
                _errors.Add(new ValidationError("training.learning_rate",
                    "Must be in range (0, 0.1]"));
            if (config.Training.BatchSize <= 0)
                _errors.Add(new ValidationError("training.batch_size", "Must be positive"));
            if (config.Training.WarmupSteps >= config.Training.TotalSteps)
                _errors.Add(new ValidationError("training.warmup_steps",
                    "Must be less than total_steps"));
            if (config.Training.Dropout < 0 || config.Training.Dropout > 0.5)
                _errors.Add(new ValidationError("training.dropout",
                    "Must be in range [0, 0.5]", "warning"));

            // Memory estimation
            long paramCount = EstimateParams(config.Model);
            double modelSizeGB = paramCount * (config.Model.Precision == "fp32" ? 4.0 : 2.0) / 1e9;
            if (modelSizeGB > 80)
                _errors.Add(new ValidationError("memory",
                    $"Estimated model size ({modelSizeGB:F1} GB) exceeds typical GPU memory",
                    "warning"));

            return _errors;
        }

        public static long EstimateParams(ModelConfig model)
        {
            long d = model.HiddenDim;
            long ff = d * model.FFMultiplier;
            long attnParams = 4 * d * d;
            long ffnParams = 3 * d * ff;
            long layerParams = attnParams + ffnParams + 4 * d;
            long embedParams = model.VocabSize * d;
            return model.NumLayers * layerParams + 2 * embedParams;
        }

        public string ToJson(OmniConfig config)
        {
            return JsonSerializer.Serialize(config, new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            });
        }
    }
}
