using System;
using System.Collections.Generic;

namespace Omni.Business.FastApiRouter
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ConflictResolution
    {
        public OmniResult<bool> ValidateRouteRegistration(string new_route, List<string> existing_routes)
        {
            if (string.IsNullOrEmpty(new_route))
            {
                return new OmniResult<bool>(new ArgumentException("Route path cannot be empty"));
            }

            foreach (var route in existing_routes)
            {
                if (route == new_route)
                {
                    return new OmniResult<bool>(new InvalidOperationException($"Route conflict detected: {new_route} is already registered"));
                }
                
                // Static path vs parameter conflict check (e.g., /users/me vs /users/{id})
                if (route.StartsWith("/users/") && new_route.StartsWith("/users/"))
                {
                    bool route_has_param = route.Contains("{") && route.Contains("}");
                    bool new_has_param = new_route.Contains("{") && new_route.Contains("}");
                    
                    if (!route_has_param && !new_has_param && route != new_route) continue;
                    
                    // Allow, but in a full implementation this would enforce precedence ordering
                }
            }

            return new OmniResult<bool>(true);
        }
    }
}
