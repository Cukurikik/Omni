// OMNI MOTHER — SEMESTER 14 BATCH 36
// C# — Business Layer (OMNI Zero-Mock Implementation)
// Implements production-grade CQRS Command/Query Segregation Engine.
// Absorbs patterns from: github.com/dotnet-architecture/eShopOnContainers, MediatR

using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Domain.CSharp
{
    // --- Monadic Result ---
    public class DomainResult<T>
    {
        public T Value { get; private set; }
        public string Error { get; private set; }
        public bool IsOk { get; private set; }

        public static DomainResult<T> Ok(T value)
            => new DomainResult<T> { Value = value, IsOk = true, Error = null };

        public static DomainResult<T> Err(string error)
            => new DomainResult<T> { Value = default, IsOk = false, Error = error };
    }

    // --- Domain Events ---
    public class DomainEvent
    {
        public string EventType { get; set; }
        public DateTime Timestamp { get; set; }
        public Dictionary<string, object> Payload { get; set; }
    }

    // --- Aggregate Root (DDD) ---
    public abstract class AggregateRoot
    {
        public Guid Id { get; protected set; }
        public int Version { get; protected set; }
        private readonly List<DomainEvent> _uncommittedEvents = new();

        public IReadOnlyList<DomainEvent> UncommittedEvents => _uncommittedEvents;

        protected void RaiseEvent(string eventType, Dictionary<string, object> payload)
        {
            _uncommittedEvents.Add(new DomainEvent
            {
                EventType = eventType,
                Timestamp = DateTime.UtcNow,
                Payload = payload
            });
            Version++;
        }

        public void ClearEvents() => _uncommittedEvents.Clear();
    }

    // --- Order Aggregate (Example Domain Entity) ---
    public enum OrderStatus
    {
        Draft,
        Submitted,
        Confirmed,
        Shipped,
        Delivered,
        Cancelled
    }

    public class OrderItem
    {
        public string ProductId { get; set; }
        public string ProductName { get; set; }
        public decimal UnitPrice { get; set; }
        public int Quantity { get; set; }
        public decimal Total => UnitPrice * Quantity;
    }

    public class OrderAggregate : AggregateRoot
    {
        public string CustomerId { get; private set; }
        public OrderStatus Status { get; private set; }
        public List<OrderItem> Items { get; private set; } = new();
        public decimal TotalAmount => Items.Sum(i => i.Total);
        public DateTime CreatedAt { get; private set; }

        private OrderAggregate() { }

        public static DomainResult<OrderAggregate> Create(string customerId)
        {
            if (string.IsNullOrWhiteSpace(customerId))
                return DomainResult<OrderAggregate>.Err("Customer ID must be non-empty.");

            var order = new OrderAggregate
            {
                Id = Guid.NewGuid(),
                CustomerId = customerId,
                Status = OrderStatus.Draft,
                CreatedAt = DateTime.UtcNow
            };

            order.RaiseEvent("OrderCreated", new Dictionary<string, object>
            {
                ["customerId"] = customerId,
                ["orderId"] = order.Id.ToString()
            });

            return DomainResult<OrderAggregate>.Ok(order);
        }

        public DomainResult<OrderItem> AddItem(string productId, string name, decimal price, int qty)
        {
            if (Status != OrderStatus.Draft)
                return DomainResult<OrderItem>.Err("Can only add items to Draft orders.");
            if (price <= 0)
                return DomainResult<OrderItem>.Err("Unit price must be > 0.");
            if (qty <= 0)
                return DomainResult<OrderItem>.Err("Quantity must be > 0.");

            var item = new OrderItem
            {
                ProductId = productId,
                ProductName = name,
                UnitPrice = price,
                Quantity = qty
            };

            Items.Add(item);
            RaiseEvent("ItemAdded", new Dictionary<string, object>
            {
                ["productId"] = productId,
                ["quantity"] = qty,
                ["total"] = item.Total
            });

            return DomainResult<OrderItem>.Ok(item);
        }

        public DomainResult<bool> Submit()
        {
            if (Status != OrderStatus.Draft)
                return DomainResult<bool>.Err($"Cannot submit order in {Status} state.");
            if (!Items.Any())
                return DomainResult<bool>.Err("Cannot submit empty order.");

            Status = OrderStatus.Submitted;
            RaiseEvent("OrderSubmitted", new Dictionary<string, object>
            {
                ["totalAmount"] = TotalAmount,
                ["itemCount"] = Items.Count
            });

            return DomainResult<bool>.Ok(true);
        }

        public DomainResult<bool> Confirm()
        {
            if (Status != OrderStatus.Submitted)
                return DomainResult<bool>.Err($"Cannot confirm order in {Status} state.");

            Status = OrderStatus.Confirmed;
            RaiseEvent("OrderConfirmed", new Dictionary<string, object>());
            return DomainResult<bool>.Ok(true);
        }

        public DomainResult<bool> Cancel(string reason)
        {
            if (Status == OrderStatus.Shipped || Status == OrderStatus.Delivered)
                return DomainResult<bool>.Err("Cannot cancel shipped/delivered orders.");

            Status = OrderStatus.Cancelled;
            RaiseEvent("OrderCancelled", new Dictionary<string, object>
            {
                ["reason"] = reason
            });
            return DomainResult<bool>.Ok(true);
        }
    }

    // --- CQRS Command Handler ---
    public class CQRSCommandHandler
    {
        private readonly Dictionary<Guid, OrderAggregate> _store = new();

        public DomainResult<Guid> HandleCreateOrder(string customerId)
        {
            var result = OrderAggregate.Create(customerId);
            if (!result.IsOk) return DomainResult<Guid>.Err(result.Error);

            _store[result.Value.Id] = result.Value;
            return DomainResult<Guid>.Ok(result.Value.Id);
        }

        public DomainResult<bool> HandleAddItem(Guid orderId, string productId, string name, decimal price, int qty)
        {
            if (!_store.ContainsKey(orderId))
                return DomainResult<bool>.Err("Order not found.");

            var order = _store[orderId];
            var result = order.AddItem(productId, name, price, qty);
            return result.IsOk
                ? DomainResult<bool>.Ok(true)
                : DomainResult<bool>.Err(result.Error);
        }

        public DomainResult<bool> HandleSubmitOrder(Guid orderId)
        {
            if (!_store.ContainsKey(orderId))
                return DomainResult<bool>.Err("Order not found.");

            return _store[orderId].Submit();
        }
    }

    // --- CQRS Query Handler ---
    public class CQRSQueryHandler
    {
        private readonly Dictionary<Guid, OrderAggregate> _readStore;

        public CQRSQueryHandler(Dictionary<Guid, OrderAggregate> store)
        {
            _readStore = store;
        }

        public DomainResult<OrderAggregate> GetOrder(Guid orderId)
        {
            return _readStore.ContainsKey(orderId)
                ? DomainResult<OrderAggregate>.Ok(_readStore[orderId])
                : DomainResult<OrderAggregate>.Err("Order not found.");
        }

        public DomainResult<List<OrderAggregate>> GetOrdersByCustomer(string customerId)
        {
            var orders = _readStore.Values
                .Where(o => o.CustomerId == customerId)
                .ToList();
            return DomainResult<List<OrderAggregate>>.Ok(orders);
        }

        public Dictionary<string, object> Diagnostics()
        {
            return new Dictionary<string, object>
            {
                ["engine"] = "OmniCQRSEngine",
                ["layer"] = "domain/csharp",
                ["orderCount"] = _readStore.Count,
                ["status"] = "operational",
                ["learnedFrom"] = "dotnet-architecture/eShopOnContainers"
            };
        }
    }
}
