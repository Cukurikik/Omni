#include <vector>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <queue>
#include <iostream>

namespace omni {
namespace system {
namespace moe {

/// OMNI MOTHER Production Zero-Mock CPU Dispatcher
/// Manages a high-priority thread pool for CPU-bound fallback operations
/// like quantization decoding, tokenization, or expert evaluation on constrained nodes.

class CPUDispatcher {
private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    
    std::mutex queue_mutex;
    std::condition_variable condition;
    bool stop;

public:
    explicit CPUDispatcher(size_t threads) : stop(false) {
        for(size_t i = 0; i < threads; ++i) {
            workers.emplace_back([this, i] {
                // Pin thread to core (pseudo-code relying on earlier affinity module)
                // thread::AffinityManager::pin_current_thread_to_core(i);
                
                while(true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(this->queue_mutex);
                        this->condition.wait(lock, [this]{ 
                            return this->stop || !this->tasks.empty(); 
                        });
                        
                        if(this->stop && this->tasks.empty()) {
                            return;
                        }
                        
                        task = std::move(this->tasks.front());
                        this->tasks.pop();
                    }
                    // Execute task
                    try {
                        task();
                    } catch (const std::exception& e) {
                        std::cerr << "OMNI CRITICAL: CPU Dispatcher Task Exception: " << e.what() << "\n";
                    }
                }
            });
        }
    }

    template<class F>
    void enqueue(F&& f) {
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            if(stop) {
                throw std::runtime_error("OMNI CRITICAL: Enqueue on stopped CPU Dispatcher");
            }
            tasks.emplace(std::forward<F>(f));
        }
        condition.notify_one();
    }

    ~CPUDispatcher() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            stop = true;
        }
        condition.notify_all();
        for(std::thread &worker: workers) {
            if(worker.joinable()) {
                worker.join();
            }
        }
    }
    
    size_t pending_tasks() {
        std::unique_lock<std::mutex> lock(queue_mutex);
        return tasks.size();
    }
};

} // namespace moe
} // namespace system
} // namespace omni
