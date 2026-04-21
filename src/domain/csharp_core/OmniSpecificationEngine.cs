// ===========================================================================
// OMNI SPECIFICATION ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : Ardalis.Specification + NSpecifications + DDD patterns
// Logic Inherited: C# / Domain Layer (Specification Pattern & Domain Rules)
// ===========================================================================
//
// By studying Ardalis.Specification and DDD, Mother learned:
//   1. Specification encapsulates a business rule as a reusable predicate
//   2. Composite specifications combine with And/Or/Not operators
//   3. Specifications can be used for querying, validation, or authorization
//   4. Expression-based specs enable database query translation (EF Core)
//   5. Value Objects enforce domain invariants at construction

using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;

namespace Omni.Domain.Specification
{
    // ============================================================
    // PART 1: Specification Pattern
    // ============================================================

    /// <summary>
    /// Base specification class with composable boolean logic.
    /// </summary>
    public abstract class Specification<T>
    {
        private int _totalEvaluations = 0;
        private int _totalSatisfied = 0;

        /// <summary>The core predicate that defines this specification.</summary>
        public abstract Expression<Func<T, bool>> ToExpression();

        /// <summary>Evaluate the specification against a candidate.</summary>
        public bool IsSatisfiedBy(T candidate)
        {
            _totalEvaluations++;
            var predicate = ToExpression().Compile();
            var result = predicate(candidate);
            if (result) _totalSatisfied++;
            return result;
        }

        /// <summary>Filter a collection using this specification.</summary>
        public IEnumerable<T> Filter(IEnumerable<T> candidates)
        {
            var predicate = ToExpression().Compile();
            return candidates.Where(predicate);
        }

        /// <summary>Count matching items.</summary>
        public int Count(IEnumerable<T> candidates)
        {
            return Filter(candidates).Count();
        }

        /// <summary>Get first matching item or default.</summary>
        public T? FirstOrDefault(IEnumerable<T> candidates)
        {
            return Filter(candidates).FirstOrDefault();
        }

        // Composite operators
        public Specification<T> And(Specification<T> other) =>
            new AndSpecification<T>(this, other);

        public Specification<T> Or(Specification<T> other) =>
            new OrSpecification<T>(this, other);

        public Specification<T> Not() =>
            new NotSpecification<T>(this);

        public static Specification<T> operator &(Specification<T> a, Specification<T> b) => a.And(b);
        public static Specification<T> operator |(Specification<T> a, Specification<T> b) => a.Or(b);
        public static Specification<T> operator !(Specification<T> a) => a.Not();
    }

    /// <summary>Lambda-based specification for inline use.</summary>
    public class LambdaSpecification<T> : Specification<T>
    {
        private readonly Expression<Func<T, bool>> _expression;
        private readonly string _description;

        public LambdaSpecification(Expression<Func<T, bool>> expression, string description = "")
        {
            _expression = expression;
            _description = description;
        }

        public override Expression<Func<T, bool>> ToExpression() => _expression;
        public override string ToString() => _description;
    }

    internal class AndSpecification<T> : Specification<T>
    {
        private readonly Specification<T> _left, _right;
        public AndSpecification(Specification<T> left, Specification<T> right) { _left = left; _right = right; }

        public override Expression<Func<T, bool>> ToExpression()
        {
            var leftExpr = _left.ToExpression();
            var rightExpr = _right.ToExpression();
            var param = Expression.Parameter(typeof(T), "x");
            var body = Expression.AndAlso(
                Expression.Invoke(leftExpr, param),
                Expression.Invoke(rightExpr, param));
            return Expression.Lambda<Func<T, bool>>(body, param);
        }
    }

    internal class OrSpecification<T> : Specification<T>
    {
        private readonly Specification<T> _left, _right;
        public OrSpecification(Specification<T> left, Specification<T> right) { _left = left; _right = right; }

        public override Expression<Func<T, bool>> ToExpression()
        {
            var leftExpr = _left.ToExpression();
            var rightExpr = _right.ToExpression();
            var param = Expression.Parameter(typeof(T), "x");
            var body = Expression.OrElse(
                Expression.Invoke(leftExpr, param),
                Expression.Invoke(rightExpr, param));
            return Expression.Lambda<Func<T, bool>>(body, param);
        }
    }

    internal class NotSpecification<T> : Specification<T>
    {
        private readonly Specification<T> _spec;
        public NotSpecification(Specification<T> spec) { _spec = spec; }

        public override Expression<Func<T, bool>> ToExpression()
        {
            var expr = _spec.ToExpression();
            var param = Expression.Parameter(typeof(T), "x");
            var body = Expression.Not(Expression.Invoke(expr, param));
            return Expression.Lambda<Func<T, bool>>(body, param);
        }
    }

    // ============================================================
    // PART 2: Value Objects (DDD)
    // ============================================================

    /// <summary>
    /// Base class for value objects with structural equality.
    /// </summary>
    public abstract class ValueObject : IEquatable<ValueObject>
    {
        /// <summary>Return the components that define equality.</summary>
        protected abstract IEnumerable<object?> GetEqualityComponents();

        public bool Equals(ValueObject? other)
        {
            if (other is null || GetType() != other.GetType()) return false;
            return GetEqualityComponents().SequenceEqual(other.GetEqualityComponents());
        }

        public override bool Equals(object? obj) => Equals(obj as ValueObject);

        public override int GetHashCode()
        {
            return GetEqualityComponents()
                .Aggregate(17, (hash, component) =>
                    hash * 31 + (component?.GetHashCode() ?? 0));
        }

        public static bool operator ==(ValueObject? a, ValueObject? b)
        {
            if (a is null && b is null) return true;
            if (a is null || b is null) return false;
            return a.Equals(b);
        }

        public static bool operator !=(ValueObject? a, ValueObject? b) => !(a == b);
    }

    /// <summary>Money value object (canonical DDD example).</summary>
    public sealed class Money : ValueObject, IComparable<Money>
    {
        public decimal Amount { get; }
        public string Currency { get; }

        public Money(decimal amount, string currency)
        {
            if (string.IsNullOrWhiteSpace(currency))
                throw new ArgumentException("Currency is required");
            if (currency.Length != 3)
                throw new ArgumentException("Currency must be ISO 4217 (3 chars)");

            Amount = Math.Round(amount, 2);
            Currency = currency.ToUpperInvariant();
        }

        public Money Add(Money other)
        {
            EnsureSameCurrency(other);
            return new Money(Amount + other.Amount, Currency);
        }

        public Money Subtract(Money other)
        {
            EnsureSameCurrency(other);
            return new Money(Amount - other.Amount, Currency);
        }

        public Money Multiply(decimal factor) =>
            new Money(Amount * factor, Currency);

        public bool IsNegative => Amount < 0;
        public bool IsZero => Amount == 0;
        public bool IsPositive => Amount > 0;

        public static Money Zero(string currency) => new Money(0, currency);
        public static Money USD(decimal amount) => new Money(amount, "USD");
        public static Money EUR(decimal amount) => new Money(amount, "EUR");

        private void EnsureSameCurrency(Money other)
        {
            if (Currency != other.Currency)
                throw new InvalidOperationException(
                    $"Cannot operate on {Currency} and {other.Currency}");
        }

        protected override IEnumerable<object?> GetEqualityComponents()
        {
            yield return Amount;
            yield return Currency;
        }

        public int CompareTo(Money? other)
        {
            if (other is null) return 1;
            EnsureSameCurrency(other);
            return Amount.CompareTo(other.Amount);
        }

        public override string ToString() => $"{Amount:N2} {Currency}";
    }

    /// <summary>Email value object with format validation.</summary>
    public sealed class Email : ValueObject
    {
        public string Value { get; }

        public Email(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new ArgumentException("Email is required");
            if (!value.Contains('@') || !value.Contains('.'))
                throw new ArgumentException($"Invalid email format: {value}");

            Value = value.Trim().ToLowerInvariant();
        }

        public string Domain => Value.Split('@')[1];
        public string Local => Value.Split('@')[0];

        protected override IEnumerable<object?> GetEqualityComponents()
        {
            yield return Value;
        }

        public override string ToString() => Value;
    }

    // ============================================================
    // PART 3: Domain Rules / Business Rule Validator
    // ============================================================

    public record BusinessRuleViolation(string RuleName, string Message);

    public abstract class BusinessRule
    {
        public abstract string RuleName { get; }
        public abstract string Message { get; }
        public abstract bool IsBroken();

        public BusinessRuleViolation? Validate()
        {
            return IsBroken()
                ? new BusinessRuleViolation(RuleName, Message)
                : null;
        }
    }

    public class BusinessRuleValidator
    {
        private readonly List<BusinessRuleViolation> _violations = new();
        private int _totalChecks = 0;

        public BusinessRuleValidator CheckRule(BusinessRule rule)
        {
            _totalChecks++;
            var violation = rule.Validate();
            if (violation is not null)
                _violations.Add(violation);
            return this;
        }

        public BusinessRuleValidator CheckRule(Func<bool> condition, string ruleName, string message)
        {
            _totalChecks++;
            if (condition())
                _violations.Add(new BusinessRuleViolation(ruleName, message));
            return this;
        }

        public bool IsValid => _violations.Count == 0;
        public IReadOnlyList<BusinessRuleViolation> Violations => _violations.AsReadOnly();

        public void ThrowIfInvalid()
        {
            if (!IsValid)
            {
                var messages = string.Join("; ", _violations.Select(v => $"[{v.RuleName}] {v.Message}"));
                throw new BusinessRuleException(messages, _violations);
            }
        }
    }

    public class BusinessRuleException : Exception
    {
        public IReadOnlyList<BusinessRuleViolation> Violations { get; }

        public BusinessRuleException(string message, IEnumerable<BusinessRuleViolation> violations)
            : base(message)
        {
            Violations = violations.ToList().AsReadOnly();
        }
    }

    // ============================================================
    // Diagnostics
    // ============================================================

    public static class SpecificationDiagnostics
    {
        public static Dictionary<string, object> GetDiagnostics()
        {
            return new Dictionary<string, object>
            {
                ["engine"] = "OmniSpecificationEngine",
                ["layer"] = "C# Domain",
                ["components"] = new[]
                {
                    "Specification<T>", "LambdaSpecification", "AndSpec", "OrSpec", "NotSpec",
                    "ValueObject", "Money", "Email",
                    "BusinessRule", "BusinessRuleValidator"
                },
                ["learned_logic"] = new[]
                {
                    "specification-pattern-predicate",
                    "composite-and-or-not-operators",
                    "expression-tree-ef-translation",
                    "value-object-structural-equality",
                    "money-currency-invariant",
                    "business-rule-validator-chain",
                    "ddd-aggregate-invariant-check",
                    "operator-overloading-spec-combine"
                }
            };
        }
    }
}
