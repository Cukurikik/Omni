import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neon_glow_075 = () => {
    return {
        id: "omni-anim-neon-glow-075",
        duration: 320,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-23px, 19px, 0)";
            el.style.filter = "contrast(1.694529628045889) hue-rotate(110deg)";
        }
    };
};
