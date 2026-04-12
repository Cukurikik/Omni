import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_plasma_glitch_101 = () => {
    return {
        id: "omni-anim-plasma-glitch-101",
        duration: 1289,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-5px, 48px, 0)";
            el.style.filter = "contrast(1.2314849598020619) hue-rotate(233deg)";
        }
    };
};
