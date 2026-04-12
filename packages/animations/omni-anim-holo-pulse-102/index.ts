import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_holo_pulse_102 = () => {
    return {
        id: "omni-anim-holo-pulse-102",
        duration: 1070,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(17px, -24px, 0)";
            el.style.filter = "contrast(1.9885564041075674) hue-rotate(92deg)";
        }
    };
};
