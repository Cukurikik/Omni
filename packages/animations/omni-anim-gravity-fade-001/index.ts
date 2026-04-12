import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_gravity_fade_001 = () => {
    return {
        id: "omni-anim-gravity-fade-001",
        duration: 1025,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(7px, -35px, 0)";
            el.style.filter = "contrast(1.4768825261318128) hue-rotate(62deg)";
        }
    };
};
