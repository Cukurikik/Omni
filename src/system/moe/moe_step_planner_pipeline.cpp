// moe_step_planner_pipeline.cpp — System Layer: MoE Step Planner
// Controls execution step batching to minimize tail latency in TensorRT-LLM.

#include <vector>
#include <chrono>

namespace omni {
namespace system {
namespace planner {

struct StepTask {
    int task_id;
    int estimated_flops;
    long long deadline_ms;
};

class StepPlanner {
private:
    std::vector<StepTask> queue;
    int max_batch_size;

public:
    StepPlanner(int batch_size) : max_batch_size(batch_size) {}

    void enqueue(int id, int flops, long long deadline) {
        queue.push_back({id, flops, deadline});
    }

    std::vector<StepTask> get_next_batch(long long current_time_ms) {
        std::vector<StepTask> batch;
        
        // Priority to tasks nearing deadline
        for (auto it = queue.begin(); it != queue.end(); ) {
            if (it->deadline_ms - current_time_ms < 50) { // critical window
                batch.push_back(*it);
                it = queue.erase(it);
                if (batch.size() >= max_batch_size) break;
            } else {
                ++it;
            }
        }

        // Fill remaining batch with normal tasks
        auto it = queue.begin();
        while (batch.size() < max_batch_size && it != queue.end()) {
            batch.push_back(*it);
            it = queue.erase(it);
        }

        return batch;
    }
};

} // namespace planner
} // namespace system
} // namespace omni
