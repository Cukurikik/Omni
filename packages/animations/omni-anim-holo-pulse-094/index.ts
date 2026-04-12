import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_holo_pulse_094 = () => {
    return {
        id: "omni-anim-holo-pulse-094",
        duration: 595,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(13px, 24px, 0)";
            el.style.filter = "contrast(1.6409649757679048) hue-rotate(44deg)";
        }
    };
};
