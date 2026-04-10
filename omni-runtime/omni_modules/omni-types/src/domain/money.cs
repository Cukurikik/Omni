// ============================================================
// 📦 omni-types/domain/money.cs — C# DDD Aggregate for Money
// ============================================================

using System;
using System.Runtime.InteropServices;

namespace Omni.Types.Domain
{
    // Struct to match C layout for FFI
    [StructLayout(LayoutKind.Sequential)]
    public struct FfiResult
    {
        public byte IsError;
        public ulong ErrorCode;
        public double Value;
    }

    public static class MoneyAggregate
    {
        [UnmanagedCallersOnly(EntryPoint = "omni_money_add")]
        public static FfiResult Add(double amountA, string currencyA, double amountB, string currencyB)
        {
            if (currencyA != currencyB)
            {
                // OmniError Code E301
                return new FfiResult { IsError = 1, ErrorCode = 301, Value = 0 };
            }

            // Decimal calculation for financial precision
            decimal a = (decimal)amountA;
            decimal b = (decimal)amountB;
            double result = (double)(a + b);

            return new FfiResult { IsError = 0, ErrorCode = 0, Value = result };
        }

        [UnmanagedCallersOnly(EntryPoint = "omni_money_subtract")]
        public static FfiResult Subtract(double amountA, string currencyA, double amountB, string currencyB)
        {
            if (currencyA != currencyB)
            {
                return new FfiResult { IsError = 1, ErrorCode = 301, Value = 0 };
            }

            decimal a = (decimal)amountA;
            decimal b = (decimal)amountB;
            double result = (double)(a - b);

            return new FfiResult { IsError = 0, ErrorCode = 0, Value = result };
        }
    }
}
