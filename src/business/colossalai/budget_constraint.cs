using System;

namespace Omni.ColossalAI
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk { get; set; }
    }

    public class BudgetConstraint
    {
        public OmniResult<bool> CanAllocate(double currentUsage, double requested, double budget)
        {
            if (budget <= 0)
            {
                return new OmniResult<bool> { Error = "Invalid budget", IsOk = false };
            }
            
            // C# business rules for Colossal-AI memory budgeting
            bool canAllocate = (currentUsage + requested) <= budget;
            
            return new OmniResult<bool> { Value = canAllocate, IsOk = true };
        }
    }
}
