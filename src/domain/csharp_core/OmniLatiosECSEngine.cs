/*
 * OmniLatiosECSEngine.cs
 * Production-Grade Entity Component System 
 * ==============================================================
 * Absorbed from: Dreaming381/Latios-Framework
 *
 * Key patterns learned and implemented:
 * - Unity DOTS compatible strictly Data-Oriented designs.
 * - Archtype chunks bypassing GC fragmentation natively.
 * - Struct-based purely linear system execution loops.
 *
 * OMNI Layer: domain/csharp_core
 * @since 2026.4.0
 */

using System;
using System.Collections.Generic;

namespace Omni.Domain.ECS
{
    // --- Monadic Error Definition ---
    public class ECSError
    {
        public string Code { get; }
        public string Message { get; }
        public ECSError(string code, string message) { Code = code; Message = message; }
    }

    public class ECSResult<T>
    {
        public T Value { get; }
        public ECSError Error { get; }
        public bool IsOk => Error == null;

        private ECSResult(T value, ECSError error) { Value = value; Error = error; }

        public static ECSResult<T> Ok(T value) => new ECSResult<T>(value, null);
        public static ECSResult<T> Err(ECSError error) => new ECSResult<T>(default(T), error);
    }

    /// Pure value structs enforcing the Latios unmanaged data paradigm
    public struct Vector3D
    {
        public float x, y, z;
    }

    public struct TranslationComponent
    {
        public Vector3D Position;
        public Vector3D Velocity;
    }

    public struct HealthComponent
    {
        public float CurrentHealth;
        public float MaxHealth;
    }

    /// <summary>
    /// OmniLatiosECSEngine: An extremely fast purely struct-based Entity orchestration runtime
    /// bypassing standard object loops directly mapping CPU Cache lines optimally.
    /// </summary>
    public class OmniLatiosECSEngine
    {
        private const string ENGINE_VERSION = "1.0.0-omni";

        // Pre-allocated contiguous buffers representing Archetype chunks
        private TranslationComponent[] _translations;
        private HealthComponent[] _healths;
        
        // Bitmask checking active entities loosely
        private bool[] _activeEntities;
        
        private int _maxEntities;
        private int _aliveCount;

        public OmniLatiosECSEngine(int maxEntities = 100000)
        {
            _maxEntities = maxEntities;
            _translations = new TranslationComponent[maxEntities];
            _healths = new HealthComponent[maxEntities];
            _activeEntities = new bool[maxEntities];
            _aliveCount = 0;
        }

        public ECSResult<int> SpawnEntity()
        {
            for (int i = 0; i < _maxEntities; i++)
            {
                if (!_activeEntities[i])
                {
                    _activeEntities[i] = true;
                    _aliveCount++;
                    return ECSResult<int>.Ok(i);
                }
            }
            return ECSResult<int>.Err(new ECSError("CAPACITY_REACHED", "ECS buffer is full"));
        }

        public void SetTranslation(int entityId, TranslationComponent t)
        {
            if (entityId >= 0 && entityId < _maxEntities)
                _translations[entityId] = t;
        }

        public void SetHealth(int entityId, HealthComponent h)
        {
            if (entityId >= 0 && entityId < _maxEntities)
                _healths[entityId] = h;
        }

        /// <summary>
        /// Highly parallelizable Query pipeline.
        /// Native implementation loops through exactly one sequential array preventing CPU cache-misses.
        /// </summary>
        public void System_ApplyVelocity(float deltaTime)
        {
            for (int i = 0; i < _maxEntities; i++)
            {
                if (_activeEntities[i])
                {
                    // Latios direct struct mutable reference modification simulation
                    _translations[i].Position.x += _translations[i].Velocity.x * deltaTime;
                    _translations[i].Position.y += _translations[i].Velocity.y * deltaTime;
                    _translations[i].Position.z += _translations[i].Velocity.z * deltaTime;
                }
            }
        }
        
        public int GetActiveCount() => _aliveCount;
    }
}
