import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_holo_fade_110 = () => {
    return {
        id: "omni-anim-holo-fade-110",
        duration: 1138,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(11px, -6px, 0)";
            el.style.filter = "contrast(1.4785567011658969) hue-rotate(77deg)";
        }
    };
};
