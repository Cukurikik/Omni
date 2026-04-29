using System;

namespace Omni.Business.P2PSwarmCoordinator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ByzantineTolerance
    {
        public OmniResult<bool> IsConsensusValid(int total_nodes, int honest_votes)
        {
            if (total_nodes <= 0 || honest_votes < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Invalid node counts"));
            }

            // P2P Swarm Business Logic: Byzantine Fault Tolerance
            // Ensures decentralized AI consensus cannot be hijacked by malicious or faulty peers
            
            // Standard BFT requires strictly greater than 2/3 of nodes to agree
            double required_threshold = (2.0 / 3.0) * total_nodes;
            
            if (honest_votes > required_threshold)
            {
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
