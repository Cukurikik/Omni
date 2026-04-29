package dev.omni.events.volcano;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class BatchEventStream {
    private BlockingQueue<String> eventQueue = new LinkedBlockingQueue<>();

    public void emitJobStateChange(String jobId, String newState) {
        String eventJson = String.format("{\"job_id\":\"%s\",\"state\":\"%s\",\"ts\":%d}", 
            jobId, newState, System.currentTimeMillis());
        eventQueue.offer(eventJson);
    }

    public void streamToAnalytics() {
        new Thread(() -> {
            try {
                while (true) {
                    String event = eventQueue.take();
                    // Process or forward to Elasticsearch/Prometheus
                    System.out.println("Volcano Event: " + event);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }).start();
    }
}
