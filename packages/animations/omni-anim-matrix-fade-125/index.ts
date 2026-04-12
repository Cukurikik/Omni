import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_matrix_fade_125 = () => {
    return {
        id: "omni-anim-matrix-fade-125",
        duration: 572,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-49px, 1px, 0)";
            el.style.filter = "contrast(1.8368036153777578) hue-rotate(219deg)";
        }
    };
};
