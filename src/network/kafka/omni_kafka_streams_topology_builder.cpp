// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Kafka Streams — Event & Streaming Layer (OMNI Zero-Mock Implementation)
// Implements deterministic Stream Topology Builder with exact DAG construction.
// Absorbs patterns from: github.com/apache/kafka → streams/

#include <vector>
#include <string>
#include <map>

namespace omni {
namespace streaming {
namespace kafka {

template <typename T>
struct Result {
    T value;
    std::string error;
    bool is_ok;
    static Result<T> Ok(T val) { return {val, "", true}; }
    static Result<T> Err(std::string err) { return {T(), err, false}; }
};

enum class ProcessorType {
    SOURCE,
    PROCESSOR,
    SINK
};

struct TopologyNode {
    std::string name;
    ProcessorType type;
    std::string topic;  // For SOURCE/SINK only
    std::vector<std::string> children;
    std::vector<std::string> parents;
};

class StreamTopologyBuilder {
private:
    std::map<std::string, TopologyNode> _nodes;

public:
    /**
     * Adds a Source node to the topology.
     * Source nodes consume from a Kafka topic — they have no parents.
     */
    Result<bool> addSource(const std::string& name, const std::string& topic) {
        if (name.empty() || topic.empty()) {
            return Result<bool>::Err("Kafka Streams: source name and topic must be non-empty.");
        }
        if (_nodes.find(name) != _nodes.end()) {
            return Result<bool>::Err("Kafka Streams: duplicate node name '" + name + "'.");
        }
        TopologyNode node;
        node.name = name;
        node.type = ProcessorType::SOURCE;
        node.topic = topic;
        _nodes[name] = node;
        return Result<bool>::Ok(true);
    }

    /**
     * Adds a Processor node connected to a parent.
     * Processors transform records — they must have at least one parent.
     */
    Result<bool> addProcessor(const std::string& name, const std::string& parentName) {
        if (name.empty() || parentName.empty()) {
            return Result<bool>::Err("Kafka Streams: processor and parent names must be non-empty.");
        }
        if (_nodes.find(parentName) == _nodes.end()) {
            return Result<bool>::Err("Kafka Streams: parent '" + parentName + "' not found in topology.");
        }
        if (_nodes.find(name) != _nodes.end()) {
            return Result<bool>::Err("Kafka Streams: duplicate node name '" + name + "'.");
        }

        TopologyNode node;
        node.name = name;
        node.type = ProcessorType::PROCESSOR;
        node.parents.push_back(parentName);
        _nodes[name] = node;
        _nodes[parentName].children.push_back(name);
        return Result<bool>::Ok(true);
    }

    /**
     * Adds a Sink node connected to a parent.
     * Sink nodes produce to a Kafka topic — they are leaf nodes.
     */
    Result<bool> addSink(const std::string& name, const std::string& topic, const std::string& parentName) {
        if (_nodes.find(parentName) == _nodes.end()) {
            return Result<bool>::Err("Kafka Streams: parent '" + parentName + "' not found.");
        }
        if (_nodes.find(name) != _nodes.end()) {
            return Result<bool>::Err("Kafka Streams: duplicate node name '" + name + "'.");
        }

        TopologyNode node;
        node.name = name;
        node.type = ProcessorType::SINK;
        node.topic = topic;
        node.parents.push_back(parentName);
        _nodes[name] = node;
        _nodes[parentName].children.push_back(name);
        return Result<bool>::Ok(true);
    }

    /**
     * Validates the constructed topology DAG.
     * - Must have at least one source and one sink
     * - No cycles (guaranteed by construction — parents must exist before children)
     * - All processors must be reachable from a source
     */
    Result<bool> validate() const {
        int sources = 0, sinks = 0;
        for (const auto& pair : _nodes) {
            if (pair.second.type == ProcessorType::SOURCE) sources++;
            if (pair.second.type == ProcessorType::SINK) sinks++;
        }
        if (sources == 0) return Result<bool>::Err("Kafka Streams: topology has no source nodes.");
        if (sinks == 0) return Result<bool>::Err("Kafka Streams: topology has no sink nodes.");
        return Result<bool>::Ok(true);
    }

    int nodeCount() const { return _nodes.size(); }
};

} // namespace kafka
} // namespace streaming
} // namespace omni
