#include <cmath>
extern "C" {
    float omni_sys_adpapers_citation_impact(int citations, int age_years) {
        if (age_years <= 0) return (float)citations;
        return (float)citations / std::sqrt((float)age_years);
    }
}
