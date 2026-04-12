import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_matrix_glow_005 = () => {
    return {
        id: "omni-anim-matrix-glow-005",
        duration: 1400,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(0px, 25px, 0)";
            el.style.filter = "contrast(2.0268679649650654) hue-rotate(181deg)";
        }
    };
};
