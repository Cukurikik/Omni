import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_gravity_glow_080 = () => {
    return {
        id: "omni-anim-gravity-glow-080",
        duration: 1062,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(3px, -6px, 0)";
            el.style.filter = "contrast(1.1895173782506345) hue-rotate(301deg)";
        }
    };
};
