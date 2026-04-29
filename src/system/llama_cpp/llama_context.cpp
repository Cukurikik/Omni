#include "omni/system.h"

class LlamaOmniContext {
public:
    LlamaOmniContext() {}
    omni::Result<bool> init() { return omni::Result<bool>::Ok(true); }
};
