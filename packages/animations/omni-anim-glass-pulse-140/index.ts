import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_glass_pulse_140 = () => {
    return {
        id: "omni-anim-glass-pulse-140",
        duration: 1185,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(6px, -38px, 0)";
            el.style.filter = "contrast(1.6263003391716244) hue-rotate(281deg)";
        }
    };
};
