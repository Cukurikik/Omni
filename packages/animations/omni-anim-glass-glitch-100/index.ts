import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_glass_glitch_100 = () => {
    return {
        id: "omni-anim-glass-glitch-100",
        duration: 532,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(45px, -36px, 0)";
            el.style.filter = "contrast(2.3706677770443996) hue-rotate(102deg)";
        }
    };
};
