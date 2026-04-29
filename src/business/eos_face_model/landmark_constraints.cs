using System;
using System.Collections.Generic;

namespace Omni.Business.EOSFaceModel
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class LandmarkConstraints
    {
        private readonly int _expectedLandmarks;

        public LandmarkConstraints(int expectedLandmarks = 68) // Standard ibug 68
        {
            _expectedLandmarks = expectedLandmarks;
        }

        public OmniResult<bool> ValidateLandmarks(List<double> landmarks)
        {
            if (landmarks == null || landmarks.Count != _expectedLandmarks * 2)
                return new OmniResult<bool>(new ArgumentException($"Expected {_expectedLandmarks * 2} values (X,Y)"));

            // Deterministic geometric constraint validation
            // e.g., Left eye must be mathematically to the left of the right eye
            
            // Typical 68 point format: 36-41 is left eye, 42-47 is right eye
            // Taking center of left eye (idx 36) and right eye (idx 45)
            double leftEyeX = landmarks[36 * 2];
            double rightEyeX = landmarks[45 * 2];

            if (leftEyeX >= rightEyeX)
            {
                return new OmniResult<bool>(new InvalidOperationException("Anatomical constraint violation: Left eye X >= Right eye X"));
            }

            // Jaw points (0-16) bounding box check
            double minJawY = double.MaxValue;
            for (int i = 0; i <= 16; i++)
            {
                if (landmarks[i * 2 + 1] < minJawY) minJawY = landmarks[i * 2 + 1];
            }

            // Nose tip (30) must be above jaw line geometrically
            double noseTipY = landmarks[30 * 2 + 1];
            
            // In image coordinates, Y increases downwards. So NoseTipY should be < JawY (some point)
            if (noseTipY > landmarks[8 * 2 + 1]) // 8 is chin point
            {
                 return new OmniResult<bool>(new InvalidOperationException("Anatomical constraint violation: Nose tip falls below chin"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
