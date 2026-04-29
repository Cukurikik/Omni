using System;
using System.Collections.Generic;

namespace OmniFramework.Business.Domain
{
    public class OmniDomainError : Exception
    {
        public OmniDomainError(string message) : base(message) {}
    }

    public class OrderAggregate
    {
        public Guid Id { get; private set; }
        public decimal TotalAmount { get; private set; }
        public string Status { get; private set; }

        public OrderAggregate(Guid id)
        {
            Id = id;
            TotalAmount = 0m;
            Status = "CREATED";
        }

        public void AddItem(decimal price, int quantity)
        {
            if (Status != "CREATED")
                throw new OmniDomainError("Cannot add items to processed order");
                
            if (price < 0 || quantity <= 0)
                throw new OmniDomainError("Invalid item parameters");
                
            TotalAmount += (price * quantity);
        }

        public void FinalizeOrder()
        {
            if (TotalAmount <= 0)
                throw new OmniDomainError("Cannot finalize empty order");
                
            Status = "PENDING_PAYMENT";
        }
    }
}
