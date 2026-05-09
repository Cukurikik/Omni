using System;
using System.Collections.Generic;

namespace Omni.Domain.Build
{
    public class OmnifileManifest
    {
        public string ProjectName { get; set; }
        public string Version { get; set; }
        public string TargetArchitecture { get; set; }
        public List<string> PolyglotDependencies { get; set; }

        public OmnifileManifest()
        {
            PolyglotDependencies = new List<string>();
        }

        public bool ValidateForSection16()
        {
            if (string.IsNullOrWhiteSpace(ProjectName)) return false;
            if (string.IsNullOrWhiteSpace(TargetArchitecture)) return false;
            if (PolyglotDependencies == null || PolyglotDependencies.Count == 0) return false;

            return true;
        }

        public string GenerateBuildToken()
        {
            return $"OMNI-BUILD-{ProjectName}-{Version}-{Guid.NewGuid().ToString().Substring(0, 8)}".ToUpper();
        }
    }
}
