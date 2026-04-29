using UnityEngine;

namespace Omni.Game.Core
{
    /// <summary>
    /// Omni Unity C# Spatial Anchor Component.
    /// Strictly typed logic for AR/VR anchoring.
    /// </summary>
    public class OmniSpatialAnchor : MonoBehaviour
    {
        private bool _isAnchored = false;
        private Vector3 _anchorPosition;

        public bool TryAnchor(Vector3 targetPosition)
        {
            if (_isAnchored)
            {
                return false; // Already anchored, deterministic failure
            }

            _anchorPosition = targetPosition;
            transform.position = _anchorPosition;
            _isAnchored = true;

            return true; // Monadic-style boolean success indicator
        }
    }
}
