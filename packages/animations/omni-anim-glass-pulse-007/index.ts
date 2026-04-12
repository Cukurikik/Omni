import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_glass_pulse_007 = () => {
    return {
        id: "omni-anim-glass-pulse-007",
        duration: 478,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(21px, -25px, 0)";
            el.style.filter = "contrast(1.7921031741213684) hue-rotate(265deg)";
        }
    };
};
