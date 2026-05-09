using System;
using System.Collections.Generic;

namespace Omni.Domain
{
    // OMNI MOTHER: Domain-Driven Design Payment Aggregate (Production Grade)
    public class PaymentAggregate
    {
        public Guid Id { get; private set; }
        public decimal Amount { get; private set; }
        public string Currency { get; private set; }
        public PaymentStatus Status { get; private set; }
        private readonly List<string> _auditTrail;

        public PaymentAggregate(decimal amount, string currency)
        {
            if (amount <= 0) throw new ArgumentException("Amount must be positive.");
            Id = Guid.NewGuid();
            Amount = amount;
            Currency = currency;
            Status = PaymentStatus.Pending;
            _auditTrail = new List<string> { $"Created at {DateTime.UtcNow}" };
        }

        public void Process(Func<Guid, decimal, bool> paymentGateway)
        {
            if (Status != PaymentStatus.Pending) throw new InvalidOperationException("Payment is not pending.");
            
            bool success = paymentGateway(Id, Amount);
            if (success)
            {
                Status = PaymentStatus.Completed;
                _auditTrail.Add($"Completed successfully at {DateTime.UtcNow}");
            }
            else
            {
                Status = PaymentStatus.Failed;
                _auditTrail.Add($"Failed at {DateTime.UtcNow}");
            }
        }

        public IReadOnlyList<string> GetAuditTrail() => _auditTrail.AsReadOnly();
    }

    public enum PaymentStatus { Pending, Completed, Failed }
}
