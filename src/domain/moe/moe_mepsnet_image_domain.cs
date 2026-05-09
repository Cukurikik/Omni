// moe_mepsnet_image_domain.cs — Domain
// Layer: Domain — MEPSNet Image Processing Validations
// Inspired by: MEPSNet_dev

using System;

namespace Omni.Domain.MoE
{
    public class MepsNetImageRequest
    {
        public Guid RequestId { get; private set; }
        public int Width { get; private set; }
        public int Height { get; private set; }
        public int Channels { get; private set; }

        public MepsNetImageRequest(int width, int height, int channels)
        {
            // Domain validation: Max 4K resolution to prevent GPU OOM
            if (width > 3840 || height > 2160)
            {
                throw new ArgumentException("Resolution exceeds maximum 4K limits.");
            }
            // Domain validation: Only RGB or RGBA
            if (channels != 3 && channels != 4)
            {
                throw new ArgumentException("Only 3-channel (RGB) or 4-channel (RGBA) supported.");
            }

            RequestId = Guid.NewGuid();
            Width = width;
            Height = height;
            Channels = channels;
        }

        public int GetTotalPixels() => Width * Height;
        public int GetBufferSize() => Width * Height * Channels;
    }
}
