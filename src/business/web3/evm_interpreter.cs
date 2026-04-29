using System;
using System.Collections.Generic;
using System.Numerics;

namespace Omni.Business.Web3
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }

        private Result(bool isSuccess, T value, E error)
        {
            IsSuccess = isSuccess;
            Value = value;
            Error = error;
        }

        public static Result<T, E> Ok(T value) => new Result<T, E>(true, value, default);
        public static Result<T, E> Err(E error) => new Result<T, E>(false, default, error);
    }

    // Highly simplified EVM-like structural interpreter
    public class EVMInterpreter
    {
        private readonly Dictionary<string, BigInteger> _state = new();

        public Result<bool, string> ExecuteTransaction(string sender, string to, BigInteger value, byte[] calldata)
        {
            if (value < 0) return Result<bool, string>.Err("Invalid value");

            if (!_state.ContainsKey(sender)) _state[sender] = 0;
            if (!_state.ContainsKey(to)) _state[to] = 0;

            if (_state[sender] < value)
            {
                return Result<bool, string>.Err("Insufficient balance");
            }

            // Transfer value
            _state[sender] -= value;
            _state[to] += value;

            // Simple contract execution simulation based on calldata
            if (calldata != null && calldata.Length > 0)
            {
                // Simulate OP_ADD
                if (calldata[0] == 0x01 && calldata.Length >= 3)
                {
                    BigInteger a = calldata[1];
                    BigInteger b = calldata[2];
                    BigInteger res = a + b;
                    // In real EVM, this goes to stack/memory
                }
            }

            return Result<bool, string>.Ok(true);
        }

        public BigInteger GetBalance(string address)
        {
            return _state.TryGetValue(address, out var bal) ? bal : 0;
        }
        
        public void Mint(string address, BigInteger amount)
        {
             if (!_state.ContainsKey(address)) _state[address] = 0;
             _state[address] += amount;
        }
    }
}
