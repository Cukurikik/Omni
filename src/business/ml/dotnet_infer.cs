using System;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace Omni.Business.ML
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }
        private Result(bool isSuccess, T value, E error) { IsSuccess = isSuccess; Value = value; Error = error; }
        public static Result<T, E> Success(T value) => new Result<T, E>(true, value, default!);
        public static Result<T, E> Failure(E error) => new Result<T, E>(false, default!, error);
    }

    public class TensorProcessor
    {
        // P/Invoke definition for OMNI C++ System Layer
        [DllImport("omni_tensor_ffi", CallingConvention = CallingConvention.Cdecl)]
        private static extern int process_tensor_f32(IntPtr input, int size, IntPtr output);

        public async Task<Result<float[], string>> ProcessTensorAsync(float[] input)
        {
            if (input == null || input.Length == 0)
                return Result<float[], string>.Failure("Input tensor cannot be null or empty");

            return await Task.Run(() => 
            {
                int size = input.Length;
                float[] output = new float[size];

                GCHandle inputHandle = GCHandle.Alloc(input, GCHandleType.Pinned);
                GCHandle outputHandle = GCHandle.Alloc(output, GCHandleType.Pinned);

                try
                {
                    int res = process_tensor_f32(inputHandle.AddrOfPinnedObject(), size, outputHandle.AddrOfPinnedObject());
                    if (res != 0)
                    {
                        return Result<float[], string>.Failure($"FFI Call failed with code {res}");
                    }
                    return Result<float[], string>.Success(output);
                }
                catch (Exception ex)
                {
                    return Result<float[], string>.Failure($"System Exception: {ex.Message}");
                }
                finally
                {
                    inputHandle.Free();
                    outputHandle.Free();
                }
            });
        }
    }
}
