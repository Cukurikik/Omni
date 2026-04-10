using System;
using System.Runtime.InteropServices;

// ============================================================
// OMNI C# Bridge — Enterprise DDD Nexus
// ============================================================
// Layer: Business (CQRS, DDD Aggregate, Domain Logic)
// Menggunakan P/Invoke bawaan .NET — TIDAK perlu NuGet eksternal.
// ============================================================

namespace OmniFramework.Stdlib
{
    /// <summary>
    /// Monadic Result dari kernel Rust — menggantikan try/catch.
    /// </summary>
    public readonly struct OmniResult<T>
    {
        public bool IsOk { get; }
        public T Value { get; }
        public string ErrorCode { get; }
        public string ErrorMessage { get; }

        private OmniResult(bool isOk, T value, string code, string msg)
        {
            IsOk = isOk;
            Value = value;
            ErrorCode = code;
            ErrorMessage = msg;
        }

        public static OmniResult<T> Ok(T value) =>
            new OmniResult<T>(true, value, null, null);

        public static OmniResult<T> Err(string code, string message) =>
            new OmniResult<T>(false, default, code, message);
    }

    /// <summary>
    /// Jembatan utama C# ↔ OMNI Kernel via P/Invoke.
    /// </summary>
    public static class OmniBridge
    {
        private const string OMNI_DLL = "omni_core";

        [DllImport(OMNI_DLL, CallingConvention = CallingConvention.Cdecl, EntryPoint = "__omni_ffi")]
        private static extern IntPtr OmniFfi(IntPtr argsBuffer, UIntPtr length);

        /// <summary>
        /// Eksekusi fungsi OMNI via C-ABI dengan zero-copy marshaling.
        /// </summary>
        public static OmniResult<IntPtr> Execute(string functionName, byte[] data)
        {
            if (data == null || data.Length == 0)
                return OmniResult<IntPtr>.Err("E301", "Data tidak boleh null/kosong");

            // Pin managed array → unmanaged pointer (zero-copy GC pinning)
            GCHandle handle = GCHandle.Alloc(data, GCHandleType.Pinned);
            try
            {
                IntPtr pinnedPtr = handle.AddrOfPinnedObject();
                IntPtr resultPtr = OmniFfi(pinnedPtr, (UIntPtr)data.Length);

                if (resultPtr == IntPtr.Zero)
                    return OmniResult<IntPtr>.Err("E302", "Kernel mengembalikan null");

                return OmniResult<IntPtr>.Ok(resultPtr);
            }
            finally
            {
                handle.Free();
            }
        }

        /// <summary>
        /// Membaca byte array dari pointer kernel Rust.
        /// </summary>
        public static byte[] ReadOmniBuffer(IntPtr ptr, int length)
        {
            byte[] result = new byte[length];
            Marshal.Copy(ptr, result, 0, length);
            return result;
        }
    }
}
