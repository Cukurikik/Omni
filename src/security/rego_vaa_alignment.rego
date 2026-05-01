package omni.vaa.alignment

default safe = false

# Vulnerability-Aware Alignment logic
safe {
    input.model.forgetting_rate < 0.05
    input.dataset.harmful_ratio == 0.0
}
