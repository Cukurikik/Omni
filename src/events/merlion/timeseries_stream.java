package omni.events.merlion;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

// OMNI Event Layer: Merlion Time Series Stream
// Java ring-buffer processor for high-frequency ingestion of IoT/Server metrics.

public class TimeSeriesStreamProcessor implements Runnable {

    // Immutable struct for zero-mock metrics
    public static class MetricPayload {
        public final long timestamp;
        public final String metricId;
        public final double value;

        public MetricPayload(long timestamp, String metricId, double value) {
            this.timestamp = timestamp;
            this.metricId = metricId;
            this.value = value;
        }
    }

    private final BlockingQueue<MetricPayload> streamQueue;
    private volatile boolean isRunning = true;
    private long processedCount = 0;

    public TimeSeriesStreamProcessor() {
        // High capacity queue to handle bursty telemetry
        this.streamQueue = new LinkedBlockingQueue<>(50000); 
    }

    public boolean ingestMetric(MetricPayload payload) {
        return streamQueue.offer(payload);
    }

    public long getProcessedCount() {
        return processedCount;
    }

    public void stop() {
        this.isRunning = false;
    }

    @Override
    public void run() {
        System.out.println("[OMNI-MERLION-STREAM] Started Time Series Ingestion Engine.");
        try {
            while (isRunning) {
                MetricPayload payload = streamQueue.take();
                
                // Deterministic batching logic would go here.
                // In OMNI, this data is routed via JNI to the Python Merlion Isolation Forest.
                processedCount++;

                if (processedCount % 10000 == 0) {
                    System.out.printf("[OMNI-MERLION-STREAM] Ingested %d metrics. Latest: %s = %f\n", 
                        processedCount, payload.metricId, payload.value);
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.err.println("[OMNI-MERLION-STREAM] Interrupted.");
        }
    }
}
