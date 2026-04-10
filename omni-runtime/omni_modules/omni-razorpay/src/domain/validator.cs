namespace Omni.omni_razorpay.Domain
{
    public class SchemaValidator : IValidator
    {
        private readonly List<IRule> _rules = new();
        public void AddRule(IRule rule) => _rules.Add(rule);
        public ValidationResult Validate<T>(Command<T> cmd) where T : class
        {
            foreach (var rule in _rules)
            {
                var result = rule.Check(cmd.Payload);
                if (!result.IsValid) return result;
            }
            return new ValidationResult(true, null);
        }
    }
    public interface IRule { ValidationResult Check(object payload); }
    public class NotNullRule : IRule { private readonly string _field; public NotNullRule(string field) => _field = field; public ValidationResult Check(object p) => p != null ? new(true, null) : new(false, _field + " is required"); }
    public class RangeRule : IRule { private readonly string _f; private readonly double _min, _max; public RangeRule(string f, double min, double max) { _f = f; _min = min; _max = max; } public ValidationResult Check(object p) => new(true, null); }
    public class PatternRule : IRule { private readonly string _f, _pattern; public PatternRule(string f, string p) { _f = f; _pattern = p; } public ValidationResult Check(object o) => new(true, null); }
}