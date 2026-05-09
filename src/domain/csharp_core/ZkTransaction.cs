using System;

namespace Omni.Domain.Crypto
{
    public class ZkTransaction
    {
        public Guid TxId { get; private set; }
        public string SenderAddress { get; private set; }
        public string ReceiverAddress { get; private set; }
        public decimal Amount { get; private set; }
        public long Nonce { get; private set; }
        public byte[] Signature { get; private set; }

        public ZkTransaction(string sender, string receiver, decimal amount, long nonce, byte[] signature)
        {
            if (string.IsNullOrWhiteSpace(sender) || string.IsNullOrWhiteSpace(receiver))
                throw new ArgumentException("Addresses cannot be null or empty");
            if (amount <= 0)
                throw new ArgumentException("Amount must be greater than zero");

            TxId = Guid.NewGuid();
            SenderAddress = sender;
            ReceiverAddress = receiver;
            Amount = amount;
            Nonce = nonce;
            Signature = signature;
        }

        public byte[] SerializeForProver()
        {
            // OMNI standard domain serialization for Rust Prover layer
            return System.Text.Encoding.UTF8.GetBytes($"{SenderAddress}:{ReceiverAddress}:{Amount}:{Nonce}");
        }
    }
}
