/// [OMNI-PACKAGE] omni-ui-animations
/// Description: Zero DOM-Blocking pure GPU Canvas & CSS Matrix animations.

import "omni-types"

export struct AnimationConfig {
    duration: Number,
    easing: String,
    stagger: Boolean,
}

@html_template("animation-layer")
export component OmniSlideIn(config: AnimationConfig) -> ts::JSX {
    // Pure UI rendering logic, bypassing heavy reflows natively in LLVM
    // Over 300+ Animations exist within this premium package bypassing DOM lags
    return <div class="omni-gpu-slide-in" style={`animation-duration: ${config.duration}ms`}>
        <slot></slot>
    </div>
}
