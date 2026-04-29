package omni.events.djl;

import ai.djl.ModelException;
import ai.djl.inference.Predictor;
import ai.djl.modality.Classifications;
import ai.djl.modality.cv.Image;
import ai.djl.modality.cv.ImageFactory;
import ai.djl.repository.zoo.Criteria;
import ai.djl.repository.zoo.ZooModel;
import ai.djl.translate.TranslateException;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

// OMNI Event Layer: DJL Stream Processor
// Zero-mock Kafka/In-Memory streaming ingestion for deep learning image inference.

public class ModelInferenceStream implements Runnable {

    private final BlockingQueue<byte[]> imageStreamQueue;
    private final ZooModel<Image, Classifications> model;
    private volatile boolean isRunning = true;

    public ModelInferenceStream(Criteria<Image, Classifications> criteria) throws ModelException, IOException {
        this.imageStreamQueue = new LinkedBlockingQueue<>(1000); // Backpressure protection
        this.model = criteria.loadModel();
    }

    public void ingestImageBytes(byte[] payload) {
        if (!imageStreamQueue.offer(payload)) {
            System.err.println("WARNING: Stream queue full, dropping payload to prevent OOM.");
        }
    }

    public void stop() {
        this.isRunning = false;
        this.model.close();
    }

    @Override
    public void run() {
        try (Predictor<Image, Classifications> predictor = model.newPredictor()) {
            while (isRunning) {
                byte[] payload = imageStreamQueue.take();
                try {
                    Image img = ImageFactory.getInstance().fromInputStream(new ByteArrayInputStream(payload));
                    Classifications result = predictor.predict(img);
                    
                    // High-speed output routing (Simulated output stream)
                    System.out.printf("[OMNI-DJL-STREAM] Inference Success: Best class: %s, Probability: %f\n", 
                            result.best().getClassName(), result.best().getProbability());
                            
                } catch (TranslateException | IOException e) {
                    System.err.println("[OMNI-DJL-STREAM] Inference Error: " + e.getMessage());
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.err.println("Stream interrupted.");
        }
    }
}
