// @omni-layer Game | @omni-lang Unity C# | @omni-batch 17
// @omni-description Neural environment simulator: Unity MonoBehaviour for
// 3D RL training environment with physics-based rewards and agent control.

using UnityEngine;
using System.Collections.Generic;
using System;

namespace Omni.Game.RL
{
    [Serializable]
    public struct EnvironmentState
    {
        public float[] Observation;
        public float Reward;
        public bool Done;
        public int StepCount;
        public float TotalReward;
    }

    public class OmniRLEnvironment : MonoBehaviour
    {
        [Header("Environment Config")]
        [SerializeField] private int observationSize = 24;
        [SerializeField] private int actionSize = 4;
        [SerializeField] private int maxSteps = 1000;
        [SerializeField] private float rewardScale = 1.0f;

        [Header("Agent")]
        [SerializeField] private Transform agentTransform;
        [SerializeField] private Transform goalTransform;
        [SerializeField] private Rigidbody agentRigidbody;

        [Header("Stats")]
        [SerializeField] private int episodeCount;
        [SerializeField] private float bestReward = float.MinValue;

        private float[] currentObservation;
        private int stepCount;
        private float episodeReward;
        private bool isDone;

        public event Action<EnvironmentState> OnStepCompleted;
        public event Action<float, int> OnEpisodeEnded;

        private void Awake()
        {
            currentObservation = new float[observationSize];
        }

        public float[] Reset()
        {
            stepCount = 0;
            episodeReward = 0f;
            isDone = false;
            episodeCount++;

            // Randomize agent position
            if (agentTransform != null)
            {
                agentTransform.localPosition = new Vector3(
                    UnityEngine.Random.Range(-4f, 4f), 0.5f,
                    UnityEngine.Random.Range(-4f, 4f));
            }

            // Randomize goal position
            if (goalTransform != null)
            {
                goalTransform.localPosition = new Vector3(
                    UnityEngine.Random.Range(-4f, 4f), 0.5f,
                    UnityEngine.Random.Range(-4f, 4f));
            }

            if (agentRigidbody != null)
            {
                agentRigidbody.velocity = Vector3.zero;
                agentRigidbody.angularVelocity = Vector3.zero;
            }

            return CollectObservation();
        }

        public EnvironmentState Step(float[] action)
        {
            if (isDone) return new EnvironmentState { Done = true };

            stepCount++;
            ApplyAction(action);
            float[] obs = CollectObservation();
            float reward = ComputeReward();
            bool done = CheckTermination();

            episodeReward += reward;
            isDone = done;

            var state = new EnvironmentState
            {
                Observation = obs,
                Reward = reward * rewardScale,
                Done = done,
                StepCount = stepCount,
                TotalReward = episodeReward
            };

            OnStepCompleted?.Invoke(state);

            if (done)
            {
                if (episodeReward > bestReward) bestReward = episodeReward;
                OnEpisodeEnded?.Invoke(episodeReward, stepCount);
            }

            return state;
        }

        private void ApplyAction(float[] action)
        {
            if (agentRigidbody == null || action == null || action.Length < 2) return;
            float moveX = Mathf.Clamp(action[0], -1f, 1f) * 5f;
            float moveZ = Mathf.Clamp(action[1], -1f, 1f) * 5f;
            agentRigidbody.AddForce(new Vector3(moveX, 0, moveZ), ForceMode.VelocityChange);
        }

        private float[] CollectObservation()
        {
            if (agentTransform == null) return currentObservation;
            Vector3 agentPos = agentTransform.localPosition;
            Vector3 goalPos = goalTransform != null ? goalTransform.localPosition : Vector3.zero;
            Vector3 velocity = agentRigidbody != null ? agentRigidbody.velocity : Vector3.zero;
            Vector3 toGoal = goalPos - agentPos;

            currentObservation[0] = agentPos.x; currentObservation[1] = agentPos.y; currentObservation[2] = agentPos.z;
            currentObservation[3] = velocity.x; currentObservation[4] = velocity.y; currentObservation[5] = velocity.z;
            currentObservation[6] = toGoal.x; currentObservation[7] = toGoal.y; currentObservation[8] = toGoal.z;
            currentObservation[9] = toGoal.magnitude;
            currentObservation[10] = velocity.magnitude;
            currentObservation[11] = (float)stepCount / maxSteps;

            return currentObservation;
        }

        private float ComputeReward()
        {
            if (agentTransform == null || goalTransform == null) return -0.01f;
            float dist = Vector3.Distance(agentTransform.localPosition, goalTransform.localPosition);
            float goalReward = dist < 0.5f ? 10f : 0f;
            float shaping = -dist * 0.01f;
            float stepPenalty = -0.001f;
            return goalReward + shaping + stepPenalty;
        }

        private bool CheckTermination()
        {
            if (stepCount >= maxSteps) return true;
            if (agentTransform != null && goalTransform != null)
            {
                if (Vector3.Distance(agentTransform.localPosition, goalTransform.localPosition) < 0.5f) return true;
            }
            if (agentTransform != null && agentTransform.localPosition.y < -1f) return true;
            return false;
        }

        public Dictionary<string, object> GetStats() => new()
        {
            ["episodes"] = episodeCount,
            ["current_step"] = stepCount,
            ["episode_reward"] = episodeReward,
            ["best_reward"] = bestReward,
            ["is_done"] = isDone
        };
    }
}
