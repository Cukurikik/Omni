#include <stdint.h>
#include <stdlib.h>
#include <math.h>

// 3D Environment core derived from DeepMind Lab architecture
typedef struct {
    float x, y, z;
    float yaw, pitch;
} OmniAgentState;

typedef struct {
    int width, height;
    uint8_t* pixel_buffer;
} OmniFrameBuffer;

OmniAgentState* omni_lab_init_agent() {
    OmniAgentState* agent = (OmniAgentState*)malloc(sizeof(OmniAgentState));
    if(agent) {
        agent->x = 0.0f; agent->y = 0.0f; agent->z = 0.0f;
        agent->yaw = 0.0f; agent->pitch = 0.0f;
    }
    return agent;
}

void omni_lab_step(OmniAgentState* agent, float forward, float turn) {
    agent->yaw += turn;
    agent->x += forward * cosf(agent->yaw);
    agent->z += forward * sinf(agent->yaw);
}

void omni_lab_free(OmniAgentState* agent) {
    if(agent) free(agent);
}
