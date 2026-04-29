using System;

namespace Omni.ToolSurvey
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk { get; set; }
    }

    public class AccessControl
    {
        public OmniResult<bool> CanExecuteTool(string role, string requiredPermission)
        {
            if (string.IsNullOrEmpty(role) || string.IsNullOrEmpty(requiredPermission))
            {
                return new OmniResult<bool> { Error = "Role/Permission cannot be empty", IsOk = false };
            }
            
            // C# business rules for verifying if an LLM agent has permissions to use a tool
            bool hasAccess = role == "admin" || requiredPermission == "public";
            
            return new OmniResult<bool> { Value = hasAccess, IsOk = true };
        }
    }
}
