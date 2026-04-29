// Omni InstructERC Event Stream (Kafka Java)
// Event Layer: Emotion recognition event processing.
// Ref: LIN-SHANG/InstructERC
package dev.omni.instructerc;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
public class OmniInstructERCStream {
    public static void buildTopology(StreamsBuilder builder) {
        KStream<String, String> emotions = builder.stream("erc-raw-utterances");
        emotions.filter((key, val) -> val != null && val.contains("\"emotion\""))
                .mapValues(v -> v.replace("\"status\":\"pending\"", "\"status\":\"CLASSIFIED\""))
                .to("erc-classified-emotions");
    }
}
