using System;

namespace Omni.Domain.Predict
{
    public class HoiForecastContext
    {
        public bool IsValid { get; private set; }

        public HoiForecastContext()
        {
            IsValid = true;
        }
    }
}
