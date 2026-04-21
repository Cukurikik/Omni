// ===========================================================================
// OMNI DOMAIN LAYER — ORDER AGGREGATE (DDD)
// ===========================================================================
// Domain Layer   : Domain (DDD aggregate, CQRS pattern)
// Language        : C#
// Function        : Complete Domain-Driven Design Order Aggregate with value
//                   objects, business rules, state machine transitions,
//                   domain events, and invariant enforcement
// ===========================================================================

using System;
using System.Collections.Generic;
using System.Linq;

namespace OmniDomain.Orders
{
    // ---- Value Objects --------------------------------------------------------

    public record Money(decimal Amount, string Currency)
    {
        public static Money Zero(string currency = "USD") => new(0, currency);

        public static Money operator +(Money a, Money b)
        {
            if (a.Currency != b.Currency)
                throw new InvalidOperationException($"Cannot add {a.Currency} to {b.Currency}");
            return new Money(a.Amount + b.Amount, a.Currency);
        }

        public static Money operator *(Money m, decimal quantity)
            => new(m.Amount * quantity, m.Currency);

        public bool IsPositive => Amount > 0;
        public override string ToString() => $"{Amount:F2} {Currency}";
    }

    public record Address(string Street, string City, string State, string ZipCode, string Country)
    {
        public bool IsValid => !string.IsNullOrWhiteSpace(Street) &&
                               !string.IsNullOrWhiteSpace(City) &&
                               !string.IsNullOrWhiteSpace(Country);
    }

    // ---- Enums ----------------------------------------------------------------

    public enum OrderStatus
    {
        Draft,
        Submitted,
        PaymentPending,
        Paid,
        Processing,
        Shipped,
        Delivered,
        Cancelled,
        Refunded
    }

    // ---- Domain Events --------------------------------------------------------

    public abstract record DomainEvent(Guid OrderId, DateTime OccurredAt);
    public record OrderCreated(Guid OrderId, DateTime OccurredAt, string CustomerId) : DomainEvent(OrderId, OccurredAt);
    public record OrderSubmitted(Guid OrderId, DateTime OccurredAt, Money Total) : DomainEvent(OrderId, OccurredAt);
    public record OrderPaid(Guid OrderId, DateTime OccurredAt, string PaymentRef) : DomainEvent(OrderId, OccurredAt);
    public record OrderShipped(Guid OrderId, DateTime OccurredAt, string TrackingNumber) : DomainEvent(OrderId, OccurredAt);
    public record OrderCancelled(Guid OrderId, DateTime OccurredAt, string Reason) : DomainEvent(OrderId, OccurredAt);
    public record ItemAdded(Guid OrderId, DateTime OccurredAt, string ProductId, int Quantity) : DomainEvent(OrderId, OccurredAt);

    // ---- Order Line Item ------------------------------------------------------

    public class OrderLineItem
    {
        public Guid LineId { get; }
        public string ProductId { get; }
        public string ProductName { get; }
        public int Quantity { get; private set; }
        public Money UnitPrice { get; }
        public Money LineTotal => UnitPrice * Quantity;

        public OrderLineItem(string productId, string productName, int quantity, Money unitPrice)
        {
            if (quantity <= 0) throw new ArgumentException("Quantity must be positive");
            if (!unitPrice.IsPositive) throw new ArgumentException("Unit price must be positive");

            LineId = Guid.NewGuid();
            ProductId = productId;
            ProductName = productName;
            Quantity = quantity;
            UnitPrice = unitPrice;
        }

        public void UpdateQuantity(int newQuantity)
        {
            if (newQuantity <= 0) throw new ArgumentException("Quantity must be positive");
            Quantity = newQuantity;
        }
    }

    // ---- Order Aggregate Root -------------------------------------------------

    public class Order
    {
        // ---- Identity & State
        public Guid Id { get; }
        public string CustomerId { get; }
        public OrderStatus Status { get; private set; }
        public DateTime CreatedAt { get; }
        public DateTime? UpdatedAt { get; private set; }

        // ---- Line Items
        private readonly List<OrderLineItem> _lineItems = new();
        public IReadOnlyList<OrderLineItem> LineItems => _lineItems.AsReadOnly();

        // ---- Shipping
        public Address ShippingAddress { get; private set; }
        public string TrackingNumber { get; private set; }

        // ---- Payment
        public string PaymentReference { get; private set; }

        // ---- Domain Events
        private readonly List<DomainEvent> _domainEvents = new();
        public IReadOnlyList<DomainEvent> DomainEvents => _domainEvents.AsReadOnly();

        // ---- Computed
        public Money Subtotal => _lineItems.Aggregate(
            Money.Zero(), (acc, item) => acc + item.LineTotal);
        public Money Tax => new(Subtotal.Amount * 0.10m, Subtotal.Currency);
        public Money Total => Subtotal + Tax;

        // ---- Constructor (private — use factory)
        private Order(string customerId)
        {
            Id = Guid.NewGuid();
            CustomerId = customerId;
            Status = OrderStatus.Draft;
            CreatedAt = DateTime.UtcNow;

            AddEvent(new OrderCreated(Id, DateTime.UtcNow, customerId));
            Console.WriteLine($"[ORDER-OMNI-CS] Created order {Id} for customer {customerId}");
        }

        // ---- Factory
        public static Order Create(string customerId)
        {
            if (string.IsNullOrWhiteSpace(customerId))
                throw new ArgumentException("Customer ID required");
            return new Order(customerId);
        }

        // ---- Behaviors (enforce invariants) -----------------------------------

        public void AddItem(string productId, string name, int qty, Money price)
        {
            EnsureStatus(OrderStatus.Draft, "Cannot add items to a non-draft order");
            var existing = _lineItems.FirstOrDefault(i => i.ProductId == productId);
            if (existing != null)
            {
                existing.UpdateQuantity(existing.Quantity + qty);
            }
            else
            {
                _lineItems.Add(new OrderLineItem(productId, name, qty, price));
            }
            Touch();
            AddEvent(new ItemAdded(Id, DateTime.UtcNow, productId, qty));
        }

        public void RemoveItem(string productId)
        {
            EnsureStatus(OrderStatus.Draft, "Cannot remove items from a non-draft order");
            _lineItems.RemoveAll(i => i.ProductId == productId);
            Touch();
        }

        public void SetShippingAddress(Address address)
        {
            if (!address.IsValid) throw new ArgumentException("Invalid shipping address");
            ShippingAddress = address;
            Touch();
        }

        public void Submit()
        {
            EnsureStatus(OrderStatus.Draft, "Only draft orders can be submitted");
            if (_lineItems.Count == 0) throw new InvalidOperationException("Cannot submit empty order");
            if (ShippingAddress == null) throw new InvalidOperationException("Shipping address required");

            Status = OrderStatus.Submitted;
            Touch();
            AddEvent(new OrderSubmitted(Id, DateTime.UtcNow, Total));
        }

        public void MarkPaid(string paymentRef)
        {
            EnsureStatus(OrderStatus.Submitted, "Order must be submitted before payment");
            PaymentReference = paymentRef;
            Status = OrderStatus.Paid;
            Touch();
            AddEvent(new OrderPaid(Id, DateTime.UtcNow, paymentRef));
        }

        public void Ship(string trackingNumber)
        {
            EnsureStatus(OrderStatus.Paid, "Order must be paid before shipping");
            TrackingNumber = trackingNumber;
            Status = OrderStatus.Shipped;
            Touch();
            AddEvent(new OrderShipped(Id, DateTime.UtcNow, trackingNumber));
        }

        public void Cancel(string reason)
        {
            if (Status == OrderStatus.Shipped || Status == OrderStatus.Delivered)
                throw new InvalidOperationException("Cannot cancel shipped/delivered orders");
            Status = OrderStatus.Cancelled;
            Touch();
            AddEvent(new OrderCancelled(Id, DateTime.UtcNow, reason));
        }

        // ---- Helpers ----------------------------------------------------------

        private void EnsureStatus(OrderStatus expected, string message)
        {
            if (Status != expected) throw new InvalidOperationException(message);
        }

        private void Touch() => UpdatedAt = DateTime.UtcNow;
        private void AddEvent(DomainEvent e) => _domainEvents.Add(e);
        public void ClearEvents() => _domainEvents.Clear();
    }
}
