package omni.business.llmpowerhouse;

public class OmniResult<T> {
    public final T value;
    public final String error;
    public final boolean isOk;

    public OmniResult(T value, String error) {
        this.value = value;
        this.error = error;
        this.isOk = (error == null);
    }
}

public class BillingService {
    public OmniResult<Double> calculateTokenCost(int tokensProcessed) {
        if (tokensProcessed < 0) {
            return new OmniResult<>(null, "Negative token count");
        }
        
        // $0.002 per 1k tokens simulation
        double cost = (tokensProcessed / 1000.0) * 0.002;
        return new OmniResult<>(cost, null);
    }
}
