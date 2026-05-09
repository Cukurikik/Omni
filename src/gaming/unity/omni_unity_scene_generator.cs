using UnityEngine;
using System.Runtime.InteropServices;
using System.Collections.Generic;

namespace Omni.Simulation
{
    /// <summary>
    /// OMNI Game & Simulation Layer
    /// Unity C# script that bridges NeRF/GAMBA volumetric outputs from the Omni Universal Binary
    /// into dynamic Unity Mesh and Compute Buffer representations.
    /// </summary>
    public class OmniSceneGenerator : MonoBehaviour
    {
        [StructLayout(LayoutKind.Sequential)]
        public struct GaussianSplatData
        {
            public Vector3 position;
            public Vector3 scale;
            public Color color;
            public float opacity;
        }

        [DllImport("omni_universal_binary", CallingConvention = CallingConvention.Cdecl)]
        private static extern int Omni_FetchGambaSplats(out System.IntPtr splatDataPtr);

        [DllImport("omni_universal_binary", CallingConvention = CallingConvention.Cdecl)]
        private static extern void Omni_FreeGambaSplats(System.IntPtr splatDataPtr);

        private ComputeBuffer splatBuffer;
        public Material splatRenderingMaterial;

        void Start()
        {
            GenerateScene();
        }

        void GenerateScene()
        {
            System.IntPtr ptr = System.IntPtr.Zero;
            int numSplats = Omni_FetchGambaSplats(out ptr);

            if (numSplats > 0 && ptr != System.IntPtr.Zero)
            {
                int structSize = Marshal.SizeOf(typeof(GaussianSplatData));
                GaussianSplatData[] splats = new GaussianSplatData[numSplats];
                
                // Zero-copy mapping requires unsafe blocks, but for Unity ComputeBuffers we marshal.
                System.IntPtr currentPtr = ptr;
                for (int i = 0; i < numSplats; i++)
                {
                    splats[i] = Marshal.PtrToStructure<GaussianSplatData>(currentPtr);
                    currentPtr += structSize;
                }

                splatBuffer = new ComputeBuffer(numSplats, structSize);
                splatBuffer.SetData(splats);

                splatRenderingMaterial.SetBuffer("_SplatBuffer", splatBuffer);

                Omni_FreeGambaSplats(ptr);
            }
        }

        void OnRenderObject()
        {
            if (splatBuffer != null)
            {
                splatRenderingMaterial.SetPass(0);
                Graphics.DrawProceduralNow(MeshTopology.Points, splatBuffer.count);
            }
        }

        void OnDestroy()
        {
            splatBuffer?.Release();
        }
    }
}
