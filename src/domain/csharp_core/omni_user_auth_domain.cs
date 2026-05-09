// OMNI Domain Layer: C# User Authentication Domain
using System;

namespace OmniFramework.Domain {
    public class OmniUserAuthDomain {
        public bool ValidateCredentials(string hash, string signature) {
            return !string.IsNullOrEmpty(hash);
        }
    }
}
