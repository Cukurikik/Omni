using System;
using System.Collections.Generic;

namespace Omni.Business.DiffgramStore
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class AnnotationSchema
    {
        public OmniResult<bool> ValidateBoundingBox(double x_min, double y_min, double x_max, double y_max, double image_width, double image_height)
        {
            // Business logic for Diffgram schema validation
            // Coordinates must be positive and within image boundaries
            if (x_min < 0 || y_min < 0 || x_max > image_width || y_max > image_height)
            {
                return new OmniResult<bool>(new ArgumentException("Bounding box coordinates out of image bounds"));
            }

            // Math constraint: min must be strictly less than max
            if (x_min >= x_max || y_min >= y_max)
            {
                return new OmniResult<bool>(new ArgumentException("Invalid box logic: min >= max"));
            }

            // Area must not be degenerate
            double area = (x_max - x_min) * (y_max - y_min);
            if (area < 1.0)
            {
                 return new OmniResult<bool>(new ArgumentException("Degenerate bounding box area"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
