using System;
using System.Collections.Generic;

namespace Omni.Business.CVCuda
{
    public class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T data) { Data = data; }
        public OmniResult(string error) { Error = error; }
    }

    public class VisionPipelineConfig
    {
        public int MaxFPS { get; set; }
        public bool EnableHardwareAcceleration { get; set; }
        public List<string> ActiveFilters { get; set; }
    }

    public class PipelineManager
    {
        private VisionPipelineConfig _config;

        public PipelineManager(VisionPipelineConfig config)
        {
            _config = config;
        }

        public OmniResult<bool> ValidateFramePayload(byte[] frameData, int width, int height)
        {
            if (frameData == null || frameData.Length == 0)
            {
                return new OmniResult<bool>("Frame data cannot be null or empty.");
            }

            int expectedSize = width * height * 3; // Assuming RGB
            if (frameData.Length != expectedSize)
            {
                return new OmniResult<bool>($"Frame size mismatch. Expected {expectedSize}, got {frameData.Length}.");
            }

            if (_config.MaxFPS > 120)
            {
                 return new OmniResult<bool>("Max FPS exceeds hardware limits (120).");
            }

            return new OmniResult<bool>(true);
        }

        public OmniResult<string> RouteToComputeNode(string streamId)
        {
            if (string.IsNullOrEmpty(streamId))
            {
                return new OmniResult<string>("Invalid Stream ID.");
            }
            
            // Hashing logic to route stream to specific GPU node
            int hash = streamId.GetHashCode();
            int nodeIdx = Math.Abs(hash) % 4; // Assuming 4 GPU nodes
            
            return new OmniResult<string>($"gpu-node-{nodeIdx}");
        }
    }
}
