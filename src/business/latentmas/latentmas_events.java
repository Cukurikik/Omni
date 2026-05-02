package omni.business.latentmas;
// @omni-domain Business Layer (LatentMAS Events)
public class LatentMASEvent { public final String type; public final String agentId; public final long timestamp; public final Object payload;
    public LatentMASEvent(String type, String agentId, Object payload) { this.type=type; this.agentId=agentId; this.timestamp=System.currentTimeMillis(); this.payload=payload; }
}
public class LatentMASEventBus {
    private final java.util.List<LatentMASEvent> events = new java.util.ArrayList<>();
    public void publish(LatentMASEvent event) { if (event!=null) events.add(event); }
    public java.util.List<LatentMASEvent> getByAgent(String agentId) { return events.stream().filter(e->e.agentId.equals(agentId)).collect(java.util.stream.Collectors.toList()); }
    public java.util.List<LatentMASEvent> getByType(String type) { return events.stream().filter(e->e.type.equals(type)).collect(java.util.stream.Collectors.toList()); }
}
