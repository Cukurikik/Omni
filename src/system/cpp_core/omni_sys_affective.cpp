#include <cmath>
extern "C" {
    float omni_sys_affective_arousal(float gsr, float hr, float baseline_gsr, float baseline_hr) {
        float delta_gsr = (gsr - baseline_gsr) / (baseline_gsr > 0 ? baseline_gsr : 1.0f);
        float delta_hr = (hr - baseline_hr) / (baseline_hr > 0 ? baseline_hr : 1.0f);
        return (delta_gsr + delta_hr) * 0.5f;
    }
}
