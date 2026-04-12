import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_gravity_bounce_070 = () => {
    return {
        id: "omni-anim-gravity-bounce-070",
        duration: 628,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(-12px, 30px, 0)";
            el.style.filter = "contrast(1.220988281704346) hue-rotate(294deg)";
        }
    };
};
