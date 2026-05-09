// OMNI Optimization — Gecode C++ Constraint Model
// Optimizes LLM task allocation across a heterogeneous GPU cluster

#include <gecode/int.hh>
#include <gecode/search.hh>

using namespace Gecode;

class OmniTaskAllocator : public Space {
protected:
    IntVarArray task_to_gpu; // Which GPU executes which task
public:
    OmniTaskAllocator(int num_tasks, int num_gpus) : task_to_gpu(*this, num_tasks, 0, num_gpus - 1) {
        
        // Constraint: Max 3 tasks per GPU to prevent VRAM OOM
        IntArgs gpu_capacities(num_gpus);
        for(int i=0; i<num_gpus; i++) gpu_capacities[i] = 3; 
        
        count(*this, task_to_gpu, gpu_capacities, IRT_LQ);
        
        // Branching strategy: allocate largest tasks first (simulated by variable selection)
        branch(*this, task_to_gpu, INT_VAR_DEGREE_MAX(), INT_VAL_MIN());
    }
    
    // Copy constructor
    OmniTaskAllocator(OmniTaskAllocator& s) : Space(s) {
        task_to_gpu.update(*this, s.task_to_gpu);
    }
    
    virtual Space* copy(void) {
        return new OmniTaskAllocator(*this);
    }
    
    void print() const {
        std::cout << "Task Allocation: " << task_to_gpu << std::endl;
    }
};
