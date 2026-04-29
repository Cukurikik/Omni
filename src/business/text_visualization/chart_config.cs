using System;

namespace Omni.Business.TextVisualization
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ChartConfig
    {
        public string Theme { get; set; } = "dark";
        public bool EnableTooltips { get; set; } = true;
        
        public OmniResult<string> ValidateConfig()
        {
            if (Theme != "dark" && Theme != "light")
            {
                return new OmniResult<string>(new ArgumentException("Theme must be 'dark' or 'light'"));
            }
            
            return new OmniResult<string>("CONFIG_VALID");
        }
    }
}
