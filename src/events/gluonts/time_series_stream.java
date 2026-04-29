package omni.events.gluonts;

import java.util.Properties;
import java.util.concurrent.LinkedBlockingQueue;
import java.nio.ByteBuffer;

// OMNI Event Layer: GluonTS Live Stream Consumer (Java JNI to Rust/Python)
// High-throughput processor for time series signals without GC pause penalties.

public class TimeSeriesStreamConsumer {
    private final LinkedBlockingQueue<byte[]> ringBuffer;
    private volatile boolean isRunning = true;

    public TimeSeriesStreamConsumer(int bufferCapacity) {
        this.ringBuffer = new LinkedBlockingQueue<>(bufferCapacity);
    }

    // Native bridge to Python GluonTS DeepAR core
    public native void submitToDeepAR(byte[] payload, int length);

    static {
        System.loadLibrary("omni_gluonts_bridge");
    }

    public void startEventLoop() {
        Thread worker = new Thread(() -> {
            while (isRunning) {
                try {
                    byte[] data = ringBuffer.take();
                    // Process binary packet (Zero-copy layout extraction)
                    if (data.length >= 8) { // Minimum size for float64 timestamp/value
                        submitToDeepAR(data, data.length);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }, "Omni-GluonTS-Stream-Worker");
        worker.setPriority(Thread.MAX_PRIORITY);
        worker.start();
    }

    public void ingestPacket(byte[] packet) {
        if (!ringBuffer.offer(packet)) {
            System.err.println("[OMNI WARN] TimeSeries ring buffer full. Dropping packet.");
        }
    }

    public void shutdown() {
        isRunning = false;
    }
}
