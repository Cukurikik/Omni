using System;
using System.Collections.Generic;

namespace Omni.Business.Quantum
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

    public enum GateType { H, X, Y, Z, CNOT, RX, RY, RZ }

    public class QuantumGate
    {
        public GateType Type { get; set; }
        public int Target { get; set; }
        public int Control { get; set; } = -1;
        public double Phase { get; set; } = 0.0;
    }

    public class CircuitOptimizer
    {
        public Result<List<QuantumGate>, string> OptimizeCircuit(List<QuantumGate> circuit)
        {
            if (circuit == null || circuit.Count == 0)
                return Result<List<QuantumGate>, string>.Failure("EmptyCircuit");

            var optimized = new List<QuantumGate>();
            
            // Pass 1: Cancellation of adjacent hermitian gates (H-H, X-X, etc on same target)
            for (int i = 0; i < circuit.Count; i++)
            {
                if (optimized.Count > 0)
                {
                    var last = optimized[optimized.Count - 1];
                    var current = circuit[i];
                    
                    if (last.Type == current.Type && last.Target == current.Target && last.Control == current.Control)
                    {
                        if (last.Type == GateType.H || last.Type == GateType.X || last.Type == GateType.Y || last.Type == GateType.Z || last.Type == GateType.CNOT)
                        {
                            optimized.RemoveAt(optimized.Count - 1); // Cancel out
                            continue;
                        }
                    }
                }
                optimized.Add(circuit[i]);
            }

            // Pass 2: Parameterized gate fusion (RX-RX)
            var finalCircuit = new List<QuantumGate>();
            for (int i = 0; i < optimized.Count; i++)
            {
                if (finalCircuit.Count > 0)
                {
                    var last = finalCircuit[finalCircuit.Count - 1];
                    var current = optimized[i];

                    if (last.Type == current.Type && last.Target == current.Target && 
                        (last.Type == GateType.RX || last.Type == GateType.RY || last.Type == GateType.RZ))
                    {
                        last.Phase += current.Phase;
                        if (Math.Abs(last.Phase % (2 * Math.PI)) < 1e-9)
                        {
                            finalCircuit.RemoveAt(finalCircuit.Count - 1);
                        }
                        continue;
                    }
                }
                finalCircuit.Add(optimized[i]);
            }

            return Result<List<QuantumGate>, string>.Success(finalCircuit);
        }
    }
}
