import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_glass_pulse_192 = () => {
    return {
        id: "omni-anim-glass-pulse-192",
        duration: 763,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-2px, 28px, 0)";
            el.style.filter = "contrast(1.5391611309150852) hue-rotate(169deg)";
        }
    };
};
