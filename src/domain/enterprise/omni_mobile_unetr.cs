using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace Omni.Business.Healthcare
{
    /// <summary>
    /// MobileUNETR: A Lightweight End-To-End Hybrid Vision Transformer For Efficient Medical Image Segmentation.
    /// Business Layer C# orchestrator interfacing with DICOM protocols and Omni medical imaging pipelines.
    /// </summary>
    public class MobileUNETR_Segmentation
    {
        // P/Invoke into the Omni Universal Binary for hardware-accelerated UNETR execution
        [DllImport("omni_universal_binary.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr Omni_ExecuteMobileUNETR(IntPtr imageData, int width, int height, int depth);

        [DllImport("omni_universal_binary.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern void Omni_FreeBuffer(IntPtr buffer);

        /// <summary>
        /// Process 3D Medical Scan (e.g., MRI/CT) using MobileUNETR.
        /// Zero-Copy pinning using unsafe blocks.
        /// </summary>
        public float[] SegmentLesion(float[] voxelData, int width, int height, int depth)
        {
            if (voxelData.Length != width * height * depth)
            {
                throw new ArgumentException("Voxel data dimensions do not match.");
            }

            // Zero-copy array pinning to prevent GC from moving memory during C-ABI execution
            unsafe
            {
                fixed (float* pVoxel = voxelData)
                {
                    IntPtr resultPtr = Omni_ExecuteMobileUNETR((IntPtr)pVoxel, width, height, depth);

                    if (resultPtr == IntPtr.Zero)
                    {
                        throw new InvalidOperationException("Omni Engine failed to execute segmentation.");
                    }

                    // Extract segmentation mask results
                    float[] segmentationMask = new float[voxelData.Length];
                    Marshal.Copy(resultPtr, segmentationMask, 0, voxelData.Length);
                    
                    // Cleanup C-allocated memory
                    Omni_FreeBuffer(resultPtr);

                    return segmentationMask;
                }
            }
        }

        public double CalculateVolume(float[] mask, double voxelSpacingMM3)
        {
            double volume = 0;
            foreach(var prob in mask)
            {
                if (prob > 0.5f) volume += voxelSpacingMM3;
            }
            return volume;
        }
    }
}
