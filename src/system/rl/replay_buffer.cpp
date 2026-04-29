#include <vector>
#include <random>
#include <stdexcept>

// OMNI RL: Experience Replay Buffer
// C++ highly optimized ring buffer for storing and sampling RL transitions.
// Critical for breaking correlation between consecutive samples in DQN.
// Source: rlcode/reinforcement-learning

namespace omni::rl {

struct Transition {
    std::vector<float> state;
    int action;
    float reward;
    std::vector<float> next_state;
    bool done;
};

class ReplayBuffer {
private:
    std::vector<Transition> buffer;
    size_t capacity;
    size_t position;
    size_t current_size;
    std::mt19937 rng;

public:
    ReplayBuffer(size_t capacity) : capacity(capacity), position(0), current_size(0) {
        buffer.resize(capacity);
        rng.seed(std::random_device{}());
    }

    void add(const std::vector<float>& state, int action, float reward, const std::vector<float>& next_state, bool done) {
        buffer[position] = {state, action, reward, next_state, done};
        position = (position + 1) % capacity;
        if (current_size < capacity) {
            current_size++;
        }
    }

    std::vector<Transition> sample(size_t batch_size) {
        if (current_size < batch_size) {
            throw std::runtime_error("Not enough samples in buffer.");
        }

        std::vector<Transition> batch(batch_size);
        std::uniform_int_distribution<size_t> dist(0, current_size - 1);

        for (size_t i = 0; i < batch_size; ++i) {
            batch[i] = buffer[dist(rng)];
        }

        return batch;
    }

    size_t size() const {
        return current_size;
    }
};

} // namespace omni::rl
