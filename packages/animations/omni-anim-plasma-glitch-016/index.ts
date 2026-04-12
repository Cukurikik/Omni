import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_plasma_glitch_016 = () => {
    return {
        id: "omni-anim-plasma-glitch-016",
        duration: 205,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(1px, -50px, 0)";
            el.style.filter = "contrast(1.7610917779338313) hue-rotate(5deg)";
        }
    };
};
