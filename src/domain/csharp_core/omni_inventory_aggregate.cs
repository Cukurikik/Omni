// OMNI Domain Layer: C# Inventory Aggregate
namespace OmniFramework.Domain {
    public class OmniInventoryAggregate {
        public int Stock { get; private set; }
        public void Deduct(int amount) => Stock -= amount;
    }
}
