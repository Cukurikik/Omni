using System;
using System.Threading.Tasks;

namespace Omni.Domain
{
    // OMNI MOTHER: Order Service Application Layer (Production Grade)
    public class OrderService
    {
        private readonly IPaymentRepository _repository;

        public OrderService(IPaymentRepository repository)
        {
            _repository = repository;
        }

        public async Task<Guid> CheckoutAsync(decimal total, string currency)
        {
            var payment = new PaymentAggregate(total, currency);
            
            // Mock transaction scope wrapper
            using (var scope = new TransactionScope())
            {
                payment.Process(MockStripeGateway);
                await _repository.SaveAsync(payment);
                scope.Commit();
            }

            return payment.Id;
        }

        private bool MockStripeGateway(Guid id, decimal amount)
        {
            Console.WriteLine($"[OMNI C#] Processing {amount} for {id}");
            return true; // Simulate success
        }
    }

    public interface IPaymentRepository
    {
        Task SaveAsync(PaymentAggregate payment);
    }
}
