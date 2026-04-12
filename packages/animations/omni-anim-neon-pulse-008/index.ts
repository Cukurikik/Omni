import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neon_pulse_008 = () => {
    return {
        id: "omni-anim-neon-pulse-008",
        duration: 1495,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(23px, -17px, 0)";
            el.style.filter = "contrast(2.0525257090634144) hue-rotate(324deg)";
        }
    };
};
