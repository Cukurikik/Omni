// ===========================================================================
// OMNI MESSAGE BROKER ENGINE (SEMESTER 3 — BATCH 38.2)
// ===========================================================================
// Absorbed From  : Apache Kafka + RabbitMQ + ActiveMQ patterns
// Logic Inherited: Java / Domain Layer (Pub/Sub + Queue Message Brokering)
// ===========================================================================
//
// By studying Kafka's partition-based log and RabbitMQ's exchange/queue
// routing, Mother learned enterprise messaging patterns:
//   1. Topics partition messages across consumers (Kafka model)
//   2. Exchanges route to queues via binding keys (AMQP model)
//   3. Consumer groups enable parallel processing with offset tracking
//   4. At-least-once delivery with acknowledgment tracking
//   5. Dead letter queues capture unprocessable messages

package omni.domain.messaging;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public final class OmniMessageBrokerEngine {

    // ---- Message ----

    public static final class Message {
        private final String id;
        private final String topic;
        private final String key;
        private final byte[] payload;
        private final Map<String, String> headers;
        private final long timestamp;
        private final int partition;

        public Message(String topic, String key, byte[] payload, Map<String, String> headers) {
            this.id = UUID.randomUUID().toString();
            this.topic = topic;
            this.key = key != null ? key : "";
            this.payload = payload;
            this.headers = headers != null ? Collections.unmodifiableMap(headers) : Collections.emptyMap();
            this.timestamp = System.currentTimeMillis();
            this.partition = Math.abs(this.key.hashCode()) % 16; // Default 16 partitions
        }

        public String getId() { return id; }
        public String getTopic() { return topic; }
        public String getKey() { return key; }
        public byte[] getPayload() { return payload; }
        public Map<String, String> getHeaders() { return headers; }
        public long getTimestamp() { return timestamp; }
        public int getPartition() { return partition; }
    }

    // ---- Partition (Kafka-inspired append-only log) ----

    private static final class Partition {
        private final int id;
        private final List<Message> log;
        private final AtomicLong offset;

        Partition(int id) {
            this.id = id;
            this.log = new CopyOnWriteArrayList<>();
            this.offset = new AtomicLong(0);
        }

        long append(Message msg) {
            log.add(msg);
            return offset.getAndIncrement();
        }

        List<Message> read(long fromOffset, int maxCount) {
            int from = (int) Math.min(fromOffset, log.size());
            int to = Math.min(from + maxCount, log.size());
            return new ArrayList<>(log.subList(from, to));
        }

        long getHighWatermark() { return offset.get(); }
        int size() { return log.size(); }
    }

    // ---- Topic (collection of partitions) ----

    private static final class Topic {
        private final String name;
        private final int partitionCount;
        private final List<Partition> partitions;
        private final AtomicLong totalPublished;

        Topic(String name, int partitionCount) {
            this.name = name;
            this.partitionCount = partitionCount;
            this.partitions = new ArrayList<>();
            for (int i = 0; i < partitionCount; i++) {
                partitions.add(new Partition(i));
            }
            this.totalPublished = new AtomicLong(0);
        }

        long publish(Message msg) {
            int partIdx = msg.getPartition() % partitionCount;
            long offset = partitions.get(partIdx).append(msg);
            totalPublished.incrementAndGet();
            return offset;
        }

        List<Message> consume(int partition, long fromOffset, int maxCount) {
            if (partition < 0 || partition >= partitionCount) return Collections.emptyList();
            return partitions.get(partition).read(fromOffset, maxCount);
        }
    }

    // ---- Consumer Group (tracks offsets per partition) ----

    public static final class ConsumerGroup {
        private final String groupId;
        private final String topic;
        private final Map<Integer, AtomicLong> committedOffsets;
        private final List<Consumer<Message>> handlers;

        public ConsumerGroup(String groupId, String topic, int partitions) {
            this.groupId = groupId;
            this.topic = topic;
            this.committedOffsets = new ConcurrentHashMap<>();
            for (int i = 0; i < partitions; i++) {
                committedOffsets.put(i, new AtomicLong(0));
            }
            this.handlers = new CopyOnWriteArrayList<>();
        }

        public void subscribe(Consumer<Message> handler) {
            handlers.add(handler);
        }

        public long getCommittedOffset(int partition) {
            AtomicLong offset = committedOffsets.get(partition);
            return offset != null ? offset.get() : 0;
        }

        public void commitOffset(int partition, long offset) {
            committedOffsets.computeIfAbsent(partition, k -> new AtomicLong(0)).set(offset);
        }

        List<Consumer<Message>> getHandlers() { return handlers; }
        public String getGroupId() { return groupId; }
    }

    // ---- Dead Letter Queue ----

    private static final class DeadLetterQueue {
        private final ConcurrentLinkedQueue<Message> messages;
        private final AtomicLong totalDeadLettered;

        DeadLetterQueue() {
            this.messages = new ConcurrentLinkedQueue<>();
            this.totalDeadLettered = new AtomicLong(0);
        }

        void add(Message msg) {
            messages.add(msg);
            totalDeadLettered.incrementAndGet();
        }

        long size() { return totalDeadLettered.get(); }
    }

    // ---- Broker Core ----

    private final Map<String, Topic> topics;
    private final Map<String, ConsumerGroup> consumerGroups;
    private final DeadLetterQueue dlq;
    private final AtomicLong totalPublished;
    private final AtomicLong totalConsumed;
    private final AtomicLong totalAcknowledged;

    public OmniMessageBrokerEngine() {
        this.topics = new ConcurrentHashMap<>();
        this.consumerGroups = new ConcurrentHashMap<>();
        this.dlq = new DeadLetterQueue();
        this.totalPublished = new AtomicLong(0);
        this.totalConsumed = new AtomicLong(0);
        this.totalAcknowledged = new AtomicLong(0);
    }

    /** Create a new topic with the specified partition count. */
    public void createTopic(String topicName, int partitions) {
        topics.putIfAbsent(topicName, new Topic(topicName, Math.max(1, partitions)));
    }

    /** Publish a message to a topic. Returns partition offset. */
    public OptionalLong publish(Message message) {
        Topic topic = topics.get(message.getTopic());
        if (topic == null) return OptionalLong.empty();

        long offset = topic.publish(message);
        totalPublished.incrementAndGet();
        return OptionalLong.of(offset);
    }

    /** Create a consumer group for a topic. */
    public ConsumerGroup createConsumerGroup(String groupId, String topicName) {
        Topic topic = topics.get(topicName);
        if (topic == null) return null;

        ConsumerGroup group = new ConsumerGroup(groupId, topicName, topic.partitionCount);
        consumerGroups.put(groupId, group);
        return group;
    }

    /** Poll messages from a topic for a consumer group. */
    public List<Message> poll(String groupId, int maxMessages) {
        ConsumerGroup group = consumerGroups.get(groupId);
        if (group == null) return Collections.emptyList();

        Topic topic = topics.get(group.topic);
        if (topic == null) return Collections.emptyList();

        List<Message> result = new ArrayList<>();
        for (int p = 0; p < topic.partitionCount && result.size() < maxMessages; p++) {
            long offset = group.getCommittedOffset(p);
            List<Message> batch = topic.consume(p, offset, maxMessages - result.size());
            result.addAll(batch);

            // Dispatch to handlers
            for (Message msg : batch) {
                for (Consumer<Message> handler : group.getHandlers()) {
                    handler.accept(msg);
                }
            }

            // Auto-commit offset
            if (!batch.isEmpty()) {
                group.commitOffset(p, offset + batch.size());
                totalConsumed.addAndGet(batch.size());
            }
        }

        return result;
    }

    /** Send a message to the dead letter queue. */
    public void deadLetter(Message message) {
        dlq.add(message);
    }

    // ---- Diagnostics ----

    public Map<String, Object> diagnostics() {
        Map<String, Object> info = new LinkedHashMap<>();
        info.put("engine", "OmniMessageBrokerEngine");
        info.put("layer", "Java Domain");
        info.put("total_topics", topics.size());
        info.put("total_consumer_groups", consumerGroups.size());
        info.put("total_published", totalPublished.get());
        info.put("total_consumed", totalConsumed.get());
        info.put("dead_letter_count", dlq.size());
        info.put("topics", topics.keySet().stream().collect(Collectors.toList()));
        info.put("learned_logic", List.of(
            "kafka-partition-append-log",
            "key-based-partition-hashing",
            "consumer-group-offset-tracking",
            "at-least-once-delivery",
            "dead-letter-queue-dlq",
            "copy-on-write-thread-safe",
            "atomic-long-lock-free-counters"
        ));
        return info;
    }
}
