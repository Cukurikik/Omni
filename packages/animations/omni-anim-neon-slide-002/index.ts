import { OmniWebMotionEngine } from '@omni-bridge/ui/motion';

export const omni_anim_neon_slide_002 = () => {
    return {
        id: "omni-anim-neon-slide-002",
        duration: 1375,
        easing: "omni-cyberpunk-glitch",
        execute: (el: HTMLElement) => {
            el.style.transform = "translate3d(25px, -37px, 0)";
            el.style.filter = "contrast(2.4488825110199417) hue-rotate(204deg)";
        }
    };
};
